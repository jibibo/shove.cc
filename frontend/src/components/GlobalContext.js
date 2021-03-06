import { useState, createContext } from "react";

const GlobalContext = createContext();

function GlobalContextProvider({ children }) {
    const [user, setUser] = useState("");
    const [room, setRoom] = useState();
    const [messages, setMessages] = useState([]);

    return (
        <GlobalContext.Provider
            value={{ user, setUser, room, setRoom, messages, setMessages }}
        >
            {children}
        </GlobalContext.Provider>
    );
}

export { GlobalContext, GlobalContextProvider };
