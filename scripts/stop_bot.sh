#!/bin/bash
# Stop the running bot

cd "$(dirname "$0")/.." || exit 1

if [ -f bot.pid ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        rm bot.pid
        echo "Bot stopped (PID: $PID)"
    else
        echo "Bot is not running (PID file exists but process not found)"
        rm bot.pid
    fi
else
    # Fallback: kill by process name
    pkill -f codexs-bot
    echo "Bot stopped (killed by process name)"
fi

