import { useState } from "react";

import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";

import { socket } from "../connection";

let deaf = true;

// ljoeOLuX6Z4 zHL9GP_B30E LD0x7ho_IYc

// TODO CURRENTLY UNUSED

function AudioPlayer() {
    const [player, setPlayer] = useState();
    const [volumeValue, setVolumeValue] = useState(20);
    const [url, setUrl] = useState()

    if (deaf) {
        deaf = false;

        socket.on("play_audio", (packet) => {
            console.debug("> play_audio", packet);
            console.log(`got url ${packet.url} by ${packet.author}`);
            setUrl(packet.url)
        });
    }

    function onClickPlay() {
    }
    function onClickPause() {
    }
    function onClickStop() {
    }
    function onClickNext() {
    }
    function onClickPrevious() {
    }
    function onChangeVolumeSlider(e, value) {
        setVolumeValue(value);
    }

    console.log("render");

    return (
        <>
            <Button
                variant="outlined"
                color="secondary"
                onClick={onClickPlay}
                disabled={!player}
            >
                Play
            </Button>
            <Button
                variant="outlined"
                color="secondary"
                onClick={onClickPause}
                disabled={!player}
            >
                Pause
            </Button>
            <Button
                variant="outlined"
                color="secondary"
                onClick={onClickStop}
                disabled={!player}
            >
                Stop
            </Button>
            <Button
                variant="outlined"
                color="secondary"
                onClick={onClickNext}
                disabled={!player}
            >
                Next
            </Button>
            <Button
                variant="outlined"
                color="secondary"
                onClick={onClickPrevious}
                disabled={!player}
            >
                Previous
            </Button>
            <Slider
                className="bet-slider"
                min={0}
                max={100}
                step={10}
                value={volumeValue}
                onChange={onChangeVolumeSlider}
                valueLabelDisplay="auto"
            />
        </>
    );
}

export default AudioPlayer;
