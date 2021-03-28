import { useState, useContext } from "react";

import { makeStyles } from "@material-ui/core/styles";
import Divider from "@material-ui/core/Divider";
import Container from "@material-ui/core/Container";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import Input from "@material-ui/core/Input";
import Slider from "@material-ui/core/Slider";
import Grid from "@material-ui/core/Grid";
import Box from "@material-ui/core/Box";
import Paper from "@material-ui/core/Paper";
import AttachMoneyIcon from "@material-ui/icons/AttachMoney";
import MoneyOffIcon from "@material-ui/icons/MoneyOff";
import AddIcon from "@material-ui/icons/Add";
import RemoveIcon from "@material-ui/icons/Remove";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";

import { abbreviate } from "../formatting";

import "./CoinflipRoom.css";

let deaf = true;

const useStyles = makeStyles((theme) => ({
    root: {
        flexgrow: 1, // what?
    },
    paper: {
        flex: 1, // what?
        display: "flex",
        alignItems: "center", // vertically centers content
        justifyContent: "center", // horizontally centers content?
        padding: theme.spacing(1),
        backgroundColor: "#333333",
        color: "#fff",
    },
}));

function Room() {
    const { accountData, gameData, setGameData } = useContext(GlobalContext);

    const [betInput, setBetInput] = useState(0);

    const classes = useStyles();

    let userStatus,
        gameStatus,
        showBetters,
        showGains = null;

    function onBet(choice) {
        sendPacket("game_action", {
            action: "bet",
            choice: choice,
            bet: betInput,
        });
        setBetInput(0);
    }

    function onChangeBetSlider(e, value) {
        setBetInput(value);
    }

    function onChangeBetInput(e) {
        setBetInput(e.target.value === "" ? "" : Number(e.target.value));
    }

    if (deaf) {
        deaf = false;

        socket.on("game_action_success", (packet) => {
            // todo memory leak: listeners dont get removed
            console.debug("> CoinflipRoom > game_action_success", packet);
        });

        socket.on("game_data", (packet) => {
            // todo same memory leak here, unlimited listeners
            console.debug("> CoinflipRoom > game_data", packet);
            setGameData(packet);
        });
    }

    if (gameData) {
        if (gameData.state === "idle") {
            userStatus = "Bet to start";
            gameStatus = "Waiting";
            showBetters = false;
            showGains = false;
        } else if (gameData.state === "running") {
            if (accountData.username in gameData.players) {
                // user is playing (has placed a bet)
                userStatus = `Your bet: $${abbreviate(
                    gameData.players[accountData.username]
                )}`;
            }

            gameStatus = `Coin lands in ${gameData.time_left} seconds!`;
            showBetters = true;
            showGains = false;
        } else {
            // state "ended"
            if (accountData.username in gameData.gains) {
                const bet = gameData.gains[accountData.username].bet;
                if (gameData.gains[accountData.username].won) {
                    userStatus = `You won $${abbreviate(bet)}`;
                } else {
                    userStatus = `You lost $${abbreviate(bet)}`;
                }
            }

            gameStatus = `Coin landed on ${gameData.coin_state}`;
            showBetters = false;
            showGains = true;
        }
    }

    return gameData ? (
        <Container>
            <Grid
                container
                justify="center"
                // alignItems="flex-start" // does nothing?
                spacing={2}
                className={classes.root}
            >
                <Box clone order={{ xs: 2, md: 1 }}>
                    <Grid item xs sm md>
                        <Paper className={classes.paper} elevation={8}>
                            <Typography component="p">
                                State: {gameData.state}
                            </Typography>
                            <Typography component="p">{gameStatus}</Typography>
                            <Typography component="p">{userStatus}</Typography>
                        </Paper>
                    </Grid>
                </Box>
                <Box clone order={{ xs: 1, md: 2 }}>
                    <Grid item xs={12} sm={12} md>
                        <Paper className={classes.paper} elevation={8}>
                            <div>
                                {gameData.coin_state !== null ? (
                                    <Grid container>
                                        <img
                                            className={
                                                "coin " +
                                                (gameData.coin_state ===
                                                "spinning"
                                                    ? "spinning"
                                                    : null)
                                            }
                                            src={`./games/coinflip/${gameData.coin_state}.svg`}
                                            alt={`${gameData.coin_state}`}
                                        />
                                    </Grid>
                                ) : (
                                    "Coin hasn't been flipped yet"
                                )}
                                {accountData.money ? (
                                    <div>
                                        <Grid
                                            container
                                            spacing={1}
                                            justify="center"
                                        >
                                            <Grid item xs={12}>
                                                <Slider
                                                    className="bet-slider"
                                                    min={0}
                                                    max={accountData.money}
                                                    step={Math.round(
                                                        accountData.money / 10
                                                    )}
                                                    value={betInput}
                                                    onChange={onChangeBetSlider}
                                                    valueLabelDisplay="auto"
                                                    valueLabelFormat={(value) =>
                                                        `$${abbreviate(value)}`
                                                    }
                                                />
                                            </Grid>
                                        </Grid>
                                        <Grid container spacing={1}>
                                            <Grid item>
                                                <Input
                                                    style={{
                                                        color: "#fff",
                                                        width: "100%",
                                                    }}
                                                    value={betInput}
                                                    onChange={onChangeBetInput}
                                                    inputProps={{
                                                        min: 0,
                                                        max: accountData.money,
                                                        type: "number",
                                                    }}
                                                />
                                            </Grid>
                                            <Grid item>
                                                <Button
                                                    variant="contained"
                                                    startIcon={
                                                        <AttachMoneyIcon />
                                                    }
                                                    onClick={() => {
                                                        onBet("heads");
                                                    }}
                                                    disabled={betInput === 0}
                                                >
                                                    Heads
                                                </Button>
                                            </Grid>
                                            <Grid item>
                                                <Button
                                                    variant="contained"
                                                    startIcon={
                                                        <AttachMoneyIcon />
                                                    }
                                                    onClick={() => {
                                                        onBet("tails");
                                                    }}
                                                    disabled={betInput === 0}
                                                >
                                                    Tails
                                                </Button>
                                            </Grid>
                                        </Grid>
                                    </div>
                                ) : (
                                    <Grid container>
                                        <MoneyOffIcon />u broke fam
                                        <MoneyOffIcon />
                                    </Grid>
                                )}
                                <Divider styles={{ width: "100%" }} />
                                <Grid container>
                                    {showBetters
                                        ? Object.entries(gameData.players).map(
                                              ([username, bet], i) => {
                                                  return (
                                                      <p key={i}>
                                                          {username} bet $
                                                          {abbreviate(bet)}
                                                      </p>
                                                  );
                                              }
                                          )
                                        : null}
                                </Grid>
                            </div>
                        </Paper>
                    </Grid>
                </Box>
                <Box clone order={{ xs: 3, md: 3 }}>
                    <Grid item xs sm md>
                        <Paper className={classes.paper} elevation={8}>
                            {showGains ? (
                                <div>
                                    <p>Gains</p>
                                    <Divider
                                        style={{
                                            backgroundColor: "white",
                                        }}
                                    />
                                    {gameData.gains
                                        ? Object.entries(gameData.gains).map(
                                              ([username, data], i) => {
                                                  const icon = data.won ? (
                                                      <AddIcon />
                                                  ) : (
                                                      <RemoveIcon />
                                                  );
                                                  return (
                                                      <Grid container key={i}>
                                                          {username}:{icon}$
                                                          {abbreviate(data.bet)}
                                                      </Grid>
                                                  );
                                              }
                                          )
                                        : "none"}
                                </div>
                            ) : (
                                "player gains show up here"
                            )}
                        </Paper>
                    </Grid>
                </Box>
            </Grid>
        </Container>
    ) : (
        <h1>gameData not set (very bad)</h1>
    );
}

export default Room;

// old game event and game action success code
// if (packet.action === "bet") { // todo show notification at bottom of screen
// addResult(
//     "You bet $" +
//         abbreviate(packet.bet) +
//         " on: " +
//         packet.choice
// );
// }
// if (packet.state === "idle") {
// if (packet.event === "ended") {
// addResult(
//     "Coin landed on " +
//         packet.coin_state +
//         ", winners: " +
//         JSON.stringify(packet.winners)
// );
// if (accountData?.username in packet.winners) {
//     addResult(
//         "You won, gained $" +
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
// }
// } else {
// // packet.state === "running"
// if (packet.event === "started") {
//     // addResult("Coin flipping, lands in " + packet.time_left);
// } else if (packet.event === "timer_ticked") {
//     // maybe add a indication the timer just ticked down
// }
// }
