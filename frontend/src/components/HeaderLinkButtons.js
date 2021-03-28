import { useContext } from "react";

import Button from "@material-ui/core/Button";
import ViewWeekIcon from "@material-ui/icons/ViewWeek";
import GitHubIcon from "@material-ui/icons/GitHub";
import PeopleAltIcon from "@material-ui/icons/PeopleAlt";

import { GlobalContext } from "./GlobalContext";

import "./HeaderLinkButtons.css";

function HeaderLinkButtons() {
    const { latency, onlineUsers } = useContext(GlobalContext);

    function onClickLink(link) {
        window.open(link);
    }

    // todo online users on click button -> show al ist of avatar/usernames (and x randoms not logged in)

    return (
        <div className="link-buttons-container">
            {latency ? <div className="latency">{latency} ms</div> : null}

            {onlineUsers ? (
                <div className="link-button">
                    <Button variant="contained" startIcon={<PeopleAltIcon />}>
                        {onlineUsers.user_count} online
                    </Button>
                </div>
            ) : (
                "onlineUsers state broken"
            )}

            <div className="link-button">
                <Button
                    variant="contained"
                    onClick={() =>
                        onClickLink("https://github.com/julianib/shove")
                    }
                >
                    <GitHubIcon />
                </Button>
            </div>

            <div className="link-button">
                <Button
                    variant="contained"
                    startIcon={<ViewWeekIcon />}
                    onClick={() =>
                        onClickLink("https://trello.com/b/n23X0GGq/shove")
                    }
                >
                    Trello
                </Button>
            </div>
        </div>
    );
}

export default HeaderLinkButtons;
