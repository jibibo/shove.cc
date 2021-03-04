import { useState, createContext } from "react";

export const UserContext = createContext();

export function UserProvider({children}) {


    const [ username, setUsername ] = useState("");
    const [ roomName, setRoomName ] = useState("");

    return (
        <UserContext.Provider value={{
            user: { username, setUsername },
            room: { roomName, setRoomName }
        }}>
            {children}
        </UserContext.Provider>
    )

}
