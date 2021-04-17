import { useState } from "react";

import Button from "@material-ui/core/Button";

import { socket, sendPacket } from "../connection";

let deaf = true;

function SearchMusic() {
  // todo impl, search and display top 5 results, click one to queue it (including thumbnails, duration, etc)
  const [results, setResults] = useState();
  const [inputValue, setInputValue] = useState("");

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
          <div key={i} onClick={() => console.log(result.youtube_id)}>
            <img src={result.thumbnail.url} alt="youtube_thumbnail" />
            <div>{result.name}</div>
          </div>
        ))
        : null}
    </>
  );
}

export default SearchMusic;
