import { useContext } from "react";

import { UserContext } from "./UserContext";

import "./Header.css";

function Header() {

    const { user } = useContext(UserContext);

    return (
        <header>
            <div>
                <h3>Logged in as: <b>{user.username}</b></h3>
            </div>
            <div>
                <button className="header-button">{user.username ? "Log out" : "Log in"}</button>
            </div>
        </header>
    );
}

export default Header;
