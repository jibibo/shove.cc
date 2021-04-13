@echo off
title BACKEND

if [%1] == [localhost] (
    :: start with backend address: http://localhost
    python backend/src/main.py -no-ssl
) else (
    :: start with backend address: https://shove.cc
    python backend/src/main.py
)