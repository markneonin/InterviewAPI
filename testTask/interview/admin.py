from django.urls import reverse
from django.utils.http import urlencode
from django.contrib import admin
from django.utils.html import format_html
from django import forms

from .models import *


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = '__all__'

    def clean_start(self):
        if self.instance.id:
            raise forms.ValidationError('Вы не можете изменить дату начала опроса')
        return self.cleaned_data['start']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = '__all__'

    def clean_title(self):
        question_id = int(self.data['question'][0])
        question = Question.objects.get(id=question_id)

        if question.q_type == 0:
            raise forms.ValidationError('Неверный тип вопроса')
        return self.cleaned_data['title']


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'view_questions_link')

    def view_questions_link(self, obj):
        count = obj.question_set.count()
        url = (
                reverse('admin:interview_question_changelist')
                + '?'
                + urlencode({'interview__id': f"{obj.id}"})
        )
        return format_html('<a href="{}">{} Question</a>', url, count)

    view_questions_link.short_description = 'Вопросы'

    def get_interview_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    form = InterviewForm


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    def get_choice_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    list_display = ('title', 'view_question_link')

    def view_question_link(self, obj):
        url = (
                reverse('admin:interview_question_changelist')
                + '?'
                + urlencode({'choice__id': f'{obj.id}'})
        )
        return format_html('<a href="{}">{}</a>', url, obj.question.title)

    view_question_link.short_description = "Вопрос"
    form = ChoiceForm


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = ('title', 'view_interview_link', 'view_choices_link')

    def view_interview_link(self, obj):
        url = (
                reverse('admin:interview_interview_changelist')
                + '?'
                + urlencode({'question__id': f'{obj.id}'})
        )
        return format_html('<a href="{}">{}</a>', url, obj.interview.title)

    view_interview_link.short_description = 'Интервью'

    def view_choices_link(self, obj):
        count = obj.choice_set.count()
        if count:
            url = (
                    reverse('admin:interview_choice_changelist')
                    + '?'
                    + urlencode({'question__id': f"{obj.id}"})
            )
            return format_html('<a href="{}">{} варианты ответа</a>', url, count)
        else:
            return

    view_choices_link.short_description = 'Варианты ответа'
