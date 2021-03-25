import { useState, useContext } from "react";

import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";
import AttachMoneyIcon from "@material-ui/icons/AttachMoney";
import MoneyOffIcon from "@material-ui/icons/MoneyOff";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import { abbreviate } from "../formatting";

import "./CoinflipRoom.css";

let deaf = true;

function Room() {
    const { accountData, gameData, setGameData } = useContext(GlobalContext);

    const [betInput, setBetInput] = useState(1);

    function onBet(choice) {
        sendPacket("game_action", {
            action: "bet",
            choice: choice,
            bet: betInput,
        });
        setBetInput(1);
    }

    function onChangeBetSlider(e, value) {
        setBetInput(value);
    }

    if (deaf) {
        deaf = false;

        socket.on("game_action_success", (packet) => {
            console.debug("> CoinflipRoom game_action_success", packet);
            if (packet.action === "bet") {
                // addResult(
                //     "You bet " +
                //         abbreviate(packet.bet) +
                //         " on: " +
                //         packet.choice
                // );
            }
        });

        socket.on("game_data", (packet) => {
            console.debug("> CoinflipRoom game_data", packet);
            setGameData(packet);

            if (packet.state === "idle") {
                if (packet.event === "ended") {
                    // addResult(
                    //     "Coin landed on " +
                    //         packet.coin_state +
                    //         ", winners: " +
                    //         JSON.stringify(packet.winners)
                    // );
                    // if (accountData?.username in packet.winners) {
                    //     addResult(
                    //         "You won, gained " +
                    //             abbreviate(
                    //                 packet.winners[accountData?.username]
                    //             ) +
                    //             "!"
                    //     );
                    // } else if (accountData?.username in packet.losers) {
                    //     addResult("You lost, gained nothing!");
                    // } else {
                    //     // didn't participate or not logged in
                    // }
                }
            } else {
                // // packet.state === "running"
                // if (packet.event === "started") {
                //     // addResult("Coin flipping, lands in " + packet.time_left);
                // } else if (packet.event === "timer_ticked") {
                //     // maybe add a indication the timer just ticked down
                // }
            }
        });
    }
    let userStatus,
        gameStatus,
        showBetters,
        showWinnersLosers = null;
    if (gameData) {
        if (gameData.state === "idle") {
            userStatus = "Bet to start";
            gameStatus = "Waiting";
            showBetters = false;
            showWinnersLosers = false;
        } else if (gameData.state === "running") {
            if (accountData.username in gameData.players) {
                // user is playing (has placed a bet)
                userStatus = `Your bet: ${abbreviate(
                    gameData.players[accountData.username]
                )}`;
            }

            gameStatus = `Coin lands in ${gameData.time_left} seconds!`;
            showBetters = true;
            showWinnersLosers = false;
        } else {
            // state "ended"
            if (accountData.username in gameData.winners) {
                userStatus = `You won ${abbreviate(
                    gameData.winners[accountData.username]
                )}`;
            } else if (accountData.username in gameData.losers) {
                userStatus = `You lost ${abbreviate(
                    gameData.losers[accountData.username]
                )}`;
            }

            gameStatus = `Coin landed on ${gameData.coin_state}`;
            showBetters = false;
            showWinnersLosers = true;
        }
    }

    return (
        <>
            {gameData ? (
                <>
                    <div style={{ width: "300px" }}>
                        State: {gameData.state}
                    </div>
                    <div>
                        {accountData.money ? (
                            <>
                                <Slider
                                    className="bet-slider"
                                    min={1}
                                    max={accountData.money}
                                    value={betInput}
                                    onChange={onChangeBetSlider}
                                    valueLabelDisplay="auto"
                                    valueLabelFormat={(value) =>
                                        abbreviate(value)
                                    }
                                />
                                {/* <Input
                                    style={{ color: "#fff", width: "100%" }}
                                    value={betInput}
                                    color="primary"
                                    onChange={onChangeBetInput}
                                    inputProps={{
                                        min: 1,
                                        max: accountData.money,
                                        type: "number",
                                    }}
                                /> */}
                                <p>Bet {abbreviate(betInput)} on...</p>
                            </>
                        ) : (
                            <>
                                u broke fam
                                <MoneyOffIcon />
                            </>
                        )}
                    </div>
                    <div className="bet-buttons">
                        <div>
                            <Button
                                variant="contained"
                                startIcon={<AttachMoneyIcon />}
                                onClick={() => {
                                    onBet("heads");
                                }}
                            >
                                Heads
                            </Button>
                        </div>
                        <div>
                            <Button
                                variant="contained"
                                startIcon={<AttachMoneyIcon />}
                                onClick={() => {
                                    onBet("tails");
                                }}
                            >
                                Tails
                            </Button>
                        </div>
                    </div>
                    <div>
                        <p>{gameStatus}</p>
                    </div>
                    <div>
                        <p>{userStatus}</p>
                    </div>
                    <div>
                        {gameData.coin_state !== null ? (
                            <img
                                className={
                                    "coin " +
                                    (gameData.coin_state === "spinning"
                                        ? "spinning"
                                        : null)
                                }
                                src={`./games/coinflip/${gameData.coin_state}.svg`}
                                alt={`${gameData.coin_state}`}
                            />
                        ) : (
                            "Coin hasn't been flipped yet"
                        )}
                    </div>
                    <div>
                        {showBetters
                            ? Object.entries(gameData.players).map(
                                  ([username, bet], i) => {
                                      return (
                                          <p key={i}>
                                              {username} bet {abbreviate(bet)}
                                          </p>
                                      );
                                  }
                              )
                            : "betters show up here"}
                    </div>
                    <div>
                        {showWinnersLosers ? (
                            <>
                                <div className="winners">
                                    Winners:{" "}
                                    {gameData.winners
                                        ? Object.entries(gameData.winners).map(
                                              ([username, gain], i) => {
                                                  return (
                                                      <p key={i}>
                                                          {username} won{" "}
                                                          {abbreviate(gain)}
                                                      </p>
                                                  );
                                              }
                                          )
                                        : "none"}
                                </div>
                                <div className="losers">
                                    Losers:{" "}
                                    {gameData.losers
                                        ? Object.entries(gameData.losers).map(
                                              ([username, loss], i) => {
                                                  return (
                                                      <p key={i}>
                                                          {username} lost{" "}
                                                          {abbreviate(loss)}
                                                      </p>
                                                  );
                                              }
                                          )
                                        : "none"}
                                </div>
                            </>
                        ) : (
                            "winners and losers show up here"
                        )}
                    </div>
                </>
            ) : (
                "LOADING"
            )}
        </>
    );
}

export default Room;
