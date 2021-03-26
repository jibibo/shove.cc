import { useState, createContext } from "react";

const GlobalContext = createContext();

function GlobalContextProvider({ children }) {
    const [accountData, setAccountData] = useState();
    const [accountList, setAccountList] = useState([]);
    const [gameData, setGameData] = useState();
    const [messages, setMessages] = useState([]);
    const [ping, setPing] = useState(0);
    const [roomData, setRoomData] = useState();
    const [roomList, setRoomList] = useState([]);
    const [userCount, setUserCount] = useState(0);

    return (
        <GlobalContext.Provider
            value={{
                accountData,
                setAccountData,
                accountList,
                setAccountList,
                gameData,
                setGameData,
                messages,
                setMessages,
                ping,
                setPing,
                roomData,
                setRoomData,
                roomList,
                setRoomList,
                userCount,
                setUserCount,
            }}
        >
            {children}
        </GlobalContext.Provider>
    );
}

export { GlobalContext, GlobalContextProvider };
