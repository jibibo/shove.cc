import { useState, useContext } from "react";

import { initSocket, sendPacket } from "./connection";

import { UserContext } from "./components/UserContext";

import { WebsiteStatus } from "./components/WebsiteStatus";
import RegisterForm from "./components/RegisterForm";
import LogInForm from "./components/LogInForm";
import JoinRoomForm from "./components/JoinRoomForm";
import RoomsList from "./components/RoomsList";
// import Message from "./components/Message";
// import { MessageBox } from "./components/MessageBox";
import Header from "./components/Header";

function App() {
    const [card, setCard] = useState();
    const [username, setUsername] = useContext(UserContext);
    console.log("App() called");
    initSocket();

    return (
        <div className="container">
            <Header />
            <WebsiteStatus />
            
            <RoomsList />
            <JoinRoomForm />
            <button onClick={() => setUsername("julian")}>sign in yh? {username}</button>
            <br />
            {/* <MessageBox /> */}

            {card ? <img alt="jc" src={`./games/holdem/${card}.svg`} /> : ""}
        </div>
    );
}

export default App;
