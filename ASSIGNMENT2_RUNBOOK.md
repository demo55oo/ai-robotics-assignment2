# Assignment 2 – Runbook (record & submit)

## Before you start
1. Put the instructor car world somewhere and note the path.
2. Install deps once (needs your Ubuntu sudo password):
   ```bash
   bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/install_deps.sh
   ```
3. Build:
   ```bash
   bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/build_ws.sh
   ```
4. Enlarge terminal fonts. Free a little disk space if Windows warns.

## Record day (4 Ubuntu terminals)

### Terminal 1 – world
```bash
export WORLD_PATH=/path/to/instructor_car_world.sdf
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term1_world.sh
```

### Terminal 2 – bridge
```bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term2_bridge.sh
```
Confirm cameras:
```bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/smoke_test.sh
```

### Start screen recording (Win + G)
Show Terminal 2 and 3 launches clearly.

### Terminal 4 – bag (start BEFORE the car moves)
```bash
cd ~
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term4_bag.sh
```

### Terminal 3 – race nodes
```bash
source ~/ai_robotics_ws/install/setup.bash
bash /mnt/c/Users/Adham/Documents/course/ai-robotics-assignment2/scripts/term3_race.sh
```

Watch one full in-lane lap. Note the lap time.

### Stop
1. Ctrl+C bag when lap finishes  
2. Stop video  
3. Zip bag: `zip -r cmd_vel_bag.zip cmd_vel_bag`  
4. Upload video + zip; set sharing to anyone with the link  
5. Fill links + team IDs + lap time in `README.md`  
6. Push GitHub repo (public)  
7. Submit https://forms.gle/4SSA9fNCGhV3ynNx8  

## Tuning during practice (not the graded take)
```bash
ros2 launch lane_bringup race.launch.py v_cruise:=1.5 kp:=1.2 kd:=0.4
ros2 topic echo /lane/offset
```
Use `/lane/debug_image` to verify lane lines before raising speed.
