import { useState, useContext } from "react";
import Button from "@material-ui/core/Button";

import { sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import "./LogInForm.css";

const LogInForm = () => {
    const { accountList } = useContext(GlobalContext);

    const [usernameInput, setUsernameInput] = useState("");
    const [passwordInput, setPasswordInput] = useState("");

    function onClickAccount(username) {
        sendPacket("log_in", {
            username,
            password: null,
        });
    }

    function onSubmit(ev) {
        ev.preventDefault();
        sendPacket("log_in", {
            username: usernameInput,
            password: passwordInput,
        });
        setUsernameInput("");
    }

    return (
        <>
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
                    <Button variant="contained" type="submit">
                        Log in
                    </Button>
                </form>
            </div>
            <div className="account-list">
                One click log-in
                {accountList.map((account, i) => {
                    return (
                        <div className="account-list-entry" key={i}>
                            <Button
                                variant="contained"
                                onClick={() => {
                                    onClickAccount(account.username);
                                }}
                            >
                                {account.username}
                            </Button>
                        </div>
                    );
                })}
            </div>
        </>
    );
};

export default LogInForm;
