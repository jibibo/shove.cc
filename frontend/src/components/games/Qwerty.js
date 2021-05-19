import { useState, useContext } from "react";

import { makeStyles } from "@material-ui/core/styles";
import { sendPacket, socket } from "../../connection";
import { GlobalContext } from "../GlobalContext";

const useStyles = makeStyles((theme) => ({
  root: {},
}));

let deaf = true;

function Qwerty() {
  const { accountData, gameData, setGameData } = useContext(GlobalContext);
  const [inputValue, setInputValue] = useState("");

  const classes = useStyles();

  if (deaf) {
    // todo memory leak: listeners dont get removed
    deaf = false;

    socket.on("game_action_success", (packet) => {
      console.debug("> game_action_success", packet);
    });

    socket.on("game_data", (packet) => {
      console.debug("> game_data", packet);
      setGameData(packet);
    });
  }

  function onChangeInput(e) {
    setInputValue(e.target.value);
  }

  function onSubmitInput(e) {
    e.preventDefault();
    sendPacket("game_action", {
      type: "submit_word",
      word: inputValue,
    });
  }

  let words = [];
  if (gameData) {
    if (accountData) {
      words = gameData.player_data[accountData.username].words;
    }
  }

  return gameData ? (
    <div className={classes.root}>
      <ul>{words}</ul>
      <form onSubmit={onSubmitInput}>
        <input value={inputValue} onChange={onChangeInput} />
      </form>
    </div>
  ) : (
    "no game data very bad"
  );
}

export default Qwerty;
