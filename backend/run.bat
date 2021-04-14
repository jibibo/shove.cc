@echo off

if [%1] == [localhost] (
    :: start with host address: http://localhost
    title BACKEND SSL DISABLED
    echo Starting with SSL DISABLED
    python src/main.py -no-ssl
) else (
    :: start with host address: https://shove.cc
    title BACKEND
    echo Starting
    python src/main.py
)