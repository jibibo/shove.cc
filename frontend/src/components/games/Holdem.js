import "./HoldemRoom.css";

function Room() {
  // todo outdated
  const seats = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const communityCards = ["Js", "Jh", "Jc", "Jd", "Ac"];

  return (
    <div className="table no-select">
      <div className="table-elements">
        {communityCards.map((card, i) => {
          return (
            <img
              className={"community-card community-card-" + (i + 1)}
              src={"./games/holdem/cards_small/" + card + ".png"}
              alt="card"
              key={i}
            />
          );
        })}

        {seats.map((seatNumber) => {
          return (
            <div className={"player player-" + seatNumber} key={seatNumber}>
              <img
                className="user-avatar"
                src="./img/avatar.png"
                alt="avatar"
              />
              <div className="hole-cards">
                <img
                  className="hole-card"
                  src="./games/holdem/cards_small/As.png"
                  alt="card"
                />
                <img
                  className="hole-card"
                  src="./games/holdem/cards_small/Ah.png"
                  alt="card"
                />
              </div>
              <span className="username">User_{seatNumber}</span>

              <img
                className="dealer-button"
                src="./games/holdem/dealer_button.svg"
                alt="dealer button"
              />

              <div className={"player-bet player-bet-" + seatNumber}>
                <img
                  className="bet-chip"
                  src="./games/holdem/chip.svg"
                  alt="bet"
                />
                {/* see py test file for working formatting*/}
                <span>9.99M</span>
              </div>
            </div>
          );
        })}

        <div className="pot-text">
          Pots: <b>400</b> <i>200</i> <i>12</i>
        </div>
      </div>
      <img className="table-image" alt="table" src="./games/holdem/table.png" />
    </div>
  );
}

export default Room;
