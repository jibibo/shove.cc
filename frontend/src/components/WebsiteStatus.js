function WebsiteStatus() {
    return (
        <div className="website-status">
            Website status:{" "}
            <span id="website-status">website ping status here</span>
            <div id="online-status" />
            Session id: <span id="session-id">session id goes here</span>
            <br />
            <br />
        </div>
    );
}

function updateStatus() {
    let onlineStatusElement = document.getElementById("online-status");
    let img = document.body.appendChild(document.createElement("img"));
    img.onload = () => {
        onlineStatusElement.innerHTML = "online";
    };
    img.onerror = () => {
        onlineStatusElement.innerHTML = "offline";
    };
    // img.src = "http://shove.cc/img/icon.png";
}

export { WebsiteStatus, updateStatus };
