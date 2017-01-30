import logging

from django.conf import settings
from django.contrib.auth.models import User

from qua.api.search.engine import get_search_engine
from qua.api.search import utils
from qua.api.search import crawler
from qua.api.models import ExternalResource


log = logging.getLogger('qua.' + __name__)


def _index(
    id, is_external, title, text=None, external=None,
    keywords=None, url=None, external_content=None
):

    engine = get_search_engine()

    spelling = utils.get_spelling_text(title, keywords, text, external, external_content)

    data = {
        'title': title,
        'keywords': keywords,
        'text': text,
        'external': external,
        'external_content': external_content,
        'spelling': spelling,
        'is_external': is_external,
        'url': url
    }

    engine.index(
        index=settings.SEARCH_INDEX_NAME,
        doc_type=settings.SEARCH_INDEX_TYPE,
        id=id,
        body=data
    )


def index_external_resource(url):

    log.debug('Index external resource: %s', url)

    html = crawler.retrieve_page(url)

    if html is None:
        return ''

    god_user = User.objects.get(username='god')
    external_resource = ExternalResource.create(url, god_user)

    title = utils.get_title(html)
    external = utils.get_text_from_html(html)

    _index('e-%s' % external_resource.id, True, title,
        external_content=external,
        url=url
    )

    return external


def index_question(question_id, title, keywords, html):

    log.debug('Indexing question %s', question_id)

    text = utils.get_text_from_html(html)
    external = ''

    for link in utils.extract_all_links(html):
        external += index_external_resource(link)

    _index(
        'q-%s' % question_id, False, title,
        text=text,
        external=external,
        keywords=keywords
    )
