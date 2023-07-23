from django.http import request
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import CreateGame, index, LogoutUser, profile_player, RegisterUser, LoginUser, dismiss
from django.contrib.auth.decorators import login_required
app_name = 'main_site'
urlpatterns = [
    path('create_game', login_required(CreateGame.as_view()), name='Создание игры'),
    path('', index, name='Главная'),
    path('login', LoginUser.as_view(), name='Вход'),
    path('register', RegisterUser.as_view(), name='Регистрация'),
    path('logout', LogoutUser.as_view(), name='Выход'),
    path('profile_player', profile_player, name='Профиль игрока'),

    path('dismiss', dismiss, name='Распустить игровую комнату до старта'),
]