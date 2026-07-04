#!/bin/bash
# Persistent GUI startup script with auto-restart

PORT=${1:-7860}
BACKEND=${2:-ollama}
LOG="/tmp/chat-gui-persistent.log"

echo "=== Starting cyber-irem GUI (port: $PORT, backend: $BACKEND) ===" | tee -a $LOG

while true; do
    echo "[$(date)] Starting GUI server..." | tee -a $LOG
    
    cd /home/lai/cyber-irem && python3 -c "
from chat_gui.app import create_app
app = create_app(backend='$BACKEND')
app.launch(server_name='0.0.0.0', server_port=$PORT, inbrowser=False, share=False)
" >> $LOG 2>&1
    
    EXIT_CODE=$?
    echo "[$(date)] GUI server exited with code $EXIT_CODE, restarting in 3s..." | tee -a $LOG
    sleep 3
done
