#!/usr/bin/env bash

# ждём интернет
for i in {1..12}; do
    ping -c1 8.8.8.8 &>/dev/null && break
    echo "инета нет, попытка $i..."
    sleep 5
done

# старт из venv
"/home/almasezhe/Documents/coding stuff/controllerBot/.venv/bin/python" \
"/home/almasezhe/Documents/coding stuff/controllerBot/main.py"
