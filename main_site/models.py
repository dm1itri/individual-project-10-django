from django.db import models
from django.http import request
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator, StepValueValidator
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Question(models.Model):
    TYPE_QUESTION_CHOICES = [
        ('Б', 'Биология'),
        ('Г', 'География'),
        ('И', 'История'),
    ]
    type_question = models.CharField('Тип вопроса', max_length=1, choices=TYPE_QUESTION_CHOICES, default='Б')
    question = models.TextField('Вопрос', max_length=256, blank=True)
    answer_correct = models.CharField('Верный ответ', max_length=32, blank=True)
    answer_2 = models.CharField('Второй ответ', max_length=32, blank=True)
    answer_3 = models.CharField('Третий ответ', max_length=32, blank=True)
    answer_4 = models.CharField('Четвертый ответ', max_length=32, blank=True)
    datetime_addition = models.DateTimeField('Время добавления', default=timezone.now)

    def __str__(self):
        type_question = {
            'Б': 'Биология',
            'Г': 'География',
            'И': 'История',
        }
        return f'<Вопрос {self.id}> {type_question[self.type_question]}\t{self.question[:min(100, len(self.question))]}'

    class Meta:
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'


class Game(models.Model):
    current_player = models.IntegerField('Ходящий', default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    number_of_players = models.IntegerField('Количество игроков (2-4)', default=2, validators=[MinValueValidator(2), MaxValueValidator(4)])
    number_of_players_connected = models.IntegerField('Количество игроков (2-4) подключено', default=1, validators=[MinValueValidator(1), MaxValueValidator(4)])
    max_number_of_questions = models.IntegerField('Максимальное количество вопросов', default=10, validators=[MinValueValidator(10), MaxValueValidator(100), StepValueValidator(10)])
    number_of_questions_answered = models.IntegerField('Кол-во отвеченных вопросов', default=0)
    question_id = models.IntegerField('ID вопроса', default=None, blank=True, null=True)
    is_started = models.BooleanField('Начата', default=False)
    is_over = models.BooleanField('Завершена', default=False)
    datetime_creation = models.DateTimeField('Время создания', default=timezone.now)
    first_player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='first_player')
    second_player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='second_player', null=True)
    third_player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='third_player', null=True)
    fourth_player = models.ForeignKey('Player', on_delete=models.CASCADE, related_name='fourth_player', null=True)

    def __str__(self):
        return f'<Игра {self.id}> Текущий игрок: {self.current_player} Количество игроков: {self.number_of_players}'


    class Meta:
        verbose_name = 'игра'
        verbose_name_plural = 'игры'


class HistoryMove(models.Model):
    number_history = models.IntegerField('Номер истории', default=0, validators=[MinValueValidator(0)])
    number_move = models.IntegerField('Номер ходящего', default=-1, validators=[MinValueValidator(-1)])
    number_steps = models.IntegerField('Количество шагов', default=0, validators=[MinValueValidator(0), MaxValueValidator(23)])
    game_id = models.ForeignKey('Game', on_delete=models.CASCADE)
    datetime_addition = models.DateTimeField('Время добавления', default=timezone.now)

    def __str__(self):
        return f'<История {self.id}> ID игры: {self.game_id.id} Номер истории: {self.number_history} Номер ходяшего: {self.number_move} Количество шагов: {self.number_steps}'

    class Meta:
        verbose_name = 'история'
        verbose_name_plural = 'истории'


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user')
    is_played = models.BooleanField('Играет', default=False)
    current_position = models.IntegerField('Текущее положение', default=0, validators=[MinValueValidator(0), MaxValueValidator(23)])
    number_move = models.IntegerField('Порядкойвый номер в текущей игре', default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    number_of_points = models.IntegerField('Количество очков', default=0, validators=[MinValueValidator(0), ])
    number_of_questions_received = models.IntegerField('Кол-во ответов', default=0, validators=[MinValueValidator(0), ])
    number_of_correct_answers = models.IntegerField('Кол-во верных ответов', default=0, validators=[MinValueValidator(0), ])
    skipping_move = models.BooleanField('Пропуск хода', default=False)
    thinks_about_the_question = models.BooleanField('Думает над вопросом', default=False)

    def clear_after_game(self):
        self.is_played = False
        self.current_position = 0
        self.number_move = 0
        self.number_of_points = 0
        self.number_of_questions_received = 0
        self.number_of_correct_answers = 0
        self.skipping_move = False
        self.thinks_about_the_question = False
        self.save()


    def __str__(self):
        return f'{self.user}'

    class Meta:
        verbose_name = 'игрок'
        verbose_name_plural = 'игроки'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)