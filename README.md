# AI for Robotics – Assignment 2  
Gazebo–ROS 2 Bridging & Lane-Following Race

## Team

| Name | ID |
|------|----|
| _Member 1_ | _ID_ |
| _Member 2_ | _ID_ |
| _Member 3_ | _ID_ |
| _Member 4 (optional)_ | _ID_ |

## Lap time

**_TBD_** (fill after the recorded run)

## Deliverable links

- **Video** (full lap + bridge/nodes start): _paste Google Drive / YouTube link — anyone with the link can view_
- **Bag** (`cmd_vel_bag` zip from the same run): _paste link_

Submission form: https://forms.gle/4SSA9fNCGhV3ynNx8  
Deadline: **10/3/2026, 11:59 PM**

---

## Approach

### Perception (`lane_perception` / `lane_detector`)

1. Subscribe to `/prius/front_camera/image_raw`.
2. Crop the lower ROI (~50% of the image).
3. HSV thresholds for white + yellow lane paint.
4. Canny edges + Probabilistic Hough lines.
5. Split segments into left/right by slope; fit `x = a·y + b`.
6. Lane center at a fixed row → normalized lateral **offset** in roughly `[-1, 1]`  
   (`+` means lane center is right of image center).
7. Publish `/lane/offset` (`std_msgs/Float32`) and `/lane/debug_image` for tuning/demo.

### Control (`lane_controller` / `lane_follower`)

PD on offset:

- `ω = -Kp · offset - Kd · d(offset)/dt` (clamped)
- `v = v_cruise` scaled down when `|offset|` or `|ω|` is large
- If no perception message for `> 0.5 s`, publish zero `Twist`

### Bridge

`config/gz_sim_bridge_car.yaml` maps clock, `/cmd_vel`, odom, TF, four cameras, and camera_info exactly as specified in the assignment PDF.

---

## Requirements

- Ubuntu 24.04 (WSL2 OK) + **ROS 2 Jazzy**
- Gazebo (Gz Sim) + `ros_gz_bridge`
- Course-provided **car world** (not redistributed here — place under `course_assets/` or set `WORLD_PATH`)
- `python3-opencv`, `cv_bridge`, `colcon`

### One-time dependency install (WSL/Ubuntu)

```bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/install_deps.sh
```

### Build workspace

```bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/build_ws.sh
source ~/ai_robotics_ws/install/setup.bash
```

---

## How to run (4 terminals)

Enlarge terminal font before recording.

**Terminal 1 – Gazebo world**

```bash
export WORLD_PATH=/path/to/instructor_car_world.sdf
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term1_world.sh
```

**Terminal 2 – Bridge**

```bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term2_bridge.sh
```

Smoke checks:

```bash
ros2 topic list
ros2 topic echo /prius/front_camera/image_raw --once
# Manual move test:
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 1.0}, angular: {z: 0.0}}" -r 10
```

**Terminal 3 – Perception + control**

```bash
source ~/ai_robotics_ws/install/setup.bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term3_race.sh
# or: ros2 launch lane_bringup race.launch.py v_cruise:=2.0
```

Optional debug view:

```bash
ros2 run rqt_image_view rqt_image_view   # topic: /lane/debug_image
# or: ros2 topic echo /lane/offset
```

**Terminal 4 – Bag (same run as video)**

```bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term4_bag.sh
# Ctrl+C after the lap; zip the cmd_vel_bag folder for Drive upload
```

---

## Tuning cheat sheet

| Symptom | Try |
|---------|-----|
| No / few Hough lines | Widen HSV white/yellow; lower `hough_threshold` |
| Oscillation | Lower `kp`, raise `kd` slightly |
| Cuts inside curves | Lower `v_cruise`; raise `kp` a little |
| Drifts one side | Check left/right slope split on `/lane/debug_image` |

Start slow (`v_cruise:=1.5`), get one clean lap, then increase speed.

---

## Repository contents

```
config/gz_sim_bridge_car.yaml
src/lane_perception/     # OpenCV lane detector
src/lane_controller/     # PD /cmd_vel follower
src/lane_bringup/        # race + bridge launch files
scripts/                 # install, build, terminal helpers
launch/race.launch.py    # convenience copy
```

Do not commit `build/`, `install/`, `log/`, or bag folders (see `.gitignore`).

---

## Recording checklist

1. Win + G (or equivalent) before starting  
2. Show bridge + node launches in the video  
3. Start bag **before** the car moves  
4. One full in-lane lap  
5. Stop bag and video together  
6. Fill lap time + links above; push public GitHub repo; submit the form
