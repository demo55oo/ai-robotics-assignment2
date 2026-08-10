#!/bin/bash
# Terminal 4 — record /cmd_vel for the same run as your video.
# Start just before the car moves; Ctrl+C when the lap finishes.

set +u
source /opt/ros/jazzy/setup.bash
set -u

OUT="${1:-cmd_vel_bag}"
echo "Recording /cmd_vel → ${OUT}  (Ctrl+C to stop)"
exec ros2 bag record -o "${OUT}" /cmd_vel
