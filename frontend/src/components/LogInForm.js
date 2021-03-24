import { useState } from "react";

import { sendPacket } from "../connection";

import "./LoginForm.css";

const LogInForm = () => {
    const [usernameInput, setUsernameInput] = useState("");
    const [passwordInput, setPasswordInput] = useState("");

    function onSubmit(ev) {
        ev.preventDefault();
        sendPacket("log_in", {
            username: usernameInput,
            password: passwordInput,
        });
        setUsernameInput("");
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
                    value={usernameInput}
                    onChange={(ev) => {
                        setUsernameInput(ev.target.value);
                    }}
                />
                <input
                    type="password"
                    id="log-in-password"
                    placeholder="Password"
                    autoComplete="off"
                    value={passwordInput}
                    onChange={(ev) => {
                        setPasswordInput(ev.target.value);
                    }}
                />
                <button className="login-button" type="submit">
                    Submit
                </button>
            </form>
        </div>
    );
};

export default LogInForm;
