import logging

from django.contrib.auth.models import User
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Question, Keyword, Answer
from qua.rest.serializers import (
    DynamicFieldsModelSerializer,
    AutoUpdatePrimaryKeyRelatedField)


log = logging.getLogger(settings.APP_NAME + __name__)


class UserSerializer(DynamicFieldsModelSerializer):

    class Meta:

        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class AnswerSerializer(DynamicFieldsModelSerializer):

    raw = serializers.CharField(allow_blank=True)
    html = serializers.CharField(required=False)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Answer
        exclude = ('id', 'question')


class QuestionSerializer(DynamicFieldsModelSerializer):

    title = serializers.CharField(max_length=300, required=False)
    keywords = AutoUpdatePrimaryKeyRelatedField(
        model=Keyword,
        many=True,
        required=False)
    answer = AnswerSerializer(required=False)
    answer_exists = serializers.BooleanField(required=False)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    def create(self, validated_data):

        if 'title' not in validated_data:
            raise ValidationError({'title': ['This field is required.']})

        question = Question.create(
            validated_data['title'],
            validated_data['user'],
            keywords=validated_data.get('keywords', None)
        )

        if 'answer' in validated_data and validated_data['answer'] != '':
            Answer.create(
                validated_data['answer']['raw'],
                validated_data['user'],
                question
            )

        # TODO: index question

        return question

    def update(self, instance, validated_data):

        instance.update(
            validated_data['user'],
            title=validated_data.get('title', None),
            keywords=validated_data.get('keywords', None)
        )

        if 'answer' in validated_data:
            if instance.answer_exists:
                if validated_data['answer']['raw'] == '':
                    instance.answer.delete()
                    instance.answer = None
                else:
                    log.debug('Trying to update %s', instance.answer.name)

                    instance.answer.update(
                        validated_data['answer']['raw'],
                        validated_data['user']
                    )
            else:
                log.debug('Creating new answer for %s', instance)

                Answer.create(
                    validated_data['answer']['raw'],
                    validated_data['user'],
                    instance
                )

        instance.save()

        # TODO: reindex question

        return instance

    class Meta:

        model = Question
        exclude = ('deleted',)


class QuestionListSerializer(serializers.Serializer):

    total = serializers.IntegerField()
    items = QuestionSerializer(many=True, fields=(
        'answer_exists', 'title', 'keywords', 'created_at', 'created_by',
        'updated_at', 'updated_by', 'id'
    ))


class UrlParamsSerializer(serializers.Serializer):

    shid = serializers.IntegerField()
    qid = serializers.IntegerField()
    token = serializers.CharField()
    track = serializers.CharField()


class SearchHitSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title = serializers.CharField()
    snippet = serializers.CharField()
    score = serializers.FloatField()
    keywords = serializers.ListField(child=serializers.CharField())
    image = serializers.CharField()
    url_params = UrlParamsSerializer(required=False)
    url = serializers.URLField(required=False)
    is_external = serializers.BooleanField()
    resource = serializers.URLField(allow_null=True)


class SearchSerializer(serializers.Serializer):

    query = serializers.CharField()
    total = serializers.IntegerField()
    hits = SearchHitSerializer(many=True)
    query_was_corrected = serializers.BooleanField()
    used_query = serializers.CharField()
    took = serializers.FloatField()