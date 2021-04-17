import { useState } from "react";
import { makeStyles } from "@material-ui/core/styles";

import Button from "@material-ui/core/Button";

import { socket, sendPacket } from "../connection";

const useStyles = makeStyles((theme) => ({
  root: {
    border: "1px red solid",
  },
}));

let deaf = true;

function SearchMusic() {
  const [results, setResults] = useState();
  const [inputValue, setInputValue] = useState("");

  const classes = useStyles();

  if (deaf) {
    deaf = false;

    socket.on("search_song", (packet) => {
      console.debug("> search_song", packet);
      setResults(packet); // list of items
    });
  }

  function onChangeSearchText(e) {
    setInputValue(e.target.value);
  }

  function onSubmitSearch(e) {
    e.preventDefault();
    sendPacket("search_song", {
      query: inputValue,
    });
    setInputValue("");
  }

  return (
    <>
      <form onSubmit={onSubmitSearch}>
        <input onChange={onChangeSearchText} value={inputValue} />
      </form>

      <Button
        type="submit"
        variant="outlined"
        color="secondary"
        onClick={onSubmitSearch}
      >
        Search
      </Button>

      {results
        ? results.map((result, i) => (
            <div
              className={classes.root}
              key={i}
              onClick={() =>
                sendPacket("queue_song", { youtube_id: result.youtube_id })
              }
            >
              <div>{result.name}</div>
              <img src={result.thumbnail.url} alt="youtube_thumbnail" />
            </div>
          ))
        : null}
    </>
  );
}

export default SearchMusic;
