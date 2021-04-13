@echo off
set BROWSER=none

if [%1] == [https] (
    :: start frontend https AND connect to backend https
    set REACT_APP_BACKEND_URL=https://shove.cc:777
    set HTTPS=true
    set PORT=443
    set SSL_CRT_FILE=../cert.pem
    set SSL_KEY_FILE=../key.pem
    start chrome.exe https://shove.cc
    npm start --prefix frontend

) else if [%1] == [shove.cc] (
    :: start localhost with backend address: https://shove.cc
    set REACT_APP_BACKEND_URL=https://shove.cc:777
    set HTTPS=false
    set PORT=80
    start chrome.exe http://localhost
    npm start --prefix frontend

) else if [%1] == [localhost] (
    :: start localhost with backend address: http://localhost
    set REACT_APP_BACKEND_URL=http://localhost:777
    set HTTPS=false
    set PORT=80
    start chrome.exe http://localhost
    npm start --prefix frontend

) else (
    echo Usage: 'frontend https' OR 'frontend localhost' OR 'frontend shove.cc'
)