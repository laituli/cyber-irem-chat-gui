#!/bin/bash
# chat-gui startup and health check script

PORT=${1:-7860}
HOST="0.0.0.0"
HEALTH_URL="http://localhost:$PORT"

echo "=== chat-gui 门禁系统 ==="

# Kill existing server
pkill -f "chat-gui" 2>/dev/null
pkill -f "python3.*7860" 2>/dev/null
pkill -f "python3.*7861" 2>/dev/null
sleep 2

# Check if port is free
if ss -tlnp 2>/dev/null | grep -q ":$PORT "; then
    echo "❌ Port $PORT is still in use"
    exit 1
fi

# Start server in background
python3 -c "
from chat_gui.app import create_app
app = create_app(backend='mock')
app.launch(server_name='$HOST', server_port=$PORT, inbrowser=False, share=False)
" > /tmp/chat-gui.log 2>&1 &

PID=$!
echo "✅ Started server (PID: $PID)"

# Wait for server to be ready
echo "⏳ Waiting for server..."
for i in {1..15}; do
    STATUS=$(curl --noproxy '*' -s -o /dev/null -w "%{http_code}" "$HEALTH_URL" 2>/dev/null)
    if [ "$STATUS" = "200" ]; then
        echo "✅ Server ready on port $PORT"
        echo ""
        echo "🌐 访问地址:"
        echo "   http://localhost:$PORT"
        echo "   http://127.0.0.1:$PORT"
        echo ""
        echo "🔍 健康检查:"
        echo "   curl --noproxy '*' http://localhost:$PORT"
        echo ""
        echo "📋 日志: tail -f /tmp/chat-gui.log"
        echo "🛑 停止: pkill -f 'python3.*$PORT'"
        exit 0
    fi
    sleep 1
done

echo "❌ Server failed to start within 15s"
echo "📋 Logs:"
cat /tmp/chat-gui.log | tail -20
exit 1
