import { useState, useContext } from "react";
import Button from "@material-ui/core/Button";
import Avatar from "@material-ui/core/Avatar";

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
    <div className="login-container">
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
      <div class="accounts-container">
        <h3>Quick log in:</h3>
        <div className="account-list">
          {accountList
            ? accountList.map((account, i) => {
              return (
                <div className="account-list-entry" key={i}>
                  <Button
                    style={{ display: "flex", justifyContent: "space-between", width: 150 }}
                    color="secondary"
                    variant="outlined"
                    onClick={() => {
                      onClickAccount(account.username);
                    }}
                  >
                    <Avatar src={`cache/avatars/${account.username}.png`} />
                    {account.username}
                  </Button>
                </div>
              );
            })
            : "No accounts!"}
        </div>
      </div>
    </div>
  );
};

export default LogInForm;
