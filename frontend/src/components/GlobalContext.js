import { useState, createContext } from "react";

const GlobalContext = createContext();

function GlobalContextProvider({ children }) {
    const [messages, setMessages] = useState([]);
    const [accountData, setAccountData] = useState({
        username: null,
        password: null,
        money: null,
    });
    const [roomName, setRoomName] = useState();

    return (
        <GlobalContext.Provider
            value={{
                accountData,
                setAccountData,
                messages,
                setMessages,
                roomName,
                setRoomName,
            }}
        >
            {children}
        </GlobalContext.Provider>
    );
}

export { GlobalContext, GlobalContextProvider };
