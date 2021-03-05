import { useContext } from "react";

import { initSocket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import RegisterForm from "./components/RegisterForm";
import LogInForm from "./components/LogInForm";
import JoinRoomForm from "./components/JoinRoomForm";
import RoomsList from "./components/RoomsList";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

function App() {
    // const [card, setCard] = useState();
    const { user, setUser } = useContext(GlobalContext);
    initSocket();

    return (
        <div>
            <Header />
            <ConnectionStatus />

            {!user ? (
                <>
                    <LogInForm />
                    <RegisterForm />
                </>
            ) : (
                "Signed in as:" + user
            )}

            <RoomsList />
            <JoinRoomForm />
            <button onClick={() => setUser("julian")}>
                sign in yh? {user}
            </button>
            <br />
            <MessageBox />

            {/* {card ? <img alt="jc" src={`./games/holdem/${card}.svg`} /> : ""} */}
        </div>
    );
}

export default App;
