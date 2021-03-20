import { useState, useContext, useRef } from "react";
import { sendPacket, socket } from "../connection";
import { GlobalContext } from "./GlobalContext";

import "./MessageBox.css";

let deaf = true;

function MessageBox() {
    const { messages, setMessages, user } = useContext(GlobalContext);

    const [message, setMessage] = useState("");
    const [visible, setVisible] = useState(true);

    const messageBox = useRef(null);

    function addMessage(text) {
        if (visible) {
            // also gets run after typing "hide"?
            // console.log("Adding message (visible is true)");
            setMessages((messages) => [...messages, text]);

            // TODO: why does this work??

            messageBox.current.scrollTo({
                top: messageBox.current.scrollHeight,
                behavior: "smooth",
            });
        }
    }

    function onSubmit(event) {
        event.preventDefault();
        if (message === "hide") {
            setVisible(false);
            console.log("MessageBox is now hidden");
            return;
        }

        sendPacket("send_message", {
            username: user,
            content: message,
        });

        setMessage("");
    }

    if (deaf) {
        deaf = false;
        // useEffect(() => {
        socket.on("chat_message", (packet) => {
            console.debug("> MessageBox chat_message", packet);
            addMessage(packet["username"] + " > " + packet["content"]);
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
                addMessage("Failed to join room: " + packet["reason"]);
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
    }

    return visible ? (
        <div className="messages-container">
            <div ref={messageBox} className="message-box">
                {messages.map((message, i) => (
                    <div className="message" key={i}>
                        <img src="/img/avatar.png" alt="donald_duck" />
                        <p>{message}</p>
                    </div>
                ))}
            </div>
            <form className="message-input" onSubmit={onSubmit}>
                <input
                    type="textarea"
                    onChange={(event) => setMessage(event.target.value)}
                    value={message}
                    placeholder="Message"
                />
            </form>
        </div>
    ) : null;
}

export default MessageBox;
