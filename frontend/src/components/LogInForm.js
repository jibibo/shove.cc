import { useState, useContext } from "react";

import { sendPacket, socket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import "./LoginForm.css";

let deaf = true;

const LogInForm = () => {
    const { setUser } = useContext(GlobalContext);

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    function onSubmit(ev) {
        ev.preventDefault();
        sendPacket("log_in", {
            username: username,
            password: null,
        });
        setUsername("");
    }

    if (deaf) {
        deaf = false;

        socket.on("log_in_status", (packet) => {
            console.debug("> LogInForm log_in_status", packet);
            if (packet["success"]) {
                setUser(packet["username"]);
            }
        });
    }

    return (
        <div className="log-in-form">
            <form onSubmit={onSubmit}>
                <input
                    autoFocus
                    type="text"
                    id="log-in-username"
                    placeholder="Username"
                    autoComplete="off"
                    value={username}
                    onChange={(ev) => {
                        setUsername(ev.target.value);
                    }}
                />
                <input
                    type="password"
                    id="log-in-password"
                    placeholder="Password"
                    autoComplete="off"
                    value={password}
                    onChange={(ev) => {
                        setPassword(ev.target.value);
                    }}
                />
                <input type="submit" value="Submit" />
            </form>
        </div>
    );
};

export default LogInForm;
