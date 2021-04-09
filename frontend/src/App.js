import { useContext } from "react";

import Container from "@material-ui/core/Container";

import { initSocket, socket, sendPacket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import LogInForm from "./components/LogInForm";
import MessageBox from "./components/MessageBox";
import Header from "./components/Header";

import "./App.css";
import Room from "./components/CoinflipRoom";
import AudioPlayer from "./components/AudioPlayer";

let deaf = true;

function App() {
  const {
    accountData,
    setAccountData,
    setAccountList,
    setGameData,
    setMessages,
    setLatency,
    setOnlineUsers,
    roomData,
    setRoomData,
    setRoomList,
  } = useContext(GlobalContext);

  // const [width, setWidth] = useState(window.innerWidth);
  // const [height, setHeight] = useState(window.innerHeight);

  // useEffect(() => {
  //     window.addEventListener("resize", () => {
  //         setWidth(window.innerWidth);
  //         setHeight(window.innerHeight);
  //     });
  // });

  function addMessage(type, author, text) {
    setMessages((currentMessages) => {
      // todo broken
      // const maxMessages = 5;
      // if (currentMessages.length > maxMessages) {
      //     let splicedMessages = [...currentMessages];
      //     splicedMessages.splice(0, currentMessages.length - maxMessages);
      //     return [
      //         ...splicedMessages,
      //         {
      //             author,
      //             text,
      //         },
      //     ];
      // } else {
      //     return [
      //         ...currentMessages,
      //         {
      //             author,
      //             text,
      //         },
      //     ];
      // }
      return [
        ...currentMessages,
        {
          type,
          author,
          text,
        },
      ];
    });
  }

  if (deaf) {
    // todo memory leak: listeners dont get removed
    // todo socket listeners shouldn't be stacked in App.js, but the specific file they belong to
    deaf = false;
    initSocket();

    // socket events

    socket.on("connect", () => {
      console.debug("> connect event");
    });

    socket.on("connect_error", () => {
      console.warn("> connect_error event");
    });

    socket.on("disconnect", (reason) => {
      console.warn("> disconnect event", reason);
      setAccountData();
      setRoomData();
      setGameData();
    });

    // packet handlers

    socket.on("account_data", (packet) => {
      console.debug("> account_data", packet);
      // if receiving other user's account data, do not call setAccountData!
      setAccountData(packet);
    });

    socket.on("account_list", (packet) => {
      console.debug("> account_list", packet);
      setAccountList(packet);
    });

    socket.on("command_success", (packet) => {
      console.debug("> command_success", packet);
      addMessage(null, "Command success", packet.response);
    });

    socket.on("error", (packet) => {
      console.error("> error", packet);
      addMessage(null, "Error", packet.description);
    });

    socket.on("join_room", (packet) => {
      console.debug("> join_room", packet);
      addMessage(null, "Joined room " + packet.room_data.name, null);
      setRoomData(packet.room_data);
      setGameData(packet.game_data);
    });

    socket.on("latency", (packet) => {
      console.debug("> latency", packet);
      setLatency(packet.latency);
    });

    socket.on("leave_room", (packet) => {
      console.debug("> leave_room", packet);
      addMessage(null, "Left room " + packet.room_name, null);
      setRoomData();
      setGameData();
    });

    socket.on("log_in", (packet) => {
      console.debug("> log_in", packet);
      addMessage(null, "Logged in as " + packet.account_data.username, null);
      setAccountData(packet.account_data);
    });

    socket.on("log_out", (packet) => {
      console.debug("> log_out", packet);
      addMessage(null, "Logged out", null);
      setAccountData();
      setRoomData();
      setGameData();
    });

    socket.on("message", (packet) => {
      console.debug("> message", packet);
      addMessage("message", packet.author, packet.text);
    });

    socket.on("ping", (packet) => {
      console.debug("> ping", packet);
      sendPacket("pong");
    });

    socket.on("room_list", (packet) => {
      console.debug("> room_list", packet);
      setRoomList(packet);
    });

    socket.on("song_like", (packet) => {
      console.debug("> song_like", packet);
      addMessage(null, null, "You liked " + packet.song_name);
    });

    socket.on("song_dislike", (packet) => {
      console.debug("> song_dislike", packet);
      addMessage(null, null, "You disliked " + packet.song_name);
    });

    socket.on("user_connected", (packet) => {
      console.debug("> user_connected", packet);
      setOnlineUsers({
        users: packet.users,
        user_count: packet.user_count,
      });

      if (packet.you) {
        addMessage(null, "Connected!", null);
      } else {
        addMessage(null, "Someone connected", null);
      }
    });

    socket.on("user_disconnected", (packet) => {
      console.debug("> user_disconnected", packet);
      setOnlineUsers({
        users: packet.users,
        user_count: packet.user_count,
      });

      if (packet.username) {
        addMessage(null, packet.username + " disconnected", null);
      } else {
        addMessage(null, "Someone nameless disconnected", null);
      }
    });
  }

  return (
    <Container>
      <Header />

      <div>
        {/* {width / height < 2 && width < 600 ? "ROTATE PHONE 😡" : null} */}

        <div>
          {accountData ? (
            roomData ? (
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
        <AudioPlayer />
      </div>
    </Container>
  );
}

export default App;
