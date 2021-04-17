import { useState, useContext, useEffect, useRef } from "react";

import { sendPacket } from "../connection";
import { GlobalContext } from "./GlobalContext";
import UserAvatar from "./UserAvatar";

import "./MessageBox.css";

const show = true; // for debugging

function MessageBox() {
  const {
    messages,
    messageBoxMinimized,
    setMessageBoxMinimized,
    notifications,
    setNotifications,
  } = useContext(GlobalContext);

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

  function handleMinimization() {
    setNotifications(0);
    setMessageBoxMinimized((previousMinimizedValue) => !previousMinimizedValue);
  }

  const minimizeStyle = {
    filter:
      "invert(15%) sepia(88%) saturate(7485%) hue-rotate(332deg) brightness(93%) contrast(107%)", // what in the
    width: "20px",
  };

  return show ? (
    <>
      <button
        onClick={handleMinimization}
        className={`message-minimize ${messageBoxMinimized ? "minimized" : ""
          }`}
      >
        <div
          key={notifications}
          style={{
            display: notifications && messageBoxMinimized ? "block" : "none",
          }}
          className="notification"
        >
          {notifications >= 9 ? "9+" : notifications}
        </div>
        {messageBoxMinimized ? (
          // workaround for array of styles. refer to https://github.com/necolas/react-native-web/issues/954, applies for react and chrome
          <img
            style={Object.assign(minimizeStyle, {
              transform: "rotateZ(180deg)",
            })}
            src="https://www.svgrepo.com/show/12644/arrow-down-angle.svg"
            alt="arrow up"
          />
        ) : (
          <img
            style={minimizeStyle}
            src="https://www.svgrepo.com/show/12644/arrow-down-angle.svg"
            alt="arrow down"
          />
        )}
      </button>
      <div hidden={messageBoxMinimized}>
        <div ref={messageBox} className="messages-container">
          {messages.map(message => (
            <div key={message.id} className="message-container">
              {message.type === "message" ? (
                <UserAvatar username={message.author} />
              ) : null}
              <div className="message-content">
                <span className="message-author">{message.author}</span>
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
      </div>
    </>
  ) : null;
}

export default MessageBox;
