import { useContext } from "react";

import { initSocket, socket, sendPacket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import LogInForm from "./components/LogInForm";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

import "./App.css";
import Room from "./components/CoinflipRoom";

let deaf = true;

function App() {
    const {
        accountData,
        setAccountData,
        setAccountList,
        setGameData,
        setMessages,
        setPing,
        roomData,
        setRoomData,
        setRoomList,
        setUserCount,
    } = useContext(GlobalContext);

    // const [width, setWidth] = useState(window.innerWidth);
    // const [height, setHeight] = useState(window.innerHeight);

    // useEffect(() => {
    //     window.addEventListener("resize", () => {
    //         setWidth(window.innerWidth);
    //         setHeight(window.innerHeight);
    //     });
    // });

    function addMessage(author, text) {
        setMessages((currentState) => [
            ...currentState,
            {
                author,
                text,
            },
        ]);
    }

    if (deaf) {
        deaf = false;
        initSocket();

        socket.on("connect", () => {
            console.debug("> App > connect event");
            sendPacket("get_room_list", {});
            sendPacket("get_account_list", {});
        });

        socket.on("connect_error", () => {
            console.warn("> App > connect_error event");
        });

        socket.on("disconnect", (reason) => {
            console.warn("> App > disconnect event", reason);
            setAccountData();
            setRoomData();
            setGameData();
        });

        socket.on("account_data", (packet) => {
            console.debug("> App > account_data", packet);
            // if receiving other user's account data, do not call setAccountData!
            setAccountData(packet);
        });

        socket.on("account_list", (packet) => {
            console.debug("> App > account_list", packet);
            setAccountList(packet.account_list);
        });

        socket.on("command_success", (packet) => {
            console.debug("> App > command_success", packet);
            addMessage("Command success", packet.response);
        });

        socket.on("error", (packet) => {
            console.error("> App > error", packet);
            addMessage("Error", packet.description);
        });

        socket.on("join_room", (packet) => {
            console.debug("> App > join_room", packet);
            addMessage("Joined room " + packet.room_data.name);
            setRoomData(packet.room_data);
            setGameData(packet.game_data);
        });

        socket.on("leave_room", (packet) => {
            console.debug("> App > leave_room", packet);
            addMessage("Left room " + packet.room_name);
            setRoomData();
            setGameData();
        });

        socket.on("log_in", (packet) => {
            console.debug("> App > log_in", packet);
            addMessage("Logged in as " + packet.account_data.username);
            setAccountData(packet.account_data);
        });

        socket.on("log_out", (packet) => {
            console.debug("> App > log_out", packet);
            addMessage("Logged out");
            setAccountData();
            setRoomData();
            setGameData();
        });

        socket.on("message", (packet) => {
            console.debug("> App > message", packet);
            addMessage(packet.author, packet.text);
        });

        socket.on("ping", (packet) => {
            console.debug("> App > ping", packet);
            sendPacket("pong", {});
            const ping = Date.now() - packet.timestamp;
            setPing(ping);
        });

        socket.on("room_list", (packet) => {
            console.debug("> App > room_list", packet);
            setRoomList(packet.room_list);
        });

        socket.on("user_connected", (packet) => {
            console.debug("> App > user_connected", packet);
            setUserCount(packet.user_count);

            if (packet.you) {
                addMessage("Connected!");
            } else {
                addMessage("Someone connected");
            }
        });

        socket.on("user_disconnected", (packet) => {
            console.debug("> App > user_disconnected", packet);
            setUserCount(packet.user_count);

            if (packet.username) {
                addMessage(packet.username + " disconnected");
            } else {
                addMessage("Someone disconnected");
            }
        });
    }

    return (
        <>
            <Header />

            <div className="container">
                {/* {width / height < 2 && width < 600 ? "ROTATE PHONE 😡" : null} */}

                <div>
                    {accountData?.username ? (
                        roomData?.name ? (
                            <Room />
                        ) : (
                            "join a room yh?"
                        )
                    ) : (
                        <LogInForm />
                    )}
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
