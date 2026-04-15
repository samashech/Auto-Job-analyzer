#!/bin/bash
echo "🚀 Starting Project RAIoT..."
echo ""

# Start Flask backend
echo "📦 Starting Flask backend on port 5000..."
python app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Start Next.js frontend
echo "🎨 Starting Next.js frontend on port 3000..."
cd frontend && npm run dev &
NEXT_PID=$!

echo ""
echo "✅ Both servers running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all servers"

# Handle cleanup
trap "kill $FLASK_PID $NEXT_PID 2>/dev/null; exit" INT TERM
wait
