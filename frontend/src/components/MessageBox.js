import { useState, useContext, useEffect, useRef } from "react";

import { sendPacket } from "../connection";
import { GlobalContext } from "./GlobalContext";
import UserAvatar from "./UserAvatar";

import "./MessageBox.css";

const show = true; // for debugging

function MessageBox() {
    const { messages } = useContext(GlobalContext);

    const [messageInput, setMessageInput] = useState("");

    const messageBox = useRef(null);

    function sendMessage(message) {
        sendPacket("send_message", {
            message,
        });
    }

    useEffect(() => {
        if (show) {
            messageBox.current.scrollTo({
                top: messageBox.current.scrollHeight,
                behavior: "smooth",
            });
        }
    }, [messages]);

    return show ? (
        <>
            <div ref={messageBox} className="messages-container">
                {messages.map((message, i) => (
                    <div key={i} className="message-container">
                        {message.type === "message" ? (
                            <UserAvatar username={message.author} />
                        ) : null}

                        <div className="message-content">
                            <span className="message-author">
                                {message.author}
                            </span>
                            <br />
                            <span className="message-text">{message.text}</span>
                        </div>
                    </div>
                ))}
            </div>
            <form
                className="message-input"
                onSubmit={(e) => {
                    e.preventDefault();
                    sendMessage(messageInput);
                    setMessageInput("");
                }}
            >
                <input
                    type="textarea"
                    onChange={(event) => setMessageInput(event.target.value)}
                    value={messageInput}
                    placeholder="Type Here..."
                />
            </form>
        </>
    ) : null;
}

export default MessageBox;
