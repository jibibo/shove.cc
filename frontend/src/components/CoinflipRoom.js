import { useState, useContext } from "react";

import { makeStyles } from "@material-ui/core/styles";
import Container from "@material-ui/core/Container";
import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";
import Grid from "@material-ui/core/Grid";
import Box from "@material-ui/core/Box";
import Paper from "@material-ui/core/Paper";
import AttachMoneyIcon from "@material-ui/icons/AttachMoney";
import MoneyOffIcon from "@material-ui/icons/MoneyOff";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import { abbreviate } from "../formatting";

import "./CoinflipRoom.css";
import { Typography } from "@material-ui/core";

let deaf = true;

const useStyles = makeStyles((theme) => ({
    root: {
        flexgrow: 1, // ?
    },
    paper: {
        flex: 1, // ??
        display: "flex",
        alignItems: "center", // vertically centers content
        justifyContent: "center", // horizontally content
        padding: theme.spacing(1),
        backgroundColor: "#333333",
        color: "#fff",
        elevation: 8, // ??
    },
}));

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
            console.debug("> CoinflipRoom > game_action_success", packet);
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
            console.debug("> CoinflipRoom > game_data", packet);
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

    const classes = useStyles();

    return gameData ? (
        <>
            <div style={{ width: "300px" }}>State: {gameData.state}</div>
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
                            valueLabelFormat={(value) => abbreviate(value)}
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
            <Container>
                <Grid
                    container
                    justify="center"
                    // alignItems="flex-start"
                    spacing={2}
                    className={classes.root}
                >
                    <Box clone order={{ xs: 2, md: 1 }}>
                        <Grid item xs={12} sm md lg>
                            <Paper className={classes.paper}>
                                <span>GAME INFO AND HEADS/TAILS % HERE</span>
                                <br />
                                <h1>aaaa</h1>
                            </Paper>
                        </Grid>
                    </Box>
                    <Box clone order={{ xs: 1, md: 2 }}>
                        <Grid item xs={12} sm={12} md={6} lg={8}>
                            <Paper className={classes.paper}>
                                <Typography>Test</Typography>
                                <span>COIN AND BUTTONS HERE</span>
                                <h1>aaaa</h1>
                            </Paper>
                        </Grid>
                    </Box>
                    <Box clone order={{ xs: 3, md: 3 }}>
                        <Grid item xs={12} sm md lg>
                            <Paper className={classes.paper}>
                                <span>OTHER WINNERS/LOSERS HERE</span>
                                <br />
                                <h1>aaaa</h1>
                            </Paper>
                        </Grid>
                    </Box>
                </Grid>
            </Container>
        </>
    ) : (
        <h1>gameData not set ???</h1>
    );
}

export default Room;
