from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient


TEST_USERNAME = 'test'
TEST_PASSWORD = 'test'


class BaseQuaTestCase(TestCase):

    def auth(self, username=TEST_USERNAME, password=TEST_PASSWORD):

        return self.client.post('/auth', {
            'username': username,
            'password': password
        })

    def create_authorized_client(
            self, username=TEST_USERNAME, password=TEST_PASSWORD):

        auth = self.auth(username, password).json()
        token = auth['response']['token']

        return APIClient(HTTP_AUTHORIZATION='JWT ' + token)

    def setUp(self):

        User.objects.create_user(
            username=TEST_USERNAME, password=TEST_PASSWORD)
        User.objects.create_user(
            username=TEST_USERNAME + '2', password=TEST_PASSWORD + '2')

        cache.clear()
