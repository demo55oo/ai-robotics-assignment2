#!/bin/bash
# Terminal 3 — perception + control nodes.

set +u
source /opt/ros/jazzy/setup.bash
source "${HOME}/ai_robotics_ws/install/setup.bash"
set -u

# Conservative defaults; raise v_cruise after a reliable lap.
exec ros2 launch lane_bringup race.launch.py \
  v_cruise:=2.0 \
  kp:=1.4 \
  kd:=0.35
