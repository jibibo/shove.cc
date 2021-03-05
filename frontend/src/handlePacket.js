import { useContext } from "react";

import { GlobalContext } from "./components/GlobalContext";

function handlePacket(packet) {
    const { messages, setMessages } = useContext(GlobalContext);

    console.debug("Handling received packet:", JSON.stringify(packet));
    const model = packet["model"];
    if (model === undefined) {
        console.error("Packet has no model set");
        return;
    }

    if (model === "client_connected") {
        if (packet["you"]) {
            setMessages(
                messages.concat("Connected! Your sid: " + packet["sid"])
            );
            document.getElementById("session-id").innerHTML = packet["sid"];
        } else {
            setMessages(messages.concat("Someone connected: " + packet["sid"]));
        }
        return;
    }

    if (model === "client_disconnected") {
        setMessages(messages.concat("Someone disconnected: " + packet["sid"]));
        return;
    }

    if (model === "join_room_status") {
        const success = packet["success"];
        const room_name = packet["room_name"];
        if (success) {
            setMessages(messages.concat("Joined room " + room_name + "!"));
        } else {
            const reason = packet["reason"];
            setMessages(
                messages.concat(
                    "Failed to join room " + room_name + ": " + reason
                )
            );
        }
        return;
    }

    if (model === "log_in_status") {
        const success = packet["success"];
        const username = packet["username"];

        if (success) {
            setMessages(messages.concat("Logged in as " + username + "!"));
            // loggedInAs = username;
        } else {
            const reason = packet["reason"];
            setMessages(
                messages.concat(
                    "Failed to log in as " + username + ": " + reason
                )
            );
        }
        return;
    }

    if (model === "message") {
        setMessages(
            messages.concat(packet["username"] + ": " + packet["content"])
        );
        return;
    }

    if (model === "register_status") {
        const success = packet["success"];
        const username = packet["username"];
        if (success) {
            setMessages(messages.concat("Registered as " + username + "!"));
        } else {
            const reason = packet["reason"];
            setMessages(
                messages.concat(
                    "Failed to register as " + username + ": " + reason
                )
            );
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

export default handlePacket;
