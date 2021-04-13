@echo off
title BACKEND %1

if [%1] == [shove.cc] (
    :: start with backend address: https://shove.cc
    python backend/src/main.py

) else if [%1] == [localhost] (
    :: start with backend address: http://localhost
    python backend/src/main.py -no-ssl

) else (
    echo Usage: 'backend shove.cc' OR 'backend localhost'
)

python backend/src/main.py -https