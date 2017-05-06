from rest_framework.response import Response


def get_response_dict(ok=1, response=None):

    return {
        'ok': ok,
        'response': response
    }


class QuaApiResponse(Response):

    def __init__(self, data=None, **kwargs):

        super(QuaApiResponse, self).__init__(
            data=get_response_dict(response=data), **kwargs)
