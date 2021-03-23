import { useState, useEffect, useContext } from "react";

import { initSocket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import LogInForm from "./components/LogInForm";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

import "./App.css";
import Room from "./components/CoinflipRoom";

function App() {
    const [width, setWidth] = useState(window.innerWidth);
    const [height, setHeight] = useState(window.innerHeight);
    const { accountData, roomName } = useContext(GlobalContext);

    useEffect(() => {
        window.addEventListener("resize", () => {
            setWidth(window.innerWidth);
            setHeight(window.innerHeight);
        });
    });

    initSocket();

    return (
        <>
            <Header />

            <div className="container">
                {width / height < 2 && width < 600 ? "ROTATE PHONE 😡" : null}

                <div>
                    {accountData.username ? null : <LogInForm />}

                    {roomName ? <Room /> : "join a room yh?"}
                </div>
                <div className="message-box-container">
                    <MessageBox />
                </div>

                <div className="connection-status-container">
                    <ConnectionStatus />
                </div>
            </div>
        </>
    );
}

export default App;
