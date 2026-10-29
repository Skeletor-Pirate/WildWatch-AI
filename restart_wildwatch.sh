#!/bin/bash
echo "[+] Restarting WildWatch AI services..."
systemctl --user daemon-reload
systemctl --user restart wildwatch-backend.service wildwatch-stream.service
sleep 2
systemctl --user --no-pager status wildwatch-backend.service wildwatch-stream.service
echo "[+] WildWatch AI is online!"
echo "[+] Dashboard: http://localhost:8000/ or http://100.83.115.127:8000/"
