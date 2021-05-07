from django.contrib import admin
from .models import *

from django import forms


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = "__all__"

    def clean_start(self):
        if self.instance.id:
            raise forms.ValidationError("Вы не можете изменить дату начала опроса")
        return self.cleaned_data["start"]


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = "__all__"

    def clean_title(self):
        question_id = int(self.data['question'][0])
        question = Question.objects.get(id=question_id)

        if question.q_type == 0:
            raise forms.ValidationError("Неверный тип вопроса")
        return self.cleaned_data["title"]


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    def get_interview_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

    form = InterviewForm


@admin.register(Choice)
class InterviewAdmin(admin.ModelAdmin):
    def get_choice_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
    form = ChoiceForm


admin.site.register(Question)
