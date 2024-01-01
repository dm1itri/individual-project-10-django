from django import forms
from django.contrib.auth.forms import BaseUserCreationForm, AuthenticationForm

from .models import *


class GameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(GameForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Game

        fields = ['number_of_players', 'max_number_of_questions']
        widgets = {
            'number_of_players': forms.NumberInput(attrs={'class': "form-control", 'min': "2", 'max': "4", 'value': "2"}),
            'max_number_of_questions': forms.NumberInput(attrs={'class': "form-control", 'min': "10", 'max': "100", 'value': "10", 'step': "10"}),
            'first_player': forms.NumberInput()
        }


class RegisterUserForm(BaseUserCreationForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': "form-control"}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': "form-control"}))

    class Meta:
        model = User
        fields = ('username', )
        widgets = {'username': forms.TextInput(attrs={'class': "form-control"})}


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
