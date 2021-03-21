import { useState, useContext } from "react";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import "./CoinflipRoom.css";

let deaf = true;

function Room() {
    const [bet, setBet] = useState(1);
    const [results, setResults] = useState([]);
    const [timeLeft, setTimeLeft] = useState(0);
    const [betters, setBetters] = useState([]);
    const [coin, setCoin] = useState(null);

    const { money, user } = useContext(GlobalContext);

    function addResult(result) {
        setResults((results) => [...results, result]);
    }

    function onBet(choice) {
        sendPacket("game_action", {
            action: "bet",
            choice: choice,
            bet: bet,
        });
    }

    if (deaf) {
        deaf = false;

        sendPacket("game_state", {});

        socket.on("game_action_status", (packet) => {
            console.debug("> CoinflipRoom game_action_status", packet);
            if (packet["success"] && packet["action"] === "bet") {
                addResult(
                    "You bet " + packet["bet"] + " on: " + packet["choice"]
                );
                sendPacket("get_account_data", {
                    username: user,
                });
            }
        });

        socket.on("game_ended", (packet) => {
            console.debug("> CoinflipRoom game_ended", packet);
            addResult("Game ended! Result: " + packet["coin_result"]);
            setCoin(packet.coin_result);
            setTimeLeft("Filipino, winners: " + JSON.stringify(packet["winners"]));
            if (user in packet["winners"]) {
                addResult("You won: gained " + packet["winners"][user]);
                sendPacket("get_account_data", {
                    username: user,
                });
            } else {
                addResult("You lost: gained nothing");
            }
        });

        socket.on("game_state", (packet) => {
            console.debug("> CoinflipRoom game_state", packet);
            setCoin(packet.coin_result);
            if (packet["running"]) {
                setTimeLeft(packet["state"]["time_left"]);
                setBetters(packet["state"]["betters"]);

                if (packet["state"]["just_started"]) {
                    addResult("Coin flip started, coin lands in: " + packet.state.time_left)
                }
            }

            
        });
    }

    return (
        <>
            <div>
                Time before flip: {timeLeft}
                <br />
                {
                    money 
                    ?
                    (
                        <>
                            <input type="range" min="1" max={money} value={bet} step="1" onChange={(e) => setBet(e.target.value)}/>
                            <code>{bet}</code>
                        </>
                    )
                    :
                    null
                }
                <div>
                    { 
                    coin !== null
                     ?
                     (
                        coin === "spinning" ?  
                        <img className="coin spinning" src={`./games/coinflip/spinning.svg`} alt="spinning" />
                          : 
                        <img className="coin" src={`./games/coinflip/${coin}.svg`} alt={`${coin}`} />
                     )
                     :
                     null
                   }
                    
                </div>
                <input
                    type="button"
                    value="Heads"
                    onClick={() => {
                        onBet("heads");
                    }}
                />
                <input
                    type="button"
                    value="Tails"
                    onClick={() => {
                        onBet("tails");
                    }}
                />
                <br />
                Betters:{" "}
                {Object.entries(betters).map(([user, bet]) => {
                    return user + ": " + bet;
                })}
            </div>
            <div>
                {results.map((result, i) => (
                    <div className="result" key={i}>
                        <p>{result}</p>
                    </div>
                ))}
            </div>
        </>
    );
}

export default Room;