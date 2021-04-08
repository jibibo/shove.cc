import { useState } from "react";

import { makeStyles } from "@material-ui/core/styles";

import { socket } from "../connection";

const useStyles = makeStyles((theme) => ({
  status: {
    padding: "10px",
    borderRadius: "10px 0px 0px",
    texAlign: "center",
    cursor: "pointer",
  },
}));

let deaf = true;

function ConnectionStatus() {
  const [status, setStatus] = useState();

  const classes = useStyles();

  var removeTimer;

  function removeStatus() {
    clearTimeout(removeTimer);
    setStatus();
  }

  function popup(text, color) {
    clearTimeout(removeTimer);
    setStatus({
      text,
      color,
    });
    removeTimer = setTimeout(removeStatus, 3000);
  }

  if (deaf) {
    deaf = false;

    socket.on("connect", () => {
      popup("connected", "green");
    });

    socket.on("connect_error", () => {
      popup("websocket offline", "darkred");
    });

    socket.on("disconnect", (reason) => {
      popup("disconnected: " + reason, "darkred");
    });
  }

  return status ? (
    <div
      onClick={removeStatus}
      style={{ backgroundColor: status.color }}
      className={classes.status}
    >
      Connection status: {status.text}
    </div>
  ) : null;
}

export default ConnectionStatus;
