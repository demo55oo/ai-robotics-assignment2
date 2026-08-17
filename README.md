# Assignment 2 – Lane following (Gazebo + ROS 2)

**Demo video:** https://www.loom.com/share/1761c3ae3028425488cb573162f93b29

Repo: https://github.com/demo55oo/ai-robotics-assignment2

## Team
- Adham Mansour Elsaid — 23012143
- Hamza Mohamed Yasser — 21012014
- Aley eldin osama ali Ali 23012080
- mohamed ahmed hesham 23012194
- Youssef abdelkader mohamed 23010144

## Links
- Video: https://www.loom.com/share/1761c3ae3028425488cb573162f93b29
- Bag: [`deliverables/cmd_vel_bag`](deliverables/cmd_vel_bag)
- Lap time: _(fill from video)_


## What we did
We bridge the Prius Sonoma world with `ros_gz_bridge` using `config/gz_sim_bridge_car.yaml`, then run two nodes:

- `lane_perception` reads `/prius/front_camera/image_raw`, finds lane lines (HSV + Canny + Hough), and publishes `/lane/offset`
- `lane_controller` takes that offset and publishes `/cmd_vel` with a simple PD (plus slowing down when the error is big)

## Build
```bash
bash scripts/install_deps.sh   # once
bash scripts/build_ws.sh
source ~/ai_robotics_ws/install/setup.bash
```

## Run
Open 3–4 Ubuntu terminals (source ROS each time: `source /opt/ros/jazzy/setup.bash`).

1. World:
```bash
bash scripts/term1_world.sh
```
(Prius on Sonoma from Fuel, or set `WORLD_PATH` if you have another sdf)

2. Bridge:
```bash
bash scripts/term2_bridge.sh
```

3. Drive:
```bash
source ~/ai_robotics_ws/install/setup.bash
ros2 launch lane_bringup race.launch.py v_cruise:=1.2
```

4. Bag (same run as the video):
```bash
bash scripts/term4_bag.sh
```

If the car oscillates, lower `kp` / `v_cruise`. If it barely turns, raise `kp` a bit. Debug image topic: `/lane/debug_image`.

## Packages
- `src/lane_perception`
- `src/lane_controller`
- `src/lane_bringup` (launch + bridge yaml + params)
