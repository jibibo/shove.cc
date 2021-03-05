import { useState, useContext } from "react";

import { InitSocket, sendPacket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import WebsiteStatus from "./components/WebsiteStatus";
import RegisterForm from "./components/RegisterForm";
import LogInForm from "./components/LogInForm";
import JoinRoomForm from "./components/JoinRoomForm";
import RoomsList from "./components/RoomsList";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

function App() {
    const [card, setCard] = useState();
    const { user, setUser } = useContext(GlobalContext);
    console.log("App() called");
    InitSocket();

    console.log(useContext(GlobalContext));

    return (
        <div>
            <Header />
            <WebsiteStatus />

            <RoomsList />
            <JoinRoomForm />
            <button onClick={() => setUser("julian")}>
                sign in yh? {user}
            </button>
            <br />
            <MessageBox />

            {card ? <img alt="jc" src={`./games/holdem/${card}.svg`} /> : ""}
        </div>
    );
}

export default App;
