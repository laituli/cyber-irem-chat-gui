#!/bin/bash
# chat-gui watchdog - ensures server stays running

PORT=${1:-7860}
LOG="/tmp/chat-gui-watchdog.log"

echo "[$(date)] Starting chat-gui watchdog..." | tee -a $LOG

while true; do
    # Check if server is running
    if ! curl --noproxy '*' -s -o /dev/null -w "%{http_code}" http://localhost:$PORT 2>/dev/null | grep -q "200"; then
        echo "[$(date)] Server not responding, restarting..." | tee -a $LOG
        
        # Kill any existing processes
        pkill -f "python3.*$PORT" 2>/dev/null
        sleep 2
        
        # Start server
        nohup python3 -c "
from chat_gui.app import create_app
app = create_app(backend='mock')
app.launch(server_name='0.0.0.0', server_port=$PORT, inbrowser=False, share=False)
" > /tmp/chat-gui-server.log 2>&1 &
        
        echo "[$(date)] Server started with PID $!" | tee -a $LOG
        
        # Wait for it to be ready
        for i in {1..10}; do
            if curl --noproxy '*' -s -o /dev/null -w "%{http_code}" http://localhost:$PORT 2>/dev/null | grep -q "200"; then
                echo "[$(date)] Server ready on port $PORT" | tee -a $LOG
                break
            fi
            sleep 1
        done
    fi
    
    sleep 10
done
