import { useState, useRef } from "react";

import Button from "@material-ui/core/Button";
import Slider from "@material-ui/core/Slider";

import { socket, sendPacket } from "../connection";
import { secondsToString, percentage } from "../formatting";
import Typography from "@material-ui/core/Typography";

let deaf = true;

function AudioPlayer() {
  // todo reduce the amount of states, make compact
  const [source, setSource] = useState();
  const [volume, setVolume] = useState(0.05);
  const [playing, setPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0.1); // prevents dividing by zero
  const [loop, setLoop] = useState(false);
  const [currentSong, setCurrentSong] = useState();
  const [likes, setLikes] = useState(0);
  const [dislikes, setDislikes] = useState(0);
  const [hasLiked, setHasLiked] = useState(false);
  const [hasDisliked, setHasDisliked] = useState(false);

  const audioRef = useRef();

  if (deaf) {
    deaf = false;

    socket.on("play_song", (packet) => {
      console.debug("> play_song", packet);
      loadNewAudio(packet.song_bytes);
      setCurrentSong(packet);
    });

    socket.on("song_rating", (packet) => {
      console.debug("> song_rating", packet);
      setDislikes(packet.dislikes);
      setLikes(packet.likes);
      setHasDisliked(packet.you.disliked);
      setHasLiked(packet.you.liked);
    });

    socket.on("toggle_shuffle", (packet) => {
      console.error("implement"); // todo impl
    });

    socket.on("log_in", () => {
      sendPacket("get_song_rating");
    });

    socket.on("log_out", () => {
      console.debug("> log_out");
      setHasDisliked(false);
      setHasLiked(false);
    });

    // socket.on audio_data, loop enable/disable, play/pause, new url (with author)
  }

  const loadNewAudio = (bytes) => {
    // blobs are amazing https://stackoverflow.com/a/60215835/13216113
    const blob = new Blob([bytes], { type: "audio/mpeg" });
    console.log("Loading new audio blob", blob);
    // audioRef.current.pause();
    // console.log("Paused:", audioRef.current.paused);
    setSource(URL.createObjectURL(blob));
    audioRef.current.load(); // tell element to load new source
    // audioRef.current.play();
  };

  function onChangeVolumeSlider(e, value) {
    // client side volume control
    setVolume(value);

    // if (audioRef.current) {
    audioRef.current.volume = Number(value);
    // }
  }

  function onClickToggleLoop() {
    // should send packet
    audioRef.current.loop = !loop;
    setLoop(!loop);
  }

  function onClickTogglePlay() {
    // should send packet
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  }

  // https://developer.mozilla.org/en-US/docs/Web/HTML/Element/audio#events

  function onAbort() {
    // console.log("abort");
  }

  function onCanPlay() {
    // console.log("canplay");
  }

  function onCanPlayThrough() {
    // console.log("canplaythrough");
    audioRef.current.play();
  }

  function onDurationChange(e) {
    // console.log("durationchange");
    setDuration(Math.floor(e.target.duration));
  }

  function onEmptied() {
    // console.log("emptied");
  }

  function onEnded() {
    // console.log("ended");
    // sendPacket("play_song", { category: "popular" }); // todo old, remove
  }

  function onError() {
    // https://stackoverflow.com/a/29682362/13216113
    console.log("error");
    if (source === undefined) {
      console.log("Not sending error packet - source is undefined");
    } else {
      sendPacket("error", {
        // bad: non-source related errors get passed like this aswell
        description: `Failed to load source: '${source}'`,
      });
    }
  }

  function onLoadStart() {
    // console.log("loadstart");
  }

  function onPause() {
    // console.log("pause");
    setPlaying(false);
  }

  function onPlay() {
    // console.log("play");
    setPlaying(true);
    // make sure html element's volume is correct
    audioRef.current.volume = volume;
  }

  function onProgress() {
    // console.log("progress");
  }

  function onStalled() {
    // console.log("stalled");
  }

  function onSuspend() {
    // console.log("suspend");
  }

  function onTimeUpdate(e) {
    // console.log("timeupdate", e); // spams console
    setProgress(Math.floor(e.target.currentTime));
  }

  function onWaiting() {
    // console.log("waiting");
  }

  return (
    <>
      {currentSong ? (
        <Typography>{`${secondsToString(progress)} / ${secondsToString(
          duration
        )} - ${currentSong.name}, plays: ${currentSong.plays}`}</Typography>
      ) : null}

      <Button variant="outlined" color="secondary" onClick={onClickTogglePlay}>
        {playing ? "Pause" : "Play"}
      </Button>

      <Button variant="outlined" color="secondary" onClick={onClickToggleLoop}>
        Loop: {loop ? "ye" : "no"}
      </Button>

      <Slider
        className="bet-slider"
        min={0}
        max={1}
        step={0.05}
        value={volume}
        onChange={onChangeVolumeSlider}
        valueLabelDisplay="auto"
        valueLabelFormat={(value) => percentage(value)}
      />

      <Button
        variant="outlined"
        color="secondary"
        onClick={() => sendPacket("play_song", { category: "random" })}
      >
        Queue random
      </Button>

      <Button
        variant="outlined"
        color="secondary"
        onClick={() => sendPacket("play_song", { category: "popular" })}
      >
        Queue popular
      </Button>

      <Button
        variant="outlined"
        color="secondary"
        onClick={() => sendPacket("skip_song")}
      >
        Skip current
      </Button>

      <Button
        variant={hasLiked ? "contained" : "outlined"}
        color="secondary"
        onClick={() =>
          sendPacket("rate_song", {
            action: "toggle_like",
          })
        }
      >
        {`Like (${likes})`}
      </Button>

      <Button
        variant={hasDisliked ? "contained" : "outlined"}
        color="secondary"
        onClick={() =>
          sendPacket("rate_song", {
            action: "toggle_dislike",
          })
        }
      >
        {`Dislike (${dislikes})`}
      </Button>

      {/*todo Should just be an Audio() object, no html required*/}
      <audio
        controls
        loop={loop}
        ref={audioRef}
        onAbort={onAbort}
        onCanPlay={onCanPlay}
        onCanPlayThrough={onCanPlayThrough}
        onDurationChange={onDurationChange}
        onEmptied={onEmptied}
        onEnded={onEnded}
        onError={onError}
        onLoadStart={onLoadStart}
        onPause={onPause}
        onPlay={onPlay}
        onProgress={onProgress}
        onStalled={onStalled}
        onSuspend={onSuspend}
        onTimeUpdate={onTimeUpdate}
        onWaiting={onWaiting}
      >
        {/*breaks without this <source />*/}
        <source src={source} type="audio/mpeg" />
      </audio>
    </>
  );
}

export default AudioPlayer;
