#!/bin/bash
# Quick ROS-side smoke checks after world + bridge are running.

set +u
source /opt/ros/jazzy/setup.bash
set -u

echo "== topic list (filtered) =="
ros2 topic list | grep -E 'cmd_vel|odom|/tf|front_camera|clock|lane' || true

echo "== waiting for front camera (10s) =="
if timeout 10 ros2 topic echo /prius/front_camera/image_raw --once >/tmp/cam_once.txt 2>&1; then
  echo "CAMERA_OK"
else
  echo "CAMERA_MISSING — is the world + bridge running?"
  cat /tmp/cam_once.txt || true
  exit 1
fi

echo "SMOKE_OK"
