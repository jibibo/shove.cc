import { useContext } from "react";

import { GlobalContext } from "./GlobalContext";
import HeaderRoomButtons from "./HeaderRoomButtons";
import HeaderAccountButtons from "./HeaderAccountButtons";


import "./Header.css";
import HeaderLinkButtons from "./HeaderLinkButtons";

function Header() {
    const { accountData } = useContext(GlobalContext);

    return (
        <header>
            <div className="header-child">
                <HeaderRoomButtons />
            </div>
            <div className="header-child">
                
                <HeaderLinkButtons />
            </div>

            {accountData ? (
                <div className="header-child">
                    <HeaderAccountButtons />
                </div>
            ) : null}
        </header>
    );
}

export default Header;
