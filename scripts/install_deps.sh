#!/bin/bash
set -eo pipefail
export DEBIAN_FRONTEND=noninteractive
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

# shellcheck disable=SC1091
set +u
source /opt/ros/jazzy/setup.bash
set -u
echo "ROS_DISTRO=${ROS_DISTRO}"

if [[ "$(id -u)" -eq 0 ]]; then
  APT=(apt-get)
else
  APT=(sudo apt-get)
fi

"${APT[@]}" update -qq
"${APT[@]}" install -y --no-install-recommends \
  ros-jazzy-ros-gz-bridge \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-cv-bridge \
  python3-opencv \
  python3-colcon-common-extensions \
  ros-jazzy-launch-ros \
  ros-jazzy-sensor-msgs \
  ros-jazzy-geometry-msgs \
  ros-jazzy-std-msgs \
  ros-jazzy-nav-msgs \
  ros-jazzy-tf2-msgs \
  ros-jazzy-rosbag2 \
  ros-jazzy-rosbag2-storage-default-plugins

apt-get clean || true
echo "----- installed packages -----"
dpkg -l | grep -E 'ros-jazzy-ros-gz-bridge|ros-jazzy-cv-bridge|python3-opencv|ros-jazzy-ros-gz-sim' || true
command -v gz || true
echo "INSTALL_DEPS_OK"
