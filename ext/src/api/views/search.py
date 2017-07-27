import logging

from django.conf import settings
from rest_framework import exceptions
from rest_framework.views import APIView

from api import search
from api import serializers
from api.pagination import paginate
from qua.rest.response import QuaApiResponse
from qua.rest.serializers import serialize, deserialize


log = logging.getLogger(settings.APP_NAME + __name__)


class SearchView(APIView):

    @paginate
    def get(self, request, limit=settings.PAGE_SIZE, offset=0):

        req_serializer = deserialize(
            serializers.SearchRequest,
            request.query_params)

        # This is загрушка
        response = {
            'query': req_serializer.data['query'],
            'total': 0,
            'hits': [],
            'query_was_corrected': False,
            'used_query': req_serializer.data['query'],
            'took': 0
        }

        # response = search.search_async(
        #     req_serializer.data['query'],
        #     req_serializer.data['limit'],
        #     req_serializer.data['offset']
        # )

        return QuaApiResponse(response)
