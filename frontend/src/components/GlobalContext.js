import { useState, createContext } from "react";

const GlobalContext = createContext();

// this is a comment

function GlobalContextProvider({ children }) {
  const [accountData, setAccountData] = useState();
  const [accountList, setAccountList] = useState([]);
  const [gameData, setGameData] = useState();
  const [messages, setMessages] = useState([]);
  const [notifications, setNotifications] = useState(0);
  const [messageBoxMinimized, setMessageBoxMinimized] = useState(1);
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
        messageBoxMinimized,
        setMessageBoxMinimized,
        notifications,
        setNotifications,
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
