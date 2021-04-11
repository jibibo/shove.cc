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
      <div className="log-in-form-container">
        <h3>LOGIN</h3>
        <div className="form">
          <form onSubmit={onSubmit}>
            <label className="log-in-username-label">Username</label>
            <br />
            <input
              autoFocus
              type="text"
              id="log-in-username"
              autoComplete="off"
              spellCheck={false}
              value={usernameInput}
              onChange={(ev) => {
                setUsernameInput(ev.target.value);
              }}
            />
            <br />
            <label className="log-in-password-label">Password</label>
            <br />
            <input
              type="password"
              id="log-in-password"
              autoComplete="off"
              value={passwordInput}
              onChange={(ev) => {
                setPasswordInput(ev.target.value);
              }}
            />
            <br />
            <Button
              className="log-in-button"
              color="secondary"
              variant="outlined"
              type="submit"
            >
              Log in
            </Button>
          </form>
        </div>
      </div>
      <div className="accounts-container">
        <h3>QUICK LOG IN</h3>
        <div className="account-list">
          {accountList
            ? accountList.map((account, i) => {
                return (
                  <div className="account-list-entry" key={i}>
                    <Button
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        width: 150,
                        color: "white",
                        backgroundColor: "rgb(7, 7, 31)",
                      }}
                      variant="contained"
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
