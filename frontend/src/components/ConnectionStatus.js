import { useState } from "react";

import { makeStyles } from "@material-ui/core/styles";

import { socket } from "../connection";

const useStyles = makeStyles((theme) => ({
    status: {
        padding: "10px",
        borderRadius: "10px 0px 0px",
        texAlign: "center",
    },
}));

let deaf = true;

function ConnectionStatus() {
    const [status, setStatus] = useState();
    const [visible, setVisible] = useState(false);

    const classes = useStyles();

    function popup(text, color) {
        setStatus({
            text,
            color,
        });
        setVisible(true);
        setTimeout(() => {
            // this should be cancelled when popup() gets called again, as it will vanish too quickly
            setVisible(false);
        }, 2000);
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
            style={{ backgroundColor: status.color }}
            className={classes.status}
            hidden={!visible}
        >
            Connection status: {status.text}
        </div>
    ) : null;
}

export default ConnectionStatus;
