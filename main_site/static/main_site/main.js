const baseURL = 'http://127.0.0.1:8000'
const user_id = JSON.parse(document.getElementById('user_id').textContent)
const csrftoken = String(document.cookie.match(/csrftoken=(.+?)(;|$)/)[1])
let lastGames
const TIMEOUT = 1000

function getMyGame() {
    fetch(`${baseURL}/api/mygame/${user_id}`)
        .then(response => response.json())
        .then(game => checkMyGame(game))
}


function getGames() {
    fetch(`${baseURL}/api/games`)
        .then(response => response.json())
        .then(games => displayGames(games))
}


function checkMyGame(game) {
    console.log(game)
    if (game['number_of_players'] === game['number_of_players_connected']) {
        window.location.replace(`${baseURL}/game/${game['id']}`)
    }
}


function displayGames(games) {
    if (games !== lastGames) {
        lastGames = games
        let append_button
        const main = document.getElementById('main')
        main.innerHTML = ''
        for (let i = 0; i < games.length; i++) {
            // create a new div element
            let game = games[i]
            let divRow = document.createElement("div")
            divRow.className = "row row-cols-5 gameroom"
            let players = [game['first_player'], game['second_player'], game['third_player'], game['fourth_player']].slice(0, game['number_of_players'])
            let button = document.createElement("button")
            button.type = 'submit'
            button.name = 'dismiss'
            button.className = 'btn btn-danger'
            for (let j = 0; j < players.length; j++) {
                let player = players[j]
                let divCol = document.createElement("div")
                divCol.className = "col"
                let img = document.createElement("img")
                img.className = 'rounded-circle'
                let a = document.createElement("a")
                a.className = 'btn btn-secondary'
                if (player !== null) {
                    img.src = 'static/image/astronaut.png'
                    img.alt = 'Аватарка'
                    a.text = player['user']['username']
                    a.href = baseURL + "/profile_player"
                } else {
                    img.src = 'static/image/add.png'
                    img.alt = 'Присоединиться'
                    a.text = 'Свободно'
                    a.href = baseURL + `/join_game/${game['id']}`
                }
                divCol.appendChild(img)
                divCol.appendChild(a)
                divRow.appendChild(divCol)
                if (player !== null) {
                    if (player['user']['id'] === user_id) {
                        button.innerText = 'Покинуть'
                        append_button = true
                    }
                }
            }
            if (game['first_player']['user']['id'] === user_id) {
                button.innerText = 'Распустить'
                button.onclick = dismiss
            }
            if (append_button) {
                divRow.appendChild(button)
            }
            main.append(divRow)
        }
    }
}


function dismiss() {
    let xhr = new XMLHttpRequest()
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status !== 200) {
            console.log(xhr.status)
        }
    }
    xhr.open('POST', `${baseURL}/dismiss`, false)
    //xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    xhr.setRequestHeader("X-CSRFToken", csrftoken)
    xhr.send()
    getGames()
}


document.body.onload = getGames
setInterval(getGames, TIMEOUT)
setInterval(getMyGame, TIMEOUT)

