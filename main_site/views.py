import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import get_object_or_404, render, redirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Q

from .forms import GameForm, RegisterUserForm, LoginUserForm
from .models import Question, Game, Player
from .models import Game


class CreateGame(CreateView):
    form_class = GameForm
    template_name = 'main_site/create_game.html'
    success_url = reverse_lazy('main_site:Главная')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание игры'
        return context

    def form_valid(self, form):
        player = Player.objects.get(user=self.request.user)
        is_playing = Game.objects.filter((Q(first_player=player) | Q(second_player=player) | Q(third_player=player) | Q(fourth_player=player)) & Q(is_over=False))
        if is_playing:
            return super().form_invalid(form)
        form.instance.first_player = player
        return super().form_valid(form)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'main_site/register.html'
    success_url = reverse_lazy('main_site:Главная')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('main_site:Главная')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'main_site/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация'
        return context


class LogoutUser(LogoutView):
    next_page = reverse_lazy('main_site:Главная')


@login_required()
def index(request):
    games = Game.objects.filter(Q(is_started=False) & (Q(datetime_creation__gt=(datetime.datetime.now() - datetime.timedelta(minutes=30))) | Q(first_player=Player.objects.get(user=request.user)))).all()
    for game in games:
        setattr(game, 'list_of_players', [game.first_player, game.second_player, game.third_player, game.fourth_player][:game.number_of_players])
        setattr(game, 'number_of_players', range(game.number_of_players))
    return render(request, 'main_site/main.html', {'title': 'Главная', 'games': games, 'this_player': Player.objects.get(user=request.user)})


@login_required()
def dismiss(request):
    Game.objects.get(is_started=False, first_player=Player.objects.get(user=request.user)).delete()
    return redirect('main_site:Главная')


@login_required()
def profile_player(request):
    return render(request, 'main_site/base.html', {'title': 'Профиль игрока'})

