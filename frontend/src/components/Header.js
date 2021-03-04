import { useContext } from "react";

import { UserContext } from "./UserContext";

function Header() {

    const [ username, _ ] = useContext(UserContext);

    return <div onClick={() => _("not julian")} className="header">logged in as: {username}</div>;
}

export default Header;
