from rest_framework import serializers
from .models import *
from django.core.exceptions import ObjectDoesNotExist
from .utils import *
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ("id", "title", "description")


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    q_type_txt = serializers.CharField(source='get_q_type_display', read_only=True)
    choices = ChoiceSerializer(many=True, default=None)
    answer = serializers.CharField(required=False)

    class Meta:
        model = Question
        fields = ('id',  'q_type', 'q_type_txt', 'title', 'lock_other', 'choices', 'answer')


class DetailInterviewSerializer(serializers.Serializer):
    interview = InterviewSerializer()
    questions = QuestionSerializer(many=True)


class CompleteInterviewSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(allow_null=True, required=False)
    interview_id = serializers.IntegerField(required=True)
    answer = serializers.JSONField()

    def validate_user(self, value):
        try:
            user = User.objects.get(user_id=value)
            return user
        except ObjectDoesNotExist:
            if value:
                user = User(user_id=value)
                user.save()
                return user
            return value

    def validate_interview(self, value):
        try:
            value = Interview.objects.get(id=value, end__gt=now(), start__lte=now())
        except ObjectDoesNotExist:
            raise ValidationError('Этого опроса больше не существует')
        return value

    def validate(self, data):
        interview = data['interview_id']
        txt_answers = data['answer']['txt_answers']
        selection_answers = data['answer']['selection_answers']

        txt_questions = Question.objects.filter(interview__exact=interview).filter(q_type__exact=0).values_list('id')
        selection_questions = []
        for question in Question.objects.filter(interview__exact=interview).filter(q_type__exact=1).all():
            selection_questions.append((question, tuple(Choice.objects.values_list('id').filter(question__exact=question))))

        counter = 0
        for answer in txt_answers:
            if (answer['question'],) in txt_questions:
                counter += 1
            else:
                raise ValidationError(f'Вопрос {answer["question"]} не относиться к данному опросу или не явялется '
                                      f'текстовым')

        if counter != len(txt_questions):
            raise ValidationError(f'Некоррекное количество ответов на текстовые вопросы')

        counter = 0
        for answer in selection_answers:
            for question in selection_questions:
                if answer['question'] == question[0].id and is_valid_selection_answer(answer, question):
                    counter += 1

        if counter != len(selection_questions):
            raise ValidationError('Некорретное количесво валидных ответов на вопросы с выбором')

        return data

    def create(self, validated_data):
        answer = validated_data['answer']
        interview = validated_data['interview']
        try:
            user = validated_data['user']
        except KeyError:
            user = None
        instance = InterviewAnswer(answer=answer,
                                    user=user,
                                    interview=interview)
        instance.save()


class AnswerSerializer(serializers.Serializer):
    interview = InterviewSerializer()
    answers = QuestionSerializer(many=True)
    user_id = serializers.IntegerField()
