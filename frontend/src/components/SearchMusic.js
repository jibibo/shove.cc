import { useState, useRef } from "react";

import Button from "@material-ui/core/Button";

import { socket, sendPacket } from "../connection";

let deaf = true;

function SearchMusic() {
  // todo impl, search and display top 5 results, click one to queue it (including thumbnails, duration, etc)
  const [results, setResults] = useState();
  const [inputValue, setInputValue] = useState();

  if (deaf) {
    deaf = false;

    socket.on("search", (packet) => {
      console.debug("> search", packet);
    });

    // socket.on audio_data, loop enable/disable, play/pause, new url (with author)
  }

  return (
    <>
      <input value={inputValue} />
      <Button
        variant="outlined"
        color="secondary"
        onClick={() => sendPacket("play_song", { category: "random" })}
      >
        Play random
      </Button>

      <Button
        variant="outlined"
        color="secondary"
        onClick={() => sendPacket("play_song", { category: "popular" })}
      >
        Play popular
      </Button>

      <Button
        variant={"contained"}
        color="secondary"
        onClick={() =>
          sendPacket("rate_song", {
            action: "toggle_like",
          })
        }
      >
        {`Like ()`}
      </Button>
    </>
  );
}

export default SearchMusic;
