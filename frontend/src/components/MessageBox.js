import { useContext } from "react";
import { GlobalContext } from "./GlobalContext";

function MessageBox() {
    const { messages } = useContext(GlobalContext);
    const messagesMapped = messages.map((message, i) => {
        <p key={i}>{message}</p>;
    });

    return (
        <>
            Messages:
            <div>{messagesMapped}</div>
        </>
    );
}

export default MessageBox;
