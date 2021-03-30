import Avatar from "@material-ui/core/Avatar";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
    root: {
        cursor: "pointer",
    },
}));

function UserAvatar({ username }) {
    const classes = useStyles();

    return <Avatar className={classes.root} src={`avatars/${username}.png`} />;
}

export default UserAvatar;
