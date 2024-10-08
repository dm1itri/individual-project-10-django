from rest_framework import serializers
from main_site.models import Game


class GamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = (
            "id",
            "first_player",
            "second_player",
            "third_player",
            "fourth_player",
            "number_of_players",
            "number_of_players_connected",
        )
        depth = 2
