import { sendPacket } from "../connection";

function RegisterForm() {
    return (
        <div className="register-form">
            Register:
            <form onSubmit={onRegisterFormSubmit}>
                <input
                    type="text"
                    id="register-username"
                    placeholder="Username"
                />
                <input
                    type="password"
                    id="register-password"
                    placeholder="Password"
                />
            </form>
        </div>
    );
}

function onRegisterFormSubmit(e) {
    e.preventDefault();
    const username = document.getElementById("register-username").value;
    const passwordElement = document.getElementById("register-password");
    const password = passwordElement.value;
    passwordElement.value = "";
    sendPacket("register", {
        username: username,
        password: password,
    });
}

export default RegisterForm;
