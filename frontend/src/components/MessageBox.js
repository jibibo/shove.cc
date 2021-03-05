import { useContext, useEffect } from "react";
import { GlobalContext } from "./GlobalContext";
import { socket } from "../connection";

function MessageBox() {
    const { messages, setMessages } = useContext(GlobalContext);

    function addMessage(text) {
        setMessages(messages.concat(text));
    }

    useEffect(() => {
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
        socket.on("chat_message", (packet) => {
            console.debug("> MessageBox chat_message", packet);
            addMessage(
                "Message from " + packet["username"] + ": " + packet["content"]
            );
        });
        socket.on("join_room_status", (packet) => {
            console.debug("> MessageBox join_room_status", packet);
            if (packet["success"]) {
                addMessage("Joined room " + packet["room_name"]);
            } else {
                addMessage("Failed to join " + packet["room_name"]);
            }
        });

        return () => {
            socket.off("client_connected");
            socket.off("client_disconnected");
            socket.off("message");
            socket.off("join_room_status");
        };
    });

    return (
        <>
            Messages:
            <div>
                {messages.map((message, i) => {
                    return <p key={i}>{message}</p>;
                })}
            </div>
        </>
    );
}

export default MessageBox;
