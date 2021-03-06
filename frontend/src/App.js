import { useContext } from "react";

import { initSocket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import LogInForm from "./components/LogInForm";
import JoinRoomForm from "./components/JoinRoomForm";
import RoomsList from "./components/RoomsList";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

import "./index.css";

function App() {
    const { user, room } = useContext(GlobalContext);
    initSocket();

    return (
        <>
        <Header />
        <div className="container">
            <div>
                <ConnectionStatus />

                {!user ? <LogInForm /> : ""}

                {!room ? (
                    <>
                        <RoomsList />
                        <JoinRoomForm />
                    </>
                ) : (
                    ""
                )}
                <br />
                <MessageBox />

                {/* {card ? <img alt="jc" src={`./games/holdem/${card}.svg`} /> : ""} */}
            </div>
        </div>
        </>
    );
}

export default App;
