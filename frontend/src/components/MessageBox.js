import { useState, useContext, useEffect, useRef } from "react";
import { sendPacket } from "../connection";
import { GlobalContext } from "./GlobalContext";

import "./MessageBox.css";

function MessageBox() {
    const { messages } = useContext(GlobalContext);

    const [messageInput, setMessageInput] = useState("");

    const messageBox = useRef(null);

    function sendMessage(message) {
        if (message === "/trello") {
            window.open("https://trello.com/b/n23X0GGq/shove");
            return;
        }

        sendPacket("send_message", {
            message,
        });
    }

    useEffect(() => {
        messageBox.current.scrollTo({
            top: messageBox.current.scrollHeight,
            behavior: "smooth",
        });
    }, [messages]);

    return (
        <>
            <div ref={messageBox} className="messages-container">
                {messages.map((message, i) => (
                    <div key={i} className="message-container">
                        <div className="avatar-container">
                            <img
                                className="message-avatar"
                                src="/img/avatar.png"
                                alt="avatar"
                            />
                        </div>
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
    );
}

export default MessageBox;
