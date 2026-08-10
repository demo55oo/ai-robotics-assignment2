#!/bin/bash
# Create/build ~/ai_robotics_ws from this repo's src packages.

set -eo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WS="${HOME}/ai_robotics_ws"

mkdir -p "${WS}/src"
# Symlink packages (idempotent)
for pkg in lane_perception lane_controller lane_bringup; do
  ln -sfn "${REPO_ROOT}/src/${pkg}" "${WS}/src/${pkg}"
done

set +u
source /opt/ros/jazzy/setup.bash
set -u

cd "${WS}"
colcon build --symlink-install --packages-select lane_perception lane_controller lane_bringup
set +u
source "${WS}/install/setup.bash"
set -u
echo "BUILD_OK — source ${WS}/install/setup.bash"
