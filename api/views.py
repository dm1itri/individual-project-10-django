from random import choice

from rest_framework.views import APIView
from rest_framework.response import Response
from main_site.models import Game, HistoryMove, Question
from django.db.models import Q
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from main_site.models import Player
from django.http import JsonResponse
from django.forms.models import model_to_dict


class MyAPIView(APIView):
    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [IsAuthenticated]
    def get(self, request):
        game_id = request.COOKIES.get('game_id')
        self.game = Game.objects.get(id=game_id)
        self.players = [self.game.first_player, self.game.second_player, self.game.third_player, self.game.fourth_player]

    def put(self, request):
        self.get(request)


class PlayersAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        players = self.players[:self.game.number_of_players]
        number_history = HistoryMove.objects.filter(game_id=self.game.id).order_by('number_history').last().number_history
        response = {
            'current_player': self.game.current_player,
            'question_id': self.game.question_id,
            'count_players': self.game.number_of_players,
            'number_history': number_history
        }
        for i in range(self.game.number_of_players):
            response[f'{i}_player'] = {'current_position': players[i].current_position,
                                       'skipping_move': players[i].skipping_move,
                                       'thinks_about_the_question': players[i].thinks_about_the_question}
        if response['question_id']:
            response['question'] = Question.objects.get(response['question_id']).to_dict(only=('question', 'answer_correct', 'answer_2', 'answer_3', 'answer_4'))
        return Response(response)


class GameAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        current_player = self.players[self.game.current_player]

        return JsonResponse(model_to_dict(self.game, fields=['current_player', 'question_id', 'is_over']) |
                            model_to_dict(current_player, fields=['thinks_about_the_question', ]))

    def put(self, request):
        super().put(request)
        current_player = int(self.request.GET['current_player'])
        current_position = int(self.request.GET['current_position'])
        skipping_move = int(self.request.GET['skipping_move'])
        number_of_points = int(self.request.GET['number_of_points'])
        thinks_about_the_question = int(self.request.GET['thinks_about_the_question'])

        player = self.players[self.game.current_player]
        player.current_position = current_position
        player.skipping_move = skipping_move
        player.number_of_points += number_of_points
        player.thinks_about_the_question = bool(thinks_about_the_question)
        if current_position not in (9, 21) and bool(thinks_about_the_question) == False:
            player.number_of_correct_answers += number_of_points
            self.game.number_of_questions_answered += 1
            if self.game.number_of_questions_answered == self.game.max_number_of_questions:
                self.game.is_over = True
        self.game.save()
        player.save()
        if not player.thinks_about_the_question and not self.game.is_over:
            curr_player = (current_player + 1) % self.game.number_of_players
            for i in range(4):
                player = self.players[self.game.current_player]
                if player.skipping_move:
                    player.skipping_move = False
                    curr_player = (current_player + 1) % self.game.number_of_players
                else:
                    break

            self.game.current_player = curr_player
            self.game.question_id = None
            player.save()
            self.game.save()


class HistoryAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        number_history = int(self.request.GET['number_history'])
        if number_history:
            move = HistoryMove.objects.filter(game_id=self.game.id, number_history=number_history).first()
        else:
            move = HistoryMove.objects.filter(game_id=self.game.id).order_by('-number_history').first()
        if move:
            return JsonResponse(model_to_dict(move, fields=['number_history', 'number_move', 'number_steps']))
        return JsonResponse({'response': None})

    def put(self, request):
        super().put(request)
        number_move = int(self.request.GET['number_move'])
        number_steps = int(self.request.GET['number_steps'])
        history = HistoryMove()
        history.game_id = self.game
        history.number_history = HistoryMove.objects.filter(game_id=self.game.id).order_by('-number_history').first().number_history + 1
        history.number_move = number_move
        history.number_steps = number_steps
        history.save()


class QuestionAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        type_question = self.request.GET['type_question']
        if type_question == 'Случайный':
            type_question = choice(['Биология', 'История', 'География'])
        question = choice(Question.objects.filter(type_question=type_question).all())
        game = Game.objects.get(id=self.game.id)
        game.question_id = question.id
        player = [game.first_player, game.second_player, game.third_player, game.fourth_player][game.current_player]
        player.number_of_questions_received += 1
        game.save()
        player.save()


class PlayersStaticsAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        players_statics = {}
        players = self.players[:self.game.number_of_players]
        for index, player in enumerate(players):
            players_statics[index] = {'numbers_of_moves': HistoryMove.objects.filter(game_id=self.game.id, number_move=index).count(),
                                      'percent_of_correct_answers': f'{round(player.number_of_correct_answers / player.number_of_questions_received * 100if player.number_of_questions_received else 0)}%',
                                      **model_to_dict(player, fields=['number_of_points', 'number_of_questions_received'])}
        return JsonResponse(players_statics)