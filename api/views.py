from random import choice

from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers import GamesSerializer
from main_site.models import Game, HistoryMove, Question
from django.db.models import Q
from django.http import JsonResponse
from django.forms.models import model_to_dict


class MyAPIView(APIView):
    def get(self, request):
        game_id = request.COOKIES.get("game_id")
        self.game = Game.objects.get(id=game_id)
        self.players = [
            self.game.first_player,
            self.game.second_player,
            self.game.third_player,
            self.game.fourth_player,
        ]


class PlayersAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        players = self.players[: self.game.number_of_players]
        number_history = (
            HistoryMove.objects.filter(game=self.game)
            .order_by("number_history")
            .last()
            .number_history
        )
        response = {
            "current_player": self.game.current_player,
            "question_id": self.game.question_id,
            "count_players": self.game.number_of_players,
            "number_history": number_history,
        }
        for i in range(self.game.number_of_players):
            response[f"{i}_player"] = {
                "current_position": players[i].current_position,
                "skipping_move": players[i].skipping_move,
                "thinks_about_the_question": players[i].thinks_about_the_question,
            }
        if response["question_id"]:
            response["question"] = model_to_dict(
                Question.objects.get(id=response["question_id"]),
                fields=[
                    "question",
                    "answer_correct",
                    "answer_2",
                    "answer_3",
                    "answer_4",
                ],
            )
        return Response(response)


class GameAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        current_player = self.players[self.game.current_player]

        return JsonResponse(
            model_to_dict(
                self.game, fields=["current_player", "question_id", "is_over"]
            )
            | model_to_dict(
                current_player,
                fields=[
                    "thinks_about_the_question",
                ],
            )
        )

    def post(self, request):
        super().get(request)
        current_player = int(self.request.data["current_player"])
        current_position = int(self.request.data["current_position"])
        skipping_move = int(self.request.data["skipping_move"])
        number_of_points = int(self.request.data["number_of_points"])
        thinks_about_the_question = int(self.request.data["thinks_about_the_question"])

        player = self.players[self.game.current_player]
        player.current_position = current_position
        player.skipping_move = skipping_move
        player.number_of_points += number_of_points
        player.thinks_about_the_question = bool(thinks_about_the_question)
        if current_position not in (9, 21) and not bool(thinks_about_the_question):
            player.number_of_correct_answers += number_of_points
            self.game.number_of_questions_answered += 1
            if (
                self.game.number_of_questions_answered
                == self.game.max_number_of_questions
            ):
                self.game.is_over = True
                for i in self.players:
                    if i:
                        i.clear_after_game()
        self.game.save()
        player.save()
        if not player.thinks_about_the_question and not self.game.is_over:
            curr_player = (current_player + 1) % self.game.number_of_players
            for i in range(4):
                player = self.players[self.game.current_player]
                if not player.skipping_move:
                    break
                player.skipping_move = False
                curr_player = (current_player + 1) % self.game.number_of_players

            self.game.current_player = curr_player
            self.game.question_id = None
            player.save()
            self.game.save()
        return Response(status=status.HTTP_201_CREATED)


class HistoryAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        number_history = int(self.request.GET["number_history"])
        if number_history:
            move = HistoryMove.objects.filter(
                game=self.game, number_history=number_history
            ).first()
        else:
            move = (
                HistoryMove.objects.filter(game=self.game)
                .order_by("-number_history")
                .first()
            )
        if move:
            return JsonResponse(
                model_to_dict(
                    move, fields=["number_history", "number_move", "number_steps"]
                )
            )
        return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        super().get(request)
        number_move = int(self.request.data["number_move"])
        number_steps = int(self.request.data["number_steps"])
        HistoryMove.objects.create(
            game=self.game,
            number_history=HistoryMove.objects.filter(game=self.game)
            .order_by("-number_history")
            .first()
            .number_history
            + 1,
            number_move=number_move,
            number_steps=number_steps,
        )
        return Response(status=status.HTTP_201_CREATED)


class QuestionAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        type_question = self.request.query_params["type_question"]
        if type_question == "Случайный":
            type_question = choice(["Биология", "История", "География"])
        question = choice(Question.objects.filter(type_question=type_question[0]).all())

        self.game.question_id = question.id
        player = self.players[self.game.current_player]
        player.number_of_questions_received += 1
        self.game.save()
        player.save()
        return JsonResponse(
            model_to_dict(
                question,
                fields=[
                    "question",
                    "answer_correct",
                    "answer_2",
                    "answer_3",
                    "answer_4",
                ],
            )
        )


class PlayersStaticsAPIView(MyAPIView):
    def get(self, request):
        super().get(request)
        players_statics = {}
        players = self.players[: self.game.number_of_players]
        for index, player in enumerate(players):
            players_statics[index] = {
                "numbers_of_moves": HistoryMove.objects.filter(
                    game=self.game, number_move=index
                ).count(),
                "percent_of_correct_answers": f"{int(player.number_of_correct_answers / player.number_of_questions_received * 100) if player.number_of_questions_received else 0}%",
                **model_to_dict(
                    player, fields=["number_of_points", "number_of_questions_received"]
                ),
            }
        return JsonResponse(players_statics)


class GamesAPIView(ListAPIView):
    queryset = Game.objects.filter(is_started=False).all()
    serializer_class = GamesSerializer


class MyGameAPIView(APIView):
    def get(self, *args, **kwargs):
        user_id = kwargs.get("user_id")
        try:
            game = Game.objects.get(
                (
                    Q(first_player__user__id=user_id)
                    | Q(second_player__user__id=user_id)
                    | Q(third_player__user__id=user_id)
                    | Q(fourth_player__user_id=user_id)
                )
                & Q(is_over=False)
            )
            return JsonResponse(model_to_dict(game))
        except Game.DoesNotExist:
            return Response(None)
