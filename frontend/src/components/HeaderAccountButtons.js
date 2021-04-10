import { useContext } from "react";

import Button from "@material-ui/core/Button";
import ExitToApp from "@material-ui/icons/ExitToApp";

import { sendPacket } from "../connection";
import { abbreviate } from "../formatting";
import { GlobalContext } from "./GlobalContext";
import UserAvatar from "./UserAvatar";

import "./HeaderAccountButtons.css";

function HeaderAccountButtons() {
  const { accountData } = useContext(GlobalContext);

  function onClickLogOut() {
    sendPacket("log_out");
  }
  return (
    <div className="account-buttons-container">
      <div className="account-button">
        <UserAvatar
          username={accountData.username}
          money={accountData.money}
        />
      </div>
      <div className="account-button">
        <Button
          variant="outlined"
          color="secondary"
          startIcon={<ExitToApp />}
          onClick={onClickLogOut}
        >
          Log out
        </Button>
      </div>
    </div>
  );
}

export default HeaderAccountButtons;
