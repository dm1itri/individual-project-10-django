from django.http import request
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from .views import PlayersAPIView, GameAPIView, HistoryAPIView, QuestionAPIView, PlayersStaticsAPIView

app_name = 'api'
urlpatterns = [
    path('players', PlayersAPIView.as_view(), name='PlayersAPIView'),
    path('game', GameAPIView.as_view(), name='GameAPIView'),
    path('history_game', HistoryAPIView.as_view(), name='HistoryAPIView'),
    path('question', QuestionAPIView.as_view(), name='QuestionAPIView'),
    path('players_statics', PlayersStaticsAPIView.as_view(), name='PlayersStaticsAPIView')
]