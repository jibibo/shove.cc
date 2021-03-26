import { useContext } from "react";

import Button from "@material-ui/core/Button";
import ViewWeekIcon from "@material-ui/icons/ViewWeek";
import GitHubIcon from "@material-ui/icons/GitHub";

import { GlobalContext } from "./GlobalContext";

import "./HeaderLinkButtons.css";

function HeaderLinkButtons() {
    const { latency } = useContext(GlobalContext);

    function onClickLink(link) {
        window.open(link);
    }

    return (
        <div className="link-buttons-container">
            {latency ? <span className="latency">{latency} ms</span> : null}
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
        </div>
    );
}

export default HeaderLinkButtons;
