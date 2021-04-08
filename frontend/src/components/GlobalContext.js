import { useState, createContext } from "react";

const GlobalContext = createContext();

function GlobalContextProvider({ children }) {
  const [accountData, setAccountData] = useState();
  const [accountList, setAccountList] = useState([]);
  const [gameData, setGameData] = useState();
  const [messages, setMessages] = useState([]);
  const [latency, setLatency] = useState(0);
  const [onlineUsers, setOnlineUsers] = useState({});
  const [roomData, setRoomData] = useState();
  const [roomList, setRoomList] = useState([]);

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
        latency,
        setLatency,
        onlineUsers,
        setOnlineUsers,
        roomData,
        setRoomData,
        roomList,
        setRoomList,
      }}
    >
      {children}
    </GlobalContext.Provider>
  );
}

export { GlobalContext, GlobalContextProvider };
