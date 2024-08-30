from django.contrib import admin
from .models import Question, Game, HistoryMove, Player


class QuestionAdmin(admin.ModelAdmin):
    list_display = ["type_question", "question", "answer_correct", "datetime_addition"]
    list_filter = ["type_question", "datetime_addition"]
    fieldsets = [
        ("Стандартная информация", {"fields": ["type_question", "question"]}),
        (
            "Ответы",
            {
                "fields": ["answer_correct", "answer_2", "answer_3", "answer_4"],
                "classes": ["collapse"],
            },
        ),
    ]


class GameAdmin(admin.ModelAdmin):
    list_display = [
        "current_player",
        "number_of_players",
        "number_of_players_connected",
        "is_started",
        "is_over",
        "datetime_creation",
    ]
    list_filter = ["is_started", "is_over", "datetime_creation"]


class HistoryMoveAdmin(admin.ModelAdmin):
    list_display = [
        "game_id",
        "number_history",
        "number_move",
        "number_steps",
        "datetime_addition",
    ]
    list_filter = ["game_id", "datetime_addition"]


# Register your models here.
admin.site.register(Question, QuestionAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(HistoryMove, HistoryMoveAdmin)
admin.site.register(Player)
