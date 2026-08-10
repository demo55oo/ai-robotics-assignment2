#!/bin/bash
# Terminal 1 — start the course-provided Gazebo car world.
# Edit WORLD_PATH below once you have the instructor file.

set +u
source /opt/ros/jazzy/setup.bash
set -u

# Prefer an env override, then a local course_assets file.
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORLD_PATH="${WORLD_PATH:-}"

if [[ -z "${WORLD_PATH}" ]]; then
  # Common placeholders — replace with your real world path.
  for candidate in \
    "${REPO_ROOT}/course_assets/car_world.sdf" \
    "${REPO_ROOT}/course_assets/prius_track.sdf" \
    "${HOME}/course_worlds/car_world.sdf"
  do
    if [[ -f "${candidate}" ]]; then
      WORLD_PATH="${candidate}"
      break
    fi
  done
fi

if [[ -z "${WORLD_PATH}" || ! -f "${WORLD_PATH}" ]]; then
  echo "ERROR: Set WORLD_PATH to the instructor-provided Gazebo world file."
  echo "Example:"
  echo "  export WORLD_PATH=/path/to/provided_car_world.sdf"
  echo "  bash scripts/term1_world.sh"
  exit 1
fi

echo "Starting Gz Sim with: ${WORLD_PATH}"
exec gz sim "${WORLD_PATH}"
