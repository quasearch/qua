import logging

from django.urls import reverse
from django.conf import settings

from qua.api.models import SearchHistory
from qua.api.search.engine import get_search_engine
from qua import utils
from qua.api.search import utils as search_utils


log = logging.getLogger('qua.' + __name__)


class UrlParams:
    def __init__(self, shid, qid, token):
        self.shid = shid
        self.qid = qid
        self.token = token
        self.track = 'search'


class SearchHit:
    def __init__(self, id, title, search_history_id,
        keywords=None, snippet=None, score=1.0, is_external=False,
        url=None, image=None
    ):
        self.id = id
        self.title = title
        self.snippet = snippet
        self.keywords = keywords
        self.score = score
        self.is_external = is_external
        self.image = image

        if self.is_external:
            self.url = self.get_away_url(url, search_history_id)
        else:
            self.url_params = self.get_url_params(search_history_id)

    def __str__(self):
        return '<SearchHit:{0:.30}|{1}>'.format(self.title, self.score)

    def __repr__(self):
        return self.__str__()

    def get_url_params(self, search_history_id):
        return UrlParams(
            search_history_id, self.id,
            utils.sign('{0}-{1}'.format(search_history_id, self.id))
        )

    def get_away_url(self, url, search_history_id):
        return reverse('away', kwargs={
                'shid': search_history_id,
                'qid': self.id,
                'token': utils.sign('{0}-{1}'.format(search_history_id, self.id)),
                'track': 'search',
                'redirect_url': url
            })


def _get_result_id(engine_hit_id):

    if engine_hit_id.startswith('q-'):
        return int(engine_hit_id[2:])
    else:
        return 0


class SearchResults:
    def __init__(self, query, result=None, search_history_id=None):
        self.query = query
        self.query_was_corrected = False
        self.used_query = self.query

        self.total = 0

        if result is not None:
            self.total = result['hits']['total']

            if result['query_was_corrected']:
                self.query_was_corrected = True
                self.used_query = result['query']

        self.hits = []

        if self.total > 0:
            for hit in result['hits']['hits']:
                self.hits.append(
                    SearchHit(
                        id=_get_result_id(hit['_id']),
                        title=hit['_source']['title'],
                        search_history_id=search_history_id,
                        keywords=hit['_source']['keywords'],
                        snippet=search_utils.generate_snippet(hit['_source']),
                        score=hit['_score'],
                        is_external=hit['_source']['is_external'],
                        url=hit['_source'].get('url', None)
                    )
                )

    def __str__(self):
        return '<SearchResults:{0:.30}|{1}>'.format(self.query, self.total)

    def __repr__(self):
        return self.__str__()


def _create_search_body(queries):

    boolean = []

    if isinstance(queries, str):
        queries = [queries,]

    for item in queries:
        boolean.append({
            'multi_match': {
                'query': item,
                'fields': ['title^2', 'keywords^1.7', 'text^1.3', 'external'],
                'operator': 'and',
                'type': 'cross_fields'
        }})

    body = {
        'query': {
            'bool': {
                'should': boolean
            }
        },
        '_source': ['_id', 'text', 'title', 'keywords', 'is_external', 'external', 'url']
    }

    return body


def _get_results(query, index, size=100):

    engine = get_search_engine()

    body = _create_search_body([query, search_utils.translit(query)])

    result = engine.search(index=index, body=body, size=size)

    return (result['hits']['total'], result['hits'])


def _search(query_stack, index):

    for attempt in range(len(query_stack)):
        query = query_stack.pop()

        found, hits = _get_results(query, index)

        if found:
            return {
                "hits": hits,
                "query": query,
                "query_was_corrected": attempt > 0
            }


def basesearch(query, user):

    log.debug('Search for: %s', query)

    if query == '':
        return SearchResults(query)

    search_stack = []

    """Keyboards inverted query
    """
    keyboard_inverted = search_utils.keyboard_layout_inverse(query)
    is_keyboard_corrected, keyboard_inverted_corrected = search_utils.spelling_correction(
        keyboard_inverted, index=settings.SEARCH_INDEX_NAME
    )

    if is_keyboard_corrected:
        search_stack.append(keyboard_inverted_corrected)

    search_stack.append(keyboard_inverted)

    """Query with typos
    """
    is_query_corrected, query_corrected = search_utils.spelling_correction(
        query, index=settings.SEARCH_INDEX_NAME
    )

    if is_query_corrected:
        search_stack.append(query_corrected)

    """Just user query
    """
    search_stack.append(query)

    result = _search(search_stack, settings.SEARCH_INDEX_NAME)

    if result is None:
        return SearchResults(query)

    if result['query_was_corrected']:
        used_query = result['query']
    else:
        used_query = query

    history_record = SearchHistory.objects.create(
        query=used_query, user=user, results=result['hits']['total'])

    return SearchResults(query, result, history_record.id)
