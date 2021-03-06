import { useState, useEffect, useContext } from "react";

import { initSocket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import LogInForm from "./components/LogInForm";
import JoinRoomForm from "./components/JoinRoomForm";
import RoomsList from "./components/RoomsList";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

import "./index.css";
import Room from "./components/Room";

function App() {

    const [ width, setWidth ] = useState(window.innerWidth);

    useEffect(() => {
        window.addEventListener("resize", () => {
            setWidth(window.innerWidth);
        })
    })
    
    const { user, room } = useContext(GlobalContext);
    initSocket();
    return (
        <>
        <Header />
        <div className="container">
            {
                width < 650 ? "ROTATE YOUR PHONE! 😡" :
                (
                    <Room />
                )
            }
            <div>
                <ConnectionStatus />

                {!user ? <LogInForm /> : ""}

                {!room ? (
                    <>
                        <RoomsList />
                        <JoinRoomForm />
                    </>
                ) : null }
                <MessageBox/>

                {/* {card ? <img alt="jc" src={`./games/holdem/${card}.svg`} /> : ""} */}
            </div>
        </div>
        </>
    );
}

export default App;
