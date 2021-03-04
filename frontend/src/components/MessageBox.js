import { useState } from "react";

import Message from "./Message";

let addMessageHandler;

function MessageBox() {
    return (
        <>
            Messages:
            <div id="message-box"></div>
        </>
    );
}

function addMessage(text, style) {
    let newMessage = <Message text={text} style={style} />;
    let element = document.createElement("p");
    let list = document.getElementById("message-box");
    if (list !== null) {
        list.insertBefore(element, list.firstChild);
        element.innerHTML = text;
    }
    console.debug("Added message:", text);
}

export { MessageBox, addMessage };
