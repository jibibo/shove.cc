import io from "socket.io-client";
import { useEffect, useState } from "react";


function checkIfOnline() {
    let img = document.body.appendChild(document.createElement("img"));
    img.onload = () => {
        return "online";
    }
    img.onerror = () => {
        return "offline";
    }
    // img.src = "http://shove.cc/img/icon.png";
}

function addToBox(message) {
    let element = document.createElement("p");
    let list = document.getElementById("message-list");
    list.insertBefore(element, list.firstChild);
    element.innerHTML = message;
}


function App() {
    const [socket, setSocket] = useState();
    const [card, setCard] = useState(null);

    useEffect(() => {
        const connection = io.connect("http://" + document.domain + ":777");
        connection.on("message", packet => {
            handlePacket(packet);
        });
        connection.on("connect", () => {
            console.log("socket connect event");
        });
        connection.on("disconnect", () => {
            console.log("socket disconnect event");
        });
        setSocket(connection);
        connection.send({
            "model": "get_rooms",
            "properties": ["name"]
        });
    }, []);

    function onBye(packet) {
        let card = packet["bye"]; // "jc"
        console.log(card);
        setCard(card);
    }

    function onJoinRoomFormSubmit(e) {
        e.preventDefault();
        const roomName = document.getElementById("join-room-input").value;
        document.getElementById("join-room-input").value = "";
        sendPacket({
            "model": "join_room",
            "room_name": roomName
        });
    }

    function onLogInFormSubmit(e) {
        e.preventDefault();
        const username = document.getElementById("log-in-username").value;
        const passwordElement = document.getElementById("log-in-password");
        const password = passwordElement.value;
        console.log(username + password);
        passwordElement.value = ""
        sendPacket({
            "model": "log_in",
            "username": username,
            "password": password
        });
    }

    function onRegisterFormSubmit(e) {
        e.preventDefault();
        const username = document.getElementById("register-username").value;
        const passwordElement = document.getElementById("register-password");
        const password = passwordElement.value;
        passwordElement.value = ""
        sendPacket({
            "model": "register",
            "username": username,
            "password": password
        });
    }

    function handlePacket(packet) {
        console.debug("Handling received packet: " + JSON.stringify(packet));
        const model = packet["model"];
        if (model === undefined) {
            console.error("Packet has no model set");
            return;
        }

        if (model === "bye") {
            onBye(packet)
            return;
        }

        if (model === "client_connected") {
            if (packet["you"]) {
                addToBox("Connected! Your sid: " + packet["sid"]);
                document.getElementById("session-id").innerHTML = packet["sid"];
            } else {
                addToBox("Someone connected: " + packet["sid"]);
            }
            return;
        }

        if (model === "join_room_status") {
            const success = packet["success"];
            const room_name = packet["room_name"];
            if (success) {
                addToBox("Joined room " + room_name + "!");
            } else {
                const reason = packet["reason"];
                addToBox("Failed to join room " + room_name + ": " + reason);
            }
            console.log("join room success: " + success)
            return;
        }

        if (model === "log_in_status") {
            const success = packet["success"];
            const username = packet["username"];

            if (success) {
                addToBox("Logged in as " + username + "!");
            } else {
                const reason = packet["reason"];
                addToBox("Failed to log in as "+ username + ": " + reason);
            }
            return;
        }

        if (model === "message") {
            addToBox(packet["username"] + ": " + packet["content"])
            return;
        }

        if (model === "register_status") {
            const success = packet["success"];
            const username = packet["username"];
            if (success) {
                addToBox("Registered as " + username + "!");
            } else {
                const reason = packet["reason"];
                addToBox("Failed to register as " + username + ": " + reason);
            }
            return;
        }

        if (model === "room_list") {
            const rooms = packet["rooms"];
            let list = document.getElementById("room-list");
            list.innerHTML = "";
            for (let i = 0; i < rooms.length; i++) {
                const room = rooms[i];
                list.innerHTML += room["name"] + ", ";
            }
            return;
        }

        console.error("Failed handling packet model: " + model);
    }

    function sendPacket(packet) {
        socket.send(packet);
        console.debug("Sent packet: " + JSON.stringify(packet));
    }

    return (
        <div className="App">
            Website status: <span id="website-status">website ping status here</span>
            <div id="online-status">{checkIfOnline()}</div>
            Session id: <span id="session-id">session id goes here</span>
            <br /><br />

            Register:
            <form onSubmit={onRegisterFormSubmit}>
                <input type="text" id="register-username" placeholder="Username" />
                <input type="password" id="register-password" placeholder="Password" />
            </form>

            Log in:
            <form onSubmit={onJoinRoomFormSubmit}>
                <input type="text" id="log-in-username" placeholder="Username" />
                <input type="password" id="log-in-password" placeholder="Password" />
            </form>

            Rooms:
            <div id="room-list" />
            <br />

            <form onSubmit={onJoinRoomFormSubmit}>
                <input type="text" id="join-room-input" placeholder="Enter room to join" />
            </form>
            <br />

            <button onClick={() => {sendPacket({"model": "hello"}) }}>
                fuck off
            </button>
            <br />
            Messages:
            <div id="message-list" />
            <br />
            { card ? <img alt="jc" src={`./games/holdem/${card}.svg`} /> : "" }
        </div>
    );
}

export default App;
