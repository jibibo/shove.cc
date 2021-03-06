import { useContext } from "react";

import { GlobalContext } from "./GlobalContext";

import "./Header.css";

function Header() {
    const { user, room } = useContext(GlobalContext);

    return (
        <header>
            <div>
                <h3>
                    Logged in as: <b>{user}</b>
                </h3>
                <h3>
                    Currently in room: <b>{room}</b>
                </h3>
            </div>
            <div>
                <button className="header-button">
                    {user ? "Log out" : "Log in"}
                </button>
            </div>
        </header>
    );
}

export default Header;
