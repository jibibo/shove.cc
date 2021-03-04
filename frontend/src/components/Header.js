import { useContext } from "react";

import { UserContext } from "./UserContext";

function Header() {

    const { user } = useContext(UserContext);

    return <div onClick={() => user.setUsername("not julian")} className="header">logged in as: {user.username}</div>;
}

export default Header;
