import logging

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from qua.api.models import Question, Keyword, Answer
from qua.api import tasks


log = logging.getLogger('qua.' + __name__)


def deserialize(serializer_class, data):

    log.debug('Deserializing %s with %s', data, serializer_class)

    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)

    log.debug('Validated data: %s', serializer.validated_data)

    return serializer

def serialize(serializer_class, instance, data=None, **kwargs):

    log.debug('Serializing %s with %s for %s. Kwargs: %s',
        data, serializer_class, instance, kwargs)

    if data is None:
        serializer = serializer_class(instance, **kwargs)
    else:
        serializer = serializer_class(instance, data=data, **kwargs)
        serializer.is_valid(raise_exception=True)

        log.debug('Validated data: %s', serializer.validated_data)

    return serializer


class AutoUpdatePrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):

    def __init__(self, model, **kwargs):

        self.model = model
        super(AutoUpdatePrimaryKeyRelatedField, self).__init__(**kwargs)

    def get_queryset(self, data):

        try:
            return self.model.get_or_create(data)
        except AttributeError:
            raise AttributeError('Model must have "get_or_create" method')

    def to_internal_value(self, data):

        if self.pk_field is not None:
            data = self.pk_field.to_internal_value(data)

        try:
            return self.get_queryset(data)[0]
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class PrimaryKeyExistsValidator:
    def __init__(self, queryset, message=None):
        self.queryset = queryset
        self.message = message or 'Item with primary key {primary_key} does not exist'

    def __call__(self, value):
        assert ('id' in value and isinstance(value, dict)), 'Value must be a "dict" with "id" element'

        try:
            self.queryset.get(pk=value['id'])
        except ObjectDoesNotExist:
            raise ValidationError(self.message.format(primary_key=value['id']))


class DynamicFieldsModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())

            for field_name in existing - allowed:
                self.fields.pop(field_name)


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
    keywords = AutoUpdatePrimaryKeyRelatedField(model=Keyword, many=True, required=False)
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

        tasks.index_question.delay(question.id)

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
        tasks.index_question.delay(instance.id)

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