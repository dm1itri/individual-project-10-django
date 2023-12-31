// Для отображения вопроса соперника при перезагрузке страницы заменить строку
// games_args['question_id'] !== null && currentPlayer === thisPlayer на  games_args['question_id'] !== null
console.log(6)
const diceId = ['dicePlaying1', 'dicePlaying2', 'dicePlaying3', 'dicePlaying4', 'dicePlaying5', 'dicePlaying6']
const questionCards = [1, 2, 3, 4, 5, 6, 8, 10, 11, 13, 14, 15, 16, 17, 18, 20, 22, 23]
const questionBiologyCards = [2, 10, 14, 17, 22]
const questionHistoryCards = [1, 5, 11, 18, 23]
const rusNamePlayers = ['желтый', 'зеленый', 'красный', 'синий']
const enNamePlayers = ['yellow', 'green', 'red', 'blue']
const baseURL = 'http://127.0.0.1:8000' //'http://localhost:8001'   //
let answerCorrect, currentPlayer, numberHistory
let playersCoords = []
const thisPlayer = Number(document.cookie.match(/number_move=(.+?)(;|$)/)[1])  // 0-3
const csrftoken = String(document.cookie.match(/csrftoken=(.+?)(;|$)/)[1])
const thisGame =  Number(window.location.href.substring(window.location.href.lastIndexOf('/')+1))


function updateIconThisUser(){
    const sp = ['first', 'second', 'third', 'fourth']
    let chips = document.getElementById('chips')
    for (let i = 0; i < 4; i++) {
        img = document.createElement('img')
        img.id = i + '_Player'
        img.className = sp[i] + 'Player'
        img.alt = sp[i] + 'Player'
        img.src = baseURL + '/static/image/car_' + (i + 1) + '.png'
        if (thisPlayer === i) {
            let a = document.createElement("a")
            a.href = baseURL + '/leave_started_game/' + thisGame
            a.appendChild(img)
            chips.appendChild(a)
        } else {
            chips.appendChild(img)
        }
    }
}


function getPlayersStatics() {
    fetch(`${baseURL}/api/players_statics`)
        .then(response => response.json())
        .then(playersStatics => {
            for (let i=0; i < Object.keys(playersStatics).length; i++) {
                document.getElementById(`${i}Player`).style.display = 'block'
                document.getElementById(`${i}numberOfMoves`).innerText = playersStatics[i]['numbers_of_moves']
                document.getElementById(`${i}numberOfPoints`).innerText = playersStatics[i]['number_of_points']
                document.getElementById(`${i}numberOfQuestionsReceived`).innerText = playersStatics[i]['number_of_questions_received']
                document.getElementById(`${i}percentOfCorrectAnswers`).innerText = playersStatics[i]['percent_of_correct_answers']
            }
        })
}
function getCurrentPlayer() {
    let xhr = new XMLHttpRequest()
    let currPlayer
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                currPlayer = JSON.parse(xhr.response)
            }
            else {
                console.log(xhr.status)
            }
        }
    }
    xhr.open('GET', `${baseURL}/api/game`, false)
    xhr.send()
    return currPlayer
}
function postCurrentPLayer(skipMove, currentPlayer, playerCoords, numberOfPoints, thinksAboutTheQuestion) {
    const data = {
        'current_player': currentPlayer,
        'current_position': playerCoords,
        'skipping_move': skipMove,
        'number_of_points': numberOfPoints,
        'thinks_about_the_question': thinksAboutTheQuestion
    }
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status !== 200) {
            console.log(xhr.status)
        }
    }
    xhr.open('POST', `${baseURL}/api/game`, false)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.setRequestHeader("X-CSRFToken", csrftoken)
    xhr.send(JSON.stringify(data))
}
function postHistoryMove(currentPlayer, numberSteps) {
    const data = {
        'number_move': currentPlayer,
        'number_steps': numberSteps
    }
    let xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status !== 200) {
                console.log(xhr.status)
        }
    }
    xhr.open('POST', `${baseURL}/api/history_game`, false)
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.setRequestHeader("X-CSRFToken", csrftoken)
    xhr.send(JSON.stringify(data))
}


function getHistoryMove(numberHistory) {
    let xhr = new XMLHttpRequest()
    let history
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                history = JSON.parse(xhr.response)
            } else {
                history = null
        }
    }
    xhr.open('GET', `${baseURL}/api/history_game?number_history=${numberHistory}`, false)
    xhr.send()
    return history
}

function getQuestion(typeQuestion) {
    fetch(`${baseURL}/api/question?type_question=${typeQuestion}`)
        .then(response => response.json())
        .then(question => updateQuestion(question))

}
function getCurrentPlayers() {
    fetch(`${baseURL}/api/players`)
    .then(response => response.json())
    .then(games_args => {
        currentPlayer = games_args['current_player']
        numberHistory = games_args['number_history']
        for (let i = 0; i < games_args['count_players']; i++){
            playersCoords.push(games_args[`${i}_player`]['current_position'])
            document.getElementById(`${i}_Player`).style.display = 'block'
            if (playersCoords[i] !== 0) {rollDice(i, 0, playersCoords[i])}
        }
        if (games_args['question_id'] !== null && currentPlayer === thisPlayer) {
            updateQuestion(games_args['question'])
        }
    }).then(waiting_move)
}

const randomIntFromInterval = (min, max) => Math.floor(Math.random() * (max - min + 1) + min) // min and max included

function dicePlaying() {
    document.getElementById('buttonDicePlaying').style.visibility = 'hidden'
    let delay = 100
    let numberSteps = randomIntFromInterval(0, 5)
    let pastIndex, interval
    document.getElementById(diceId[numberSteps]).style.display = 'block'
    interval = setInterval(function() {
        pastIndex = numberSteps
        numberSteps = randomIntFromInterval(0, 5)
        numberSteps = (numberSteps === pastIndex) ? (numberSteps + 1) % 6 : numberSteps
        document.getElementById(diceId[numberSteps]).style.display = 'block'
        document.getElementById(diceId[pastIndex]).style.display = 'none'
        }, delay);

    setTimeout(() => clearInterval(interval), 2000)
    setTimeout(function () {
        document.getElementById(diceId[numberSteps]).style.display = 'none'
        move(currentPlayer, numberSteps + 1)
        // rollDice(currentPlayer, playersCoords[currentPlayer], currentIndex + 1)
    }, 3000) // 3000
}

function rollDice (numberPlayer, index_0, number_steps) {
    const square_cards = [0, 7, 12, 19]
    let realCoords = index_0
    let move
    if (index_0 >= 19) {
        index_0 -= 19
    } else if (index_0 >= 12) {
        index_0 -= 12
    } else if (index_0 >= 7) {
        index_0 -=7
    }

    for (let i = 1; i <= number_steps; i++) {
        if (0 <= realCoords && realCoords < 7) {
            if (numberPlayer % 2) {
                move =  realCoords !== 6 ? index_0  * 100 + 250 : index_0  * 100 + 350
            } else {
                move =  index_0  * 100 + 200
            }
            document.getElementById(`${numberPlayer}_Player`).style.left = move + 'px'
        } else if (7 <= realCoords && realCoords < 12) {
            if (numberPlayer < 2) {
                move = index_0 * 100 + 200
            } else {
                move = realCoords !== 11 ? index_0 * 100 + 250 : index_0 * 100 + 350
            }
            document.getElementById(`${numberPlayer}_Player`).style.top = move + 'px'
        } else if (12 <= realCoords && realCoords < 19) {
            if (numberPlayer % 2) {
                move =  750 - index_0 * 100
            } else {
                move = realCoords !== 18 ? 700 - index_0 * 100 : 700 - index_0 * 100 - 100
            }
            document.getElementById(`${numberPlayer}_Player`).style.left = move + 'px'
        } else {
            if (numberPlayer < 2) {
                move = realCoords !== 23 ? 500 - index_0 * 100 : 500 - index_0 * 100 - 100
            } else {
                move = 550 - index_0 * 100
            }
            document.getElementById(`${numberPlayer}_Player`).style.top = move + 'px'
        }
        realCoords = realCoords === 23 ? 0 : realCoords + 1
        index_0 = square_cards.includes(realCoords) ? 0: index_0 + 1
    }
    return realCoords
}

function checkSquareCards(numberPlayer) {
    if (playersCoords[numberPlayer] === 12) {
        let countSteps = randomIntFromInterval(1, 23)
        setTimeout(rollDice, 1000, numberPlayer, playersCoords[numberPlayer], countSteps)
        postHistoryMove(currentPlayer, countSteps)
        playersCoords[numberPlayer] = (countSteps + playersCoords[numberPlayer]) % 24
        numberHistory += 1
    }
    if (playersCoords[numberPlayer] === 19) {
        setTimeout(rollDice, 2000, numberPlayer, playersCoords[numberPlayer], 12)
        // 2000 таймаут поставлен, т.к. если попадет сюда с телепорта, то не будет видно перемещение сюда, а сразу в парк
        postHistoryMove(currentPlayer, 12)
        playersCoords[numberPlayer] = 7
        numberHistory += 1
    }
    if (playersCoords[numberPlayer] === 7) {
        return 1
    }
    return 0
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function updateDocument(currentPlayer, thinksAboutTheQuestion=false, gameIsOver) {
    document.getElementById("endGame").style.display = gameIsOver ? 'block':'none'
    document.getElementById("question").style.display = gameIsOver ? 'none':'block'
    document.getElementById("rollDice").style.display = gameIsOver ? 'none':'block'
    document.getElementById("numberPlayer").innerText = rusNamePlayers[currentPlayer]
    document.getElementById("numberPlayer").style.color = enNamePlayers[currentPlayer]
    document.getElementById("buttonDicePlaying").style.visibility = (currentPlayer === thisPlayer && !thinksAboutTheQuestion) ? 'visible' : 'hidden'
}

function updateQuestion(question) {
    answerCorrect = randomIntFromInterval(1, 4)
    document.getElementById("question_1").innerText = question['question']
    document.getElementById(`btn_answer_1`).disabled = false
    for (let i=2; i < 5; i++) {
        document.getElementById(`btn_answer_${i}`).value = question[`answer_${i}`]
        document.getElementById(`btn_answer_${i}`).disabled = false
    }
    if (answerCorrect !== 1) {
        document.getElementById(`btn_answer_1`).value = question[`answer_${answerCorrect}`]

    }
    document.getElementById(`btn_answer_${answerCorrect}`).value = question[`answer_correct`]
    document.getElementById("question").style.visibility = 'visible'
}

async function choosingAnswer(numberChoosingAnswer) {
    let point = 1
    for (let i=1; i<5; i++){
        document.getElementById(`btn_answer_${i}`).disabled = true
    }
    document.getElementById(`btn_answer_${answerCorrect}`).style.background = 'rgba(0,255,0,0.71)'
    if (numberChoosingAnswer !== answerCorrect) {
        point = 0
        document.getElementById(`btn_answer_${numberChoosingAnswer}`).style.background = 'rgba(255,0,0,0.89)'
    }
    setTimeout(function () {
        document.getElementById(`btn_answer_${answerCorrect}`).style.background = 'buttonface'
        document.getElementById(`btn_answer_${numberChoosingAnswer}`).style.background = 'buttonface'
        document.getElementById("question").style.visibility = 'hidden'
    }, 3000)
    await endMoveAndAnswer(currentPlayer, playersCoords[currentPlayer] === 7 ? 1 : 0, playersCoords[currentPlayer], point, 0)
}

async function move(numberPlayer, numberSteps) {
    let typeQuestion
    postHistoryMove(numberPlayer, numberSteps)
    numberHistory += 1
    playersCoords[numberPlayer] = rollDice(numberPlayer, playersCoords[numberPlayer], numberSteps)
    let skippingMove = checkSquareCards(numberPlayer)
    if (skippingMove === 0 && questionCards.includes(playersCoords[numberPlayer])) {
        endMoveAndAnswer(numberPlayer, skippingMove, playersCoords[numberPlayer], 0, 1)
        if (questionBiologyCards.includes(playersCoords[numberPlayer])){
            typeQuestion = 'Биология'
        } else if (questionHistoryCards.includes(playersCoords[numberPlayer])) {
            typeQuestion = 'История'
        } else if (playersCoords[numberPlayer] === 3 || playersCoords[numberPlayer] === 15){
            typeQuestion = 'Случайный'
        } else {
            typeQuestion = 'География' // !!!!!! Но здесь должны быть какие-то особенне вопросы
        }
        getQuestion(typeQuestion)
    }
    else {
        let point = playersCoords[numberPlayer] === 21 ? 1: playersCoords[numberPlayer] === 9 ?-1:0
        endMoveAndAnswer(numberPlayer, skippingMove, playersCoords[numberPlayer], point, 0)
    }
}

async function endMoveAndAnswer(numberPlayer, skipMove, playerCoords, numberOfPoints, thinksAboutTheQuestion) {
    postCurrentPLayer(skipMove, numberPlayer, playerCoords, numberOfPoints, thinksAboutTheQuestion)
    //currentPlayer = getCurrentPlayer()['current_player']
    //updateDocument(currentPlayer, thinksAboutTheQuestion)
    if (!thinksAboutTheQuestion) {
        await waiting_move()
    }
}

async function waiting_move() {
    let numberMove, result, nextHistory
    let t = true
    while (t) {
        getPlayersStatics()
        result = getCurrentPlayer()
        console.log(result['is_over'])
        if (result['is_over'] === false) {
            currentPlayer = result['current_player']
            updateDocument(currentPlayer, result['thinks_about_the_question'] && currentPlayer === thisPlayer, false)
            nextHistory = getHistoryMove(numberHistory + 1)
            if (currentPlayer === thisPlayer && nextHistory === null) {
                t = false
            } else if (nextHistory === null) {
                await sleep(2000)
            } else {
                numberMove = nextHistory['number_move']
                playersCoords[numberMove] = rollDice(numberMove, playersCoords[numberMove], nextHistory['number_steps'])
                numberHistory += 1
                await sleep (2000)
            }
        } else {
            setTimeout(updateDocument, 1000, currentPlayer, false, true)
            t = false
        }
    }
}


updateIconThisUser()
getCurrentPlayers()