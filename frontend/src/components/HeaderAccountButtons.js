import { useContext } from "react";

import Button from "@material-ui/core/Button";
import Tooltip from "@material-ui/core/Tooltip";
import ExitToApp from "@material-ui/icons/ExitToApp";
import AccountCircleIcon from "@material-ui/icons/AccountCircle";

import { sendPacket } from "../connection";
import { abbreviate, thousandsSeperatorFull } from "../formatting";
import { GlobalContext } from "./GlobalContext";

import "./HeaderAccountButtons.css";

function HeaderAccountButtons() {
    const { accountData } = useContext(GlobalContext);

    function onClickLogOut() {
        sendPacket("log_out", {});
    }
    return (
        <div className="account-buttons-container">
            <div className="account-button">
                <Tooltip
                    title={`$${thousandsSeperatorFull(accountData.money)}`}
                    arrow
                >
                    <Button
                        variant="contained"
                        startIcon={<AccountCircleIcon />}
                        onClick={onClickLogOut}
                    >
                        {`${accountData.username} | $${abbreviate( // todo add divider here
                            accountData.money
                        )}`}
                    </Button>
                </Tooltip>
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
