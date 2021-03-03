const socket = io.connect("http://" + document.domain + ":80")
const state = {
    room: null
}

// functionality

$("form.message").on("submit", onSubmitMessage)
$("form.room").on("submit", onSubmitRoom)

function addToBox(message) {
    $("h1.nothing-here").remove()
    $("div.message-holder").append("<div class='message-bubble'>" + message + "</div>")
}

function onSubmitRoom(e) {
    e.preventDefault()
    let room = $("input.room").val()
    $("input.room").empty()

    sendPacket({
        model: "room_join",
        room: room
    })
}

function onSubmitMessage(e) {
    e.preventDefault()
    const username = $("input.username").val()
    const message = $("input.message").val()
    $("input.message").val("").focus()

    sendPacket({
        model: "message",
        room: state.room,
        username : username,
        message : message
    })
}

// packets


socket.on("message", packet => {
    handlePacket(packet)
})

function handlePacket(packet) {
    console.debug("Handling received packet: " + JSON.stringify(packet))

    const model = packet.model

    if (model === undefined) {
        console.error("No packet model set")
        return
    }

    if (model === "message") {
        addToBox(packet["username"] + ": " + packet["message"])
        return
    }

    if (model === "room_joined_status") {
        if (packet["success"]) {
            state.room = packet["room"]
            addToBox("Joined room " + packet["room"])
        } else {
            addToBox("Failed to join room")
        }
        return
    }

    if (model === "room_joined_someone") {
        addToBox("Someone joined the room: " + packet["username"])
        return
    }

    if (model === "client_connected") {
        if (packet["you"]) {
            state.sid = packet["sid"]
            addToBox("Connected! Your sid: " + packet["sid"])
        } else {
            addToBox("Someone connected: " + packet["sid"])
        }
        return
    }

    if (model === "client_disconnected") {
        addToBox("Someone disconnected: " + packet["sid"])
        return
    }

    console.error("Unknown packet model: " + model)
}

function sendPacket(packet) {
    socket.send(packet)
    console.debug("Sent packet: " + JSON.stringify(packet))
}