import { useState, useEffect, useContext } from "react";

import { initSocket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import LogInForm from "./components/LogInForm";
import RoomsList from "./components/RoomsList";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

import "./App.css";
import Room from "./components/Room";

function App() {
    const [width, setWidth] = useState(window.innerWidth);
    const [height, setHeight] = useState(window.innerHeight);

    useEffect(() => {
        window.addEventListener("resize", () => {
            setWidth(window.innerWidth);
            setHeight(window.innerHeight);
        });
    });

    const { user, room } = useContext(GlobalContext);
    initSocket();
    return (
        <>
            <Header />

            <div className="container">
                {width / height < 2 && width < 600 ? "ROTATE PHONE 😡" : null}

                <div>
                    <ConnectionStatus />
                    {user ? null : <LogInForm />}

                    {room ? <Room /> : <RoomsList />}

                    <MessageBox />
                </div>
            </div>
        </>
    );
}

export default App;
