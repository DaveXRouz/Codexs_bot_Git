#!/bin/bash
# Run the bot in the background with nohup

cd "$(dirname "$0")/.." || exit 1

# Activate virtual environment
source .venv/bin/activate

# Run bot in background with nohup (survives terminal closure)
nohup codexs-bot > logs/bot.log 2>&1 &

# Save the process ID
echo $! > bot.pid

echo "Bot started in background. PID: $(cat bot.pid)"
echo "Logs: logs/bot.log"
echo "To stop: ./scripts/stop_bot.sh"

