import { useState } from "react";

import { initSocket, sendPacket } from "./connection";

import { WebsiteStatus } from "./components/WebsiteStatus";
import RegisterForm from "./components/RegisterForm";
import LogInForm from "./components/LogInForm";
import JoinRoomForm from "./components/JoinRoomForm";
import RoomsList from "./components/RoomsList";
import Message from "./components/Message";
import { MessageBox } from "./components/MessageBox";
import Header from "./components/Header";

function App() {
    const [card, setCard] = useState();
    const [username, setUsername] = useState();
    console.log("App() called");
    initSocket();

    return (
        <div className="container">
            <Header />
            <WebsiteStatus />
            {username ? "" : <RegisterForm />}
            {username ? "" : <LogInForm />}

            <RoomsList />
            <JoinRoomForm />
            <button>fuck off</button>
            <br />
            <MessageBox />

            {card ? <img alt="jc" src={`./games/holdem/${card}.svg`} /> : ""}
        </div>
    );
}

export default App;
