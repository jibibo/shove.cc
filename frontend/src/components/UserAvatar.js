import Avatar from "@material-ui/core/Avatar";
import Tooltip from "@material-ui/core/Tooltip";
import { makeStyles } from "@material-ui/core/styles";

import { thousandsSeperatorFull } from "../formatting";

const useStyles = makeStyles((theme) => ({
  root: {
    cursor: "pointer",
    border: "solid 2px #f50057"
  },
}));

function UserAvatar({ username, money }) {
  const classes = useStyles();

  return money !== undefined ? (
    <Tooltip title={`$${thousandsSeperatorFull(money)}`} arrow>
      <Avatar className={classes.root} src={`avatars/${username}.png`} />
    </Tooltip>
  ) : (
    <Avatar className={classes.root} src={`avatars/${username}.png`} />
  );
}

export default UserAvatar;
