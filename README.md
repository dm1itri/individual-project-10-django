# Игрушка на Джанго

## Тема и описание проекта
Данная игра позволяет увеличить естестественно-научных знания в процессе развлечения с друзьями

## Сыграть - ДОПИСАТЬ

## Цели проекта:
- Расширить знания Django
- Разобраться с фронтенд разработкой (изучить JavaScript, Sass)
- Написать многопользовательскую WEB-игру


## Начало игры 
1. Перейдите на главную страницу WEB-приложения
2. Настройте игровую комнату
3. Нажмите создать игру
5. ПОзовите своих друзей

## Правила игры
- Игроки выполняют ход в той последовательности, в которой присоединились к игровому процессу
- Ход выполняется посредством бросания кубика
- В игре присутствует несколько типов клеток
  - С вопросом
    - По биологии
    - По географии
    - По истории
    - Случайный
  - Специальные
    - Парк - пропуск хода
    - Автобус в парк - переход к клетке Парк
    - Телепорт - перемещение на случайное количество клеток (1-23)
    - Подарок - получение дополнительного очка
    - Скелети (викинг) - потеря одного очка
  - Обычные
    - Старт
- При неправильном ответет на вопрос начисляется одно очко, при неправильном - ноль
- Завершение игры происходит при даче ответов на определённое количетсво вопросов

## Реализация ##

Код состоит из классов и функций, выполняющих всю работу

_**Классы**_:
- MyAPIView(APIView)
- PlayersAPIView(MyAPIView)
- GameAPIView(MyAPIView)
- HistoryAPIView(MyAPIView)
- QuestionAPIView(MyAPIView)
- PlayersStaticsAPIView(MyAPIView)
- GamesAPIView(ListAPIView)
- MyGameAPIView(APIView)
- QuestionAdmin(admin.ModelAdmin)
- GameAdmin(admin.ModelAdmin)
- HistoryMoveAdmin(admin.ModelAdmin)
- GameForm(forms.ModelForm)
- RegisterUserForm(BaseUserCreationForm)
- LoginUserForm(AuthenticationForm)
- Question(models.Model)
- Game(models.Model)
- HistoryMove(models.Model)
- Player(models.Model)
- CreateGame(CreateView)
- RegisterUser(CreateView)
- LoginUser(LoginView)
- LogoutUser(LogoutView)

_**Основные библиотеки**_:
- Django

_**Версия PYTHON**_:
- 3.12
