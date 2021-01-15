#!/bin/bash
set -e

if [ "$1" = 'bot' ]; then
    exec python3 /home/track/track/track/bot.py
fi

exec "$@"