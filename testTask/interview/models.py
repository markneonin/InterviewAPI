from django.db import models
from django.core.exceptions import ValidationError

import django.contrib.postgres.fields as postgr


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)


class Interview(models.Model):
    title = models.CharField(verbose_name='Имя опроса', max_length=256)
    start = models.DateTimeField(verbose_name='Дата старта')
    end = models.DateTimeField(verbose_name='Дата окончания опроса')
    description = models.CharField(verbose_name='Описание опроса', max_length=4096, null=True)

    class Meta:
        verbose_name_plural = "Опрос"

    def __str__(self):
           return self.title


class Question(models.Model):
    title = models.CharField(verbose_name='Вопрос', max_length=4096)
    interview = models.ForeignKey(Interview, verbose_name='Опрос', on_delete=models.CASCADE)
    Q_TYPE_CHOICES = (
        (0, 'Текстовый ответ'),
        (1, 'Выбор варианта/ов')
    )
    q_type = models.IntegerField(verbose_name='Тип вопроса', choices=Q_TYPE_CHOICES)
    lock_other = models.BooleanField(verbose_name='Один вариант ответа', null=True, default=None)

    def __str__(self):
        try:
            qtype = ('Текстовый ответ', 'Выбор варианта/ов')[self.q_type]
        except TypeError:
            qtype = '_'

        return f"{self.title} ({qtype})"

    class Meta:
        verbose_name_plural = "Вопрос"


class Choice(models.Model):
    title = models.CharField(verbose_name='Вариант ответа', max_length=4096)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Вариант ответа"


# class TxtAnswer(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     text = models.CharField(verbose_name='Ответ пользователя', max_length=4096)
#
#     def __str__(self):
#         return self.text
#
#
# class SelectionAnswer(models.Model):
#
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choices = postgr.ArrayField(models.IntegerField(), max_length=15, default=list)


class InterviewAnswer(models.Model):
    """Результаты пройденного опроса хранятся одним куском в JSON поле,
    это позволят сохранить консистентность данных в случае анонимных
    прохождений,а так же даёт возможность хранить результаты всех попыток
    авторизированных пользователей пройти один и тот же опрос"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    answer = postgr.JSONField(default=dict)



