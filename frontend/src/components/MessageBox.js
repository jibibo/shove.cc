// import { useState } from "react";

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
    let element = document.createElement("p");
    let list = document.getElementById("message-box");
    if (list !== null) {
        list.insertBefore(element, list.firstChild);
        element.innerHTML = text;
    }
    console.debug("Added message:", text);
}

export { MessageBox, addMessage };
