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

    const { user } = useContext(GlobalContext);

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
            addResult("Game ended! Result: " + packet["result"]);
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

        socket.on("game_started", (packet) => {
            console.debug("> CoinflipRoom game_started", packet);
            setTimeLeft(packet["time_left"]);
            setBetters(packet["betters"]);
        });

        socket.on("game_state", (packet) => {
            console.debug("> CoinflipRoom game_state", packet);
            setTimeLeft(packet["time_left"]);
            setBetters(packet["betters"]);
        });
    }

    return (
        <>
            <div>
                Time before flip: {timeLeft}
                <br />
                <input
                    type="number"
                    value={bet}
                    onChange={(e) => {
                        setBet(e.target.value);
                    }}
                />
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
