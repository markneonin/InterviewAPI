from .serializers import *
from .models import *
from .utils import *

from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from random import randint


class InterviewView(viewsets.ViewSet):

    def list(self, request):
        queryset = Interview.objects.all().filter(end__gt=now()).filter(start__lte=now())
        serializer = InterviewSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Interview.objects.all()
        interview = get_object_or_404(queryset, pk=pk, end__gt=now(), start__lte=now())

        questions = Question.objects.all().filter(interview__exact=interview)
        choices = Choice.objects.all().filter(question__interview__exact=interview)

        for question in questions:
            if question.q_type == 1:
                question_choices = []
                for choice in choices:
                    if choice.question == question: question_choices.append(choice)
                question.choices = question_choices

        data = {
            'interview': interview,
            'questions': questions
        }

        serializer = DetailInterviewSerializer(data)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def complete(self, request):
        serializer = CompleteInterviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(validated_data=serializer.validated_data)
            return Response({'message': 'Success'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class Answers(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        interview_answers = InterviewAnswer.objects.filter(user__exact=user).all()

        for interview_answer in interview_answers:
            ans_objs = []
            answer = interview_answer.answer

            for txt in answer['txt_answers']:
                answer_obj = Question.objects.filter().get(pk=txt['question'])

                answer_obj.answer = txt['text']
                ans_objs.append(answer_obj)

            for sel in answer['selection_answers']:
                answer_obj = Question.objects.filter().get(pk=sel['question'])
                choices = Choice.objects.filter(id__in=sel['choices'])
                answer_obj.choices = choices
                ans_objs.append(answer_obj)

            interview_answer.answers = ans_objs

        serializer = AnswerSerializer(interview_answers, many=True)
        return Response(serializer.data)
