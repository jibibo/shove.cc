import { useState, createContext } from "react";

const GlobalContext = createContext();

function GlobalContextProvider({ children }) {
    const [messages, setMessages] = useState([]);
    const [money, setMoney] = useState();
    const [room, setRoom] = useState();
    const [user, setUser] = useState();

    return (
        <GlobalContext.Provider
            value={{
                messages,
                setMessages,
                money,
                setMoney,
                room,
                setRoom,
                user,
                setUser,
            }}
        >
            {children}
        </GlobalContext.Provider>
    );
}

export { GlobalContext, GlobalContextProvider };
