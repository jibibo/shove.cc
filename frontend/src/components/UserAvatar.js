import Avatar from "@material-ui/core/Avatar";
import Tooltip from "@material-ui/core/Tooltip";
import { makeStyles } from "@material-ui/core/styles";

import { thousandsSeperatorFull } from "../formatting";

import { GlobalContext } from "./GlobalContext";
import { useContext } from "react";

const useStyles = makeStyles((theme) => ({
  root: {
    cursor: "pointer",
    border: "solid 2px #f50057",
  },
}));
// {`https://shove.cc:777/avatars/${username}.png`}

function UserAvatar({ username, money }) {
  const { accountList } = useContext(GlobalContext);
  const classes = useStyles();

  // URL.createObjectURL(
  //   new Blob([account.avatar], { type: "image/png" })
  // );

  const account = accountList.find((account) => {
    if (account.username === username) {
      return account;
    }
    return null;
  });

  return money !== undefined ? (
    <Tooltip title={`$${thousandsSeperatorFull(money)}`} arrow>
      <Avatar className={classes.root} src={account.avatar} />
    </Tooltip>
  ) : (
    <Avatar className={classes.root} src={account.avatar} />
  );
}

export default UserAvatar;
