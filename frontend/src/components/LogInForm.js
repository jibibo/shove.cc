import { sendPacket } from "../connection";

const LogInForm = () => {
    return (
        <div className="log-in-form">
            Log in:
            <form onSubmit={onLogInFormSubmit}>
                <input
                    type="text"
                    id="log-in-username"
                    placeholder="Username"
                />
                <input
                    type="password"
                    id="log-in-password"
                    placeholder="Password"
                />
            </form>
        </div>
    );
};

function onLogInFormSubmit(e) {
    e.preventDefault();
    const username = document.getElementById("log-in-username").value;
    const passwordElement = document.getElementById("log-in-password");
    const password = passwordElement.value;
    console.log(username + password);
    passwordElement.value = "";
    sendPacket({
        model: "log_in",
        username: username,
        password: password,
    });
}

export default LogInForm;
