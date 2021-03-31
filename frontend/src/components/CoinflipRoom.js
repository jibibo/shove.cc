import { useState, useContext } from "react";

import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Button from "@material-ui/core/Button";
import Input from "@material-ui/core/Input";
import Slider from "@material-ui/core/Slider";
import Grid from "@material-ui/core/Grid";
import Box from "@material-ui/core/Box";
import Paper from "@material-ui/core/Paper";
import AttachMoneyIcon from "@material-ui/icons/AttachMoney";
import MoneyOffIcon from "@material-ui/icons/MoneyOff";
import List from "@material-ui/core/List";
import ListSubheader from "@material-ui/core/ListSubheader";
import ListItemText from "@material-ui/core/ListItemText";
import ListItem from "@material-ui/core/ListItem";
import ListItemAvatar from "@material-ui/core/ListItemAvatar";
import Divider from "@material-ui/core/Divider";

import { socket, sendPacket } from "../connection";

import { GlobalContext } from "./GlobalContext";
import UserAvatar from "./UserAvatar";

import { abbreviate } from "../formatting";

import "./CoinflipRoom.css";

let deaf = true;

const useStyles = makeStyles((theme) => ({
    root: {
        // flexgrow: 1, // what?
    },
    paper: {
        padding: theme.spacing(1),
        backgroundColor: "#333",
        color: "#fff",
    },
    white: {
        color: "#fff",
    },
    coin: {
        maxWidth: 300,
        margin: "auto",
    },
}));

function Room() {
    const { accountData, gameData, setGameData } = useContext(GlobalContext);

    const [betInput, setBetInput] = useState(0);

    const classes = useStyles();

    let userStatus,
        gameStatus,
        showBetters,
        winners,
        losers,
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
        // todo memory leak: listeners dont get removed
        deaf = false;

        socket.on("game_action_success", (packet) => {
            console.debug("> game_action_success", packet);
        });

        socket.on("game_data", (packet) => {
            console.debug("> game_data", packet);
            setGameData(packet);
        });
    }

    if (gameData) {
        showBetters = false;
        showGains = false;
        if (gameData.state === "idle") {
            gameStatus = "Waiting";
            userStatus = "Bet to start";
        } else if (gameData.state === "running") {
            gameStatus = `Coin lands in ${gameData.time_left} seconds!`;
            showBetters = true;

            if (accountData.username in gameData.players) {
                // user is playing (has placed a bet)
                userStatus = `Your bet: $${abbreviate(
                    gameData.players[accountData.username]
                )}`;
            }
        } else {
            // state "ended"
            gameStatus = `Coin landed on ${gameData.coin_state}`;
            showGains = true;

            winners = [];
            losers = [];

            if (accountData.username in gameData.gains) {
                // check if this user won/lost
                const bet = gameData.gains[accountData.username].bet;
                if (gameData.gains[accountData.username].won) {
                    userStatus = `You won $${abbreviate(bet)}`;
                    winners.push(accountData.username);
                } else {
                    userStatus = `You lost $${abbreviate(bet)}`;
                    losers.push(accountData.username);
                }
            }

            // check all users to see who won/lost
            for (var username in gameData.gains) {
                if (username !== accountData.username) {
                    // make sure no to add this user twice
                    if (gameData.gains[username].won) {
                        winners.push(username);
                    } else {
                        losers.push(username);
                    }
                }
            }
        }
    }

    return gameData ? (
        <Grid container spacing={2} className={classes.root}>
            <Box clone order={{ xs: 2, md: 1 }}>
                <Grid item xs sm md>
                    <Paper className={classes.paper} elevation={8}>
                        <Typography>State: {gameData.state}</Typography>
                        <Typography>{gameStatus}</Typography>
                        <Typography>{userStatus}</Typography>
                    </Paper>
                </Grid>
            </Box>
            <Box clone order={{ xs: 1, md: 2 }}>
                <Grid item xs={12} sm={12} md>
                    <Paper className={classes.paper} elevation={8}>
                        <>
                            {gameData.coin_state !== null ? (
                                <Grid container className={classes.coin}>
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
                                                startIcon={<AttachMoneyIcon />}
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
                                                startIcon={<AttachMoneyIcon />}
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
                            {showBetters ? (
                                <List
                                    dense
                                    subheader={
                                        <ListSubheader
                                            className={classes.white}
                                        >
                                            BETTERS
                                        </ListSubheader>
                                    }
                                >
                                    {Object.entries(gameData.players).map(
                                        ([username, bet], i) => {
                                            return (
                                                <ListItem key={i}>
                                                    <ListItemAvatar>
                                                        <UserAvatar
                                                            username={username}
                                                        />
                                                    </ListItemAvatar>
                                                    <ListItemText
                                                        primary={username}
                                                        secondary={
                                                            "$" +
                                                            abbreviate(bet)
                                                        }
                                                        secondaryTypographyProps={{
                                                            className:
                                                                classes.white,
                                                        }}
                                                    />
                                                </ListItem>
                                            );
                                        }
                                    )}
                                </List>
                            ) : null}
                        </>
                    </Paper>
                </Grid>
            </Box>
            <Box clone order={{ xs: 3, md: 3 }}>
                <Grid item xs sm md>
                    <Paper className={classes.paper} elevation={8}>
                        {showGains ? (
                            <Grid container>
                                <Grid item xs={6}>
                                    <List
                                        dense
                                        subheader={
                                            <ListSubheader
                                                className={classes.white}
                                            >
                                                WINNERS
                                            </ListSubheader>
                                        }
                                    >
                                        {winners.map((username, i) => {
                                            return (
                                                <>
                                                    <ListItem key={i}>
                                                        <ListItemAvatar>
                                                            <UserAvatar
                                                                username={
                                                                    username
                                                                }
                                                            />
                                                        </ListItemAvatar>
                                                        <ListItemText
                                                            primary={username}
                                                            secondary={
                                                                "+ $" +
                                                                abbreviate(
                                                                    gameData
                                                                        .gains[
                                                                        username
                                                                    ].bet
                                                                )
                                                            }
                                                            secondaryTypographyProps={{
                                                                className:
                                                                    classes.white,
                                                            }}
                                                        />
                                                    </ListItem>
                                                    {username ===
                                                    accountData.username ? (
                                                        <Divider />
                                                    ) : null}
                                                </>
                                            );
                                        })}
                                    </List>
                                </Grid>
                                <Grid item xs={6}>
                                    <List
                                        dense
                                        subheader={
                                            <ListSubheader
                                                className={classes.white}
                                            >
                                                LOSERS
                                            </ListSubheader>
                                        }
                                    >
                                        {losers.map((username, i) => {
                                            return (
                                                <>
                                                    <ListItem key={i}>
                                                        <ListItemAvatar>
                                                            <UserAvatar
                                                                username={
                                                                    username
                                                                }
                                                            />
                                                        </ListItemAvatar>
                                                        <ListItemText
                                                            primary={username}
                                                            secondary={
                                                                "- $" +
                                                                abbreviate(
                                                                    gameData
                                                                        .gains[
                                                                        username
                                                                    ].bet
                                                                )
                                                            }
                                                            secondaryTypographyProps={{
                                                                className:
                                                                    classes.white,
                                                            }}
                                                        />
                                                    </ListItem>
                                                    {username ===
                                                    accountData.username ? (
                                                        <Divider />
                                                    ) : null}
                                                </>
                                            );
                                        })}
                                    </List>
                                </Grid>
                            </Grid>
                        ) : (
                            "player gains show up here"
                        )}
                    </Paper>
                </Grid>
            </Box>
        </Grid>
    ) : (
        <h1>gameData not set (very bad)</h1>
    );
}

export default Room;
