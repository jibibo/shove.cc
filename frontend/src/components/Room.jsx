import "./Room.css";

function Room() {
    return (
        <div className="table">
            <div className="players">
                <div className="player player-1"></div>
                <div className="player player-2"></div>
                <div className="player player-3"></div>
                <div className="player player-4"></div>
                <div className="player player-5"></div>
                <div className="player player-6"></div>
                <div className="player player-7"></div>
                <div className="player player-8"></div>
                <div className="player player-9"></div>
                <div className="player player-10"></div>
            </div>
            <img src="./games/holdem/table.png" />
        </div>
    )
}

export default Room;
