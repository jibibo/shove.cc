import { useState } from "react";
import YouTube from "react-youtube";

import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";

import { socket } from "../connection";

let deaf = true;

// https://www.npmjs.com/package/react-youtube
// https://developers.google.com/youtube/iframe_api_reference

// ERROR CODES
// 2 – The request contains an invalid parameter value. For example, this error occurs if you specify a video ID that does not have 11 characters, or if the video ID contains invalid characters, such as exclamation points or asterisks.
// 5 – The requested content cannot be played in an HTML5 player or another error related to the HTML5 player has occurred.
// 100 – The video requested was not found. This error occurs when a video has been removed (for any reason) or has been marked as private.
// 101/150 – The owner of the requested video does not allow it to be played in embedded players.

// ljoeOLuX6Z4

// TODO CURRENTLY UNUSED

function YoutubePlayer() {
  const [player, setPlayer] = useState();
  const [youtubeId, setYoutubeId] = useState("zHL9GP_B30E"); // use or delete
  const [volumeValue, setVolumeValue] = useState(20);

  // const player = document.getElementById("yt").get;

  const opts = {
    height: 300,
    width: 500,
    playerVars: {
      // https://developers.google.com/youtube/player_parameters
      autoplay: 1,
      controls: 1,
      disablekd: 1,
      fs: 0,
      reL: 0,
    },
  };

  if (deaf) {
    deaf = false;

    socket.on("youtube", (packet) => {
      console.debug("> youtube", packet);
      console.log(`got id ${packet.id} by ${packet.author}`);
      setYoutubeId(packet.id);
      // if (player) {
      // player.loadVideoById(packet.id);
      // } else {
      // console.log("packet: player not set");
      // }
    });
  }

  function onError(event) {
    console.log("on error", event);
  }
  // https://www.youtube.com/watch?v=LD0x7ho_IYc&feature=emb_rel_pause
  function onReady(event) {
    console.log("on ready", event);
    setPlayer(event.target);
    setYoutubeId("zHL9GP_B30E");
    // event.target.loadVideoById("zHL9GP_B30E");
    event.target.playVideo();
  }

  function onClickPlay() {
    console.log("play clicked");
    player.playVideo();
  }
  function onClickPause() {
    console.log("pause clicked");
    player.pauseVideo();
  }
  function onClickStop() {
    console.log("stop clicked");
    player.stopVideo();
  }
  function onClickNext() {
    console.log("next clicked");
    player.nextVideo();
  }
  function onClickPrevious() {
    console.log("previous clicked");
    player.previousVideo();
  }
  function onChangeVolumeSlider(e, value) {
    setVolumeValue(value);
    player.setVolume(Number(volumeValue));
  }

  console.log("render");
  if (player) {
    console.log("render: player is set");
  } else {
    console.log("render: player not set");
  }

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
      <YouTube
        id="yt"
        videoId={youtubeId}
        opts={opts}
        onError={onError}
        onReady={onReady}
      />
    </>
  );
}

export default YoutubePlayer;
