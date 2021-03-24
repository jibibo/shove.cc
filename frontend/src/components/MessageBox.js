import { useState, useContext, useRef } from "react";
import { sendPacket, socket } from "../connection";
import { GlobalContext } from "./GlobalContext";

import "./MessageBox.css";

let deaf = true;

function MessageBox() {
    const { messages, setMessages } = useContext(GlobalContext);

    const [message, setMessage] = useState("");
    const [visible, setVisible] = useState(true);

    const messageBox = useRef(null);

    function addMessage(author, text) {
        if (visible) {
            // also gets run after typing "hide"?
            // console.log("Adding message (visible is true)");
            setMessages((messages) => [...messages, {
                author,
                text
            }]);

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
            message,
        });

        setMessage("");
    }

    if (deaf) {
        deaf = false;
        // useEffect(() => {
            
        socket.on("message", (packet) => {
            console.debug("> MessageBox message", packet);
            addMessage(packet.author, packet.content);
        });

        socket.on("command_success", (packet) => {
            console.debug("> MessageBox command_success", packet);
            addMessage(packet.response)
        });

        socket.on("error", (packet) => {
            console.debug("Messagebox error", packet);
            addMessage("Error: " + packet.description);
        });

        socket.on("user_connected", (packet) => {
            console.debug("> MessageBox user_connected", packet);
            if (!packet.you) {
                addMessage("Someone connected");
            }
        });

        socket.on("user_disconnected", (packet) => {
            console.debug("> MessageBox user_disconnected", packet);
            let disconnectedUsername;

            if (packet.username) {
                disconnectedUsername = packet.username;
            } else {
                disconnectedUsername = "Someone";
            }

            addMessage(disconnectedUsername + " disconnected");
        });

        socket.on("join_room", (packet) => {
            console.debug("> MessageBox join_room", packet);
            addMessage("Joined room " + packet.room_name);  
        });

        socket.on("log_in", (packet) => {
            console.debug("> MessageBox log_in", packet);
            addMessage("Signed in as " + packet.account_data.username);
        });
    }

    return (
        <>
            <div ref={messageBox} className="messages-container">
                {messages.map((message, key) => (
                    <div key={key} className="message">
                        <div className="profile-picture">
                            <img
                                className="picture"
                                src="/img/avatar.png"
                                alt="avatar"
                            />
                        </div>
                        <div className="message-content">
                            <span style={{ fontWeight: 700 }} >{message.author}</span><br /><span style={{ fontWeight: 300 }}>{message.text}</span>
                        </div>
                    </div>
                ))}
            </div>
            <form className="message-input" onSubmit={onSubmit}>
                <input
                    type="textarea"
                    onChange={(event) => setMessage(event.target.value)}
                    value={message}
                    placeholder="Type Here..."
                />
            </form>
        </>
    );
}

export default MessageBox;
