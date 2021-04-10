@echo off
title FRONTEND
set DOMAIN=shove.cc
set HTTPS=true
set SSL_CRT_FILE=cert.pem
set SSL_KEY_FILE=key.pem
npm start --prefix frontend