from datetime import datetime, timedelta
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.db.models import Q

from .forms import GameForm, RegisterUserForm, LoginUserForm
from .models import Player, HistoryMove
from .models import Game


class CreateGame(CreateView):
    form_class = GameForm
    template_name = "main_site/create_game.html"
    success_url = reverse_lazy("main_site:Главная")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание игры"
        return context

    def form_valid(self, form):
        player = Player.objects.get(user=self.request.user)
        is_playing = Game.objects.filter(
            (
                Q(first_player=player)
                | Q(second_player=player)
                | Q(third_player=player)
                | Q(fourth_player=player)
            )
            & Q(is_over=False)
        )
        if is_playing:
            return super().form_invalid(form)
        form.instance.first_player = player
        player.is_played = True
        player.save()
        return super().form_valid(form)


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = "main_site/register.html"
    success_url = reverse_lazy("main_site:Главная")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Регистрация"
        return context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect("main_site:Главная")


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "main_site/login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Авторизация"
        return context


class LogoutUser(LogoutView):
    next_page = reverse_lazy("main_site:Регистрация")


@login_required()
def index(request):
    player = get_object_or_404(Player, user=request.user)
    games = Game.objects.filter(
        Q(is_started=False)
        & (
            Q(datetime_creation__gt=(datetime.now() - timedelta(minutes=30)))
            | Q(first_player=player)
            | Q(second_player=player)
            | Q(third_player=player)
            | Q(fourth_player=player)
        )
    ).all()
    for game in games:
        setattr(
            game,
            "list_of_players",
            [
                game.first_player,
                game.second_player,
                game.third_player,
                game.fourth_player,
            ][: game.number_of_players],
        )
        setattr(game, "number_of_players", range(game.number_of_players))
    return render(
        request,
        "main_site/main.html",
        {"title": "Главная", "games": games, "this_player": player},
    )


@login_required()
def game(request, game_id):
    player = Player.objects.get(user=request.user)
    response = render(request, "main_site/game.html", {"title": "Игра"})
    response.set_cookie("number_move", str(player.number_move))
    response.set_cookie("game_id", str(game_id))
    return response


@login_required()
def dismiss(request):
    player = Player.objects.get(user=request.user)
    Game.objects.get(is_started=False, first_player=player).delete()
    return redirect("main_site:Главная")


@login_required()
def leave_started_game(request, game_id):
    player = Player.objects.get(user=request.user)
    game = Game.objects.get(id=game_id)
    if (
        player
        in [
            game.first_player,
            game.second_player,
            game.third_player,
            game.fourth_player,
        ]
        and game.is_started
    ):
        player.clear_after_game()
        game.is_over = True
        game.save()
        return redirect("main_site:Главная")


@login_required()
def join_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    if game.number_of_players_connected < game.number_of_players:
        player = Player.objects.get(user=request.user)
        match game.number_of_players_connected:
            case 1:
                game.second_player = player
            case 2:
                game.third_player = player
            case 3:
                game.fourth_player = player
        player.number_move = game.number_of_players_connected
        game.number_of_players_connected += 1
        player.save()
    if game.number_of_players_connected == game.number_of_players:
        game.is_started = True
        game.save()
        null_history_move = HistoryMove(
            game_id=game, number_history=0, number_move=-1, number_steps=0
        )
        null_history_move.save()
        return redirect("main_site:Игра", game_id)
    game.save()
    return redirect("main_site:Главная")


@login_required()
def leave_game(request, game_id):
    player = Player.objects.get(user=request.user)
    game = Game.objects.get(id=game_id)
    if game.second_player == player:
        game.second_player = game.third_player
        game.third_player = game.fourth_player
    elif game.third_player == player:
        game.third_player = game.fourth_player
    game.fourth_player = None
    game.save()
    return redirect("main_site:Главная")


@login_required()
def profile_player(request):
    player = Player.objects.get(user=request.user)
    context = {
        "title": "Профиль игрока",
        "date_joined": request.user.date_joined.strftime("%d.%m.%Y\n%H:%M"),
        "winning_percentage": int(
            player.global_number_of_correct_answers
            / player.global_number_of_questions_received
            * 100
        )
        if player.global_number_of_questions_received
        else 0,
        "games": player.global_number_games,
        "questions_received": player.global_number_of_questions_received,
    }
    return render(request, "main_site/profile.html", context=context)
