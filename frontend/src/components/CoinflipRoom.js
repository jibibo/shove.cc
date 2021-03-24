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
    const [coinState, setCoinState] = useState(null);

    const { accountData } = useContext(GlobalContext);

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

        sendPacket("get_game_state", {});

        socket.on("game_action_success", (packet) => {
            console.debug("> CoinflipRoom game_action_success", packet);
            if (packet["action"] === "bet") {
                addResult(
                    "You bet " + packet["bet"] + " on: " + packet["choice"]
                );
                sendPacket("get_account_data", {});
            }
        });

        socket.on("game_state", (packet) => {
            console.debug("> CoinflipRoom game_state", packet);
            setCoinState(packet.coin_state);

            if (packet.state === "idle") {
                if (packet.event === "ended") {
                    addResult(
                        "Coin landed on " +
                            packet.coin_state +
                            ", winners: " +
                            JSON.stringify(packet.info.winners)
                    );
                    setTimeLeft("done");
                    if (accountData?.username in packet.info.winners) {
                        addResult(
                            "You won, gained " +
                                packet.info.winners[accountData?.username] +
                                "!"
                        );
                        sendPacket("get_account_data", {});
                    } else {
                        addResult("You lost, gained nothing!");
                    }
                }
            } else {
                // packet.state === "running"
                setBetters(packet.info.betters);
                setTimeLeft(packet.info.time_left);

                if (packet.event === "started") {
                    addResult(
                        "Coin flipping, lands in " + packet.info.time_left
                    );
                } else if (packet.event === "timer_ticked") {
                    // maybe add a indication the timer just ticked down
                }
            }
        });
    }

    return (
        <>
            <div>
                Time before flip: {timeLeft}
                <br />
                {accountData?.money ? (
                    <>
                        <input
                            type="range"
                            min="1"
                            max={accountData?.money}
                            value={bet}
                            step="1"
                            onChange={(e) => setBet(e.target.value)}
                        />
                        <code>{bet}</code>
                    </>
                ) : (
                    "broke"
                )}
                <div>
                    {coinState !== null ? (
                        coinState === "spinning" ? (
                            <img
                                className="coin spinning"
                                src={`./games/coinflip/spinning.svg`}
                                alt="spinning"
                            />
                        ) : (
                            <img
                                className="coin"
                                src={`./games/coinflip/${coinState}.svg`}
                                alt={`${coinState}`}
                            />
                        )
                    ) : null}
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
