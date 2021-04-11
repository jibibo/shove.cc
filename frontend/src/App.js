import { useState, useContext } from "react";

import Container from "@material-ui/core/Container";
import AppBar from "@material-ui/core/AppBar";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";

import { initSocket, socket, sendPacket } from "./connection";

import { GlobalContext } from "./components/GlobalContext";

import ConnectionStatus from "./components/ConnectionStatus";
import LogInForm from "./components/LogInForm";
import MessageBox from "./components/MessageBox";
import HeaderRoomButtons from "./components/HeaderRoomButtons";
import Header from "./components/Header";
import TabPanel from "./components/TabPanel";

import "./App.css";
import Room from "./components/CoinflipRoom";
import AudioPlayer from "./components/AudioPlayer";
import { abbreviate } from "./formatting";

let deaf = true;

function App() {
  const [tabIndex, setTabIndex] = useState(0);

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

  function addMessage(type, author, text) {
    setMessages((currentMessages) => {
      const maxMessages = 20;
      if (currentMessages.length > maxMessages) {
        let slicedMessages = [...currentMessages].slice(-maxMessages); // this will start at -5 index to the latest message of the array
        return [
          ...slicedMessages,
          {
            type,
            author,
            text,
          },
        ];
      }
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
      console.error("> connect_error event");
    });

    socket.on("disconnect", (reason) => {
      console.error("> disconnect event", reason);
      setAccountData();
      setRoomData();
      setGameData();
      setTabIndex(0);
    });

    // packet handlers

    socket.on("account_data", (packet) => {
      console.debug("> account_data", packet);
      // if receiving other user's account data, do not call setAccountData!

      setAccountData(packet);
    });

    socket.on("account_list", (list) => {
      console.debug("> account_list", list);
      const newList = list.map((account) => {
        if (account.avatar_bytes) {
          // for each account, set .avatar property to a URL containing the avatar blob, if avatar is set
          account.avatar = URL.createObjectURL(
            new Blob([account.avatar_bytes], { type: account.avatar_type })
          );
        }
        return account;
      });
      setAccountList(newList);
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
      setTabIndex(2);
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
      setTabIndex(1);
    });

    socket.on("log_in", (packet) => {
      console.debug("> log_in", packet);
      addMessage(null, "Logged in as " + packet.account_data.username, null);
      setAccountData(packet.account_data);
      setTabIndex(1);
    });

    socket.on("log_out", (packet) => {
      console.debug("> log_out", packet);
      addMessage(null, "Logged out", null);
      setAccountData();
      setRoomData();
      setGameData();
      setTabIndex(0);
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
        users_logged_in: packet.users_logged_in,
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

  const handleChange = (event, newValue) => setTabIndex(newValue);

  return (
    <>
      <Header />

      <AppBar style={{ backgroundColor: "rgb(23, 23, 41)" }} position="static">
        <Container>
          <Tabs value={tabIndex} onChange={handleChange}>
            <Tab label="Account" />
            <Tab label="Room List" />
            <Tab label="Room" />
            <Tab label="Music" />
            <Tab label="Settings" />
          </Tabs>
        </Container>
      </AppBar>

      <Container>
        <TabPanel value={tabIndex} index={0}>
          {accountData ? (
            `Logged in as ${accountData.username} with $${abbreviate(
              accountData.money
            )} in the pocket`
          ) : (
            <LogInForm />
          )}
        </TabPanel>

        <TabPanel value={tabIndex} index={1}>
          <HeaderRoomButtons />
        </TabPanel>

        <TabPanel value={tabIndex} index={2}>
          {roomData ? <Room /> : "join a room yh?"}
        </TabPanel>

        <TabPanel value={tabIndex} index={3}>
          <AudioPlayer />
        </TabPanel>
      </Container>

      <div className="message-box-container">
        <MessageBox />
      </div>

      <div className="connection-status-container">
        <ConnectionStatus />
      </div>
    </>
  );
}

export default App;
