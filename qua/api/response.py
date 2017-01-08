from rest_framework.response import Response


class QuaApiResponse(Response):
    def __init__(self, data=None, status=None, template_name=None,
        headers=None, content_type=None
    ):
        custom_data = {
            'ok': 1,
            'response': data
        }

        super(QuaApiResponse, self).__init__(data=custom_data, status=status,
            template_name=template_name, headers=headers,
            content_type=content_type)
