import { useContext } from "react";

import { GlobalContext } from "./GlobalContext";
import HeaderRoomButtons from "./HeaderRoomButtons";
import HeaderAccountButtons from "./HeaderAccountButtons";

import "./Header.css";
import HeaderLinkButtons from "./HeaderLinkButtons";
import Container from "@material-ui/core/Container";
import Typography from "@material-ui/core/Typography";

function Header() {
  const { accountData } = useContext(GlobalContext);

  // 625 is when it breaks 
  
  return (
      <header>
        <Container className="header-container">
          <div className="header-child">
          <Typography variant="h4">🎲 Shove</Typography>
            </div>
          {accountData ? (
            <div className="header-child">
            <HeaderAccountButtons />
          </div>
        ) : null}
      </Container>
    </header>
  );
}

export default Header;

{/* <div className="header-child">
<HeaderRoomButtons />
</div>
<div className="header-child">
<HeaderLinkButtons />
</div>
*/}
