#!/bin/bash
# Terminal 2 — ros_gz_bridge with assignment YAML.

set +u
source /opt/ros/jazzy/setup.bash
if [[ -f "${HOME}/ai_robotics_ws/install/setup.bash" ]]; then
  source "${HOME}/ai_robotics_ws/install/setup.bash"
fi
set -u

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CFG="${REPO_ROOT}/config/gz_sim_bridge_car.yaml"

if [[ ! -f "${CFG}" ]]; then
  echo "ERROR: missing bridge config: ${CFG}"
  exit 1
fi

echo "Bridge config: ${CFG}"
exec ros2 run ros_gz_bridge parameter_bridge --ros-args -p "config_file:=${CFG}"
