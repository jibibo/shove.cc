import { useContext, useEffect } from "react";
import { socket } from "../connection";
import { GlobalContext } from "./GlobalContext";

let deaf = true;

function MessageBox() {
    const { messages, setMessages } = useContext(GlobalContext);

    console.log("MessageBox()");

    function addMessage(text) {
        setMessages((messages) => [text, ...messages]);
    }

    useEffect(() => {
        // if (deaf) {
        deaf = false;

        // socket.on("connect_error", () => {
        //     addMessage("test");
        // })

        socket.on("chat_message", (packet) => {
            console.debug("> MessageBox chat_message", packet);
            addMessage(
                "Message from " + packet["username"] + ": " + packet["content"]
            );
        });

        socket.on("client_connected", (packet) => {
            console.debug("> MessageBox client_connected", packet);
            if (packet["you"]) {
                addMessage("Connected!");
            } else {
                addMessage("Someone connected: " + packet["sid"]);
            }
        });

        socket.on("client_disconnected", (packet) => {
            console.debug("> MessageBox client_disconnected", packet);
            addMessage("Someone disconnected: " + packet["sid"]);
        });

        socket.on("join_room_status", (packet) => {
            console.debug("> MessageBox join_room_status", packet);
            if (packet["success"]) {
                addMessage("Joined room " + packet["room_name"]);
            } else {
                addMessage("Failed to join " + packet["room_name"]);
            }
        });

        socket.on("log_in_status", (packet) => {
            console.debug("> MessageBox log_in_status", packet);
            if (packet["success"]) {
                addMessage("Signed in as " + packet["username"]);
            } else {
                addMessage("Failed to sign in as " + packet["username"]);
            }
        });
    }, [socket]);

    return (
        <>
            Messages:
            {messages.map((message, i) => (
                <p key={i}>{message}</p>
            ))}
        </>
    );
}

export default MessageBox;
