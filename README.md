# 🤖 YP100 Tracked Robot Tank Simulation (ROS 2 Humble + Gazebo Classic)

Kho mã nguồn mô phỏng độc lập (Decoupled Simulation Package) dành cho robot xe tăng bánh xích **YP100 (PIF TANK)** chạy trên nền tảng **ROS 2 Humble** và **Gazebo Classic (Gazebo 11)** trên hệ điều hành **Ubuntu 22.04 LTS**.

---

## 📌 1. Tổng Quan Kiến Trúc

Dự án được cấu trúc theo 4 module chuẩn của ROS 2:

- **`tank_description`**: Chứa mô hình robot URDF/Xacro chuẩn kích thước khung gầm YP100 ($300 \times 240 \times 122\text{ mm}$), cấu hình cảm biến (RPLIDAR A2M12, IMU 6-DOF) và plugin Gazebo (`gazebo_ros_diff_drive`).
- **`tank_gazebo`**: Chứa môi trường mô phỏng nhà xưởng trong nhà (`indoor_obstacle.world`) với tường ngăn, hành lang và các chướng ngại vật tĩnh; kèm launch file spawn robot.
- **`tank_navigation`**: Cấu hình bộ lọc vị trí EKF (`robot_localization`), thuật toán tạo bản đồ SLAM (`slam_toolbox`), thuật toán dẫn đường tự hành Nav2 (`DWB Controller` + `Navfn Planner`), và giao diện RViz2.
- **`tank_bringup`**: Các launch file một chạm tích hợp chạy toàn bộ chuỗi hệ thống.

```
map ──(slam_toolbox / amcl)──► odom ──(robot_localization EKF)──► base_footprint ──► base_link
                                                                                       ├──► laser_frame (RPLIDAR A2M12)
                                                                                       ├──► imu_link (BNO055/MPU)
                                                                                       ├──► left_wheel
                                                                                       └──► right_wheel
```

---

## 🛠️ 2. Yêu Cầu Cài Đặt (Trên máy phụ Ubuntu 22.04 LTS)

### 2.1. Cài đặt các gói phụ thuộc ROS 2 & Gazebo Classic

Mở terminal trên Ubuntu 22.04 và chạy lệnh:

```bash
sudo apt update && sudo apt install -y \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros \
  ros-humble-robot-localization \
  ros-humble-slam-toolbox \
  ros-humble-navigation2 \
  ros-humble-nav2-bringup \
  ros-humble-xacro \
  ros-humble-joint-state-publisher-gui \
  ros-humble-teleop-twist-keyboard
```

---

## 🚀 3. Hướng Dẫn Clone & Build

### 3.1. Tạo ROS 2 Workspace và clone repo

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/khuy747/yp100_tank_sim.git
```

### 3.2. Biên dịch bằng Colcon

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

*(Mẹo: Thêm `source ~/ros2_ws/install/setup.bash` vào file `~/.bashrc` để không phải source lại mỗi lần mở terminal).*

---

## 🕹️ 4. Hướng Dẫn Vận Hành Từng Chế Độ

### Chế độ 1: Khởi động mô phỏng Gazebo & Kiểm tra xe
Khởi động môi trường thế giới Gazebo, nạp mô hình YP100 và chạy bộ lọc EKF:

```bash
ros2 launch tank_bringup tank_sim.launch.py
```

Mở một terminal mới để lái xe bằng cụm phím **W-A-S-D** quen thuộc (hoặc 4 phím mũi tên):
```bash
ros2 run tank_bringup teleop_wasd
```
- **W / S**: Tiến / Lùi
- **A / D**: Quay trái / Quay phải
- **Q / E**: Tiến rẽ trái / Tiến rẽ phải
- **Space hoặc X**: Phanh / Dừng khẩn cấp
- **R / F**: Tăng / Giảm tốc độ

---

### Chế độ 2: Quét & Tạo Bản Đồ (SLAM Mapping)
Khởi động Gazebo + EKF + SLAM Toolbox + RViz2:

```bash
ros2 launch tank_bringup tank_slam.launch.py
```

1. Mở terminal phụ chạy bộ điều khiển WASD để lái xe đi dạo quanh các phòng và hành lang:
```bash
ros2 run tank_bringup teleop_wasd
```
2. Theo dõi bản đồ 2D được dựng dần trên RViz2.
3. Khi bản đồ đã hoàn chỉnh, lưu bản đồ lại bằng lệnh:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/yp100_tank_sim/tank_navigation/maps/my_map
```
*(Lệnh trên sẽ tạo ra 2 file: `my_map.yaml` và `my_map.pgm`).*

---

### Chế độ 3: Dẫn Đường Tự Hành (Autonomous Navigation với Nav2)
Khởi động xe trong Gazebo cùng hệ thống Nav2 định vị bằng AMCL:

```bash
ros2 launch tank_bringup tank_nav.launch.py map:=/home/<user>/ros2_ws/src/yp100_tank_sim/tank_navigation/maps/my_map.yaml
```

**Thao tác trên RViz2:**
1. Chọn nút **2D Pose Estimate** trên thanh công cụ và click/kéo mũi tên trên map để đặt vị trí ban đầu của robot (khớp với vị trí trong Gazebo).
2. Chọn nút **Nav2 Goal** (hoặc **2D Goal Pose**) và click vào vị trí đích muốn xe đến.
3. Xe YP100 sẽ tự động lập quỹ đạo toàn cục (Global Plan), né tránh các chướng ngại vật động/tĩnh và di chuyển mượt mà tới đích!

---

## ⚙️ 5. Thông Số Kỹ Thuật Khung Gầm YP100 Đã Tinh Chỉnh

| Thông số | Giá trị | Ghi chú trong code |
| :--- | :--- | :--- |
| **Kích thước khung** | $300 \times 240 \times 122\text{ mm}$ | `tank_description/urdf/yp100_core.xacro` |
| **Bán kính bánh xích** | $32.5\text{ mm}$ (Đường kính $65\text{ mm}$) | `wheel_radius = 0.0325` |
| **Khoảng cách 2 xích** | $0.22\text{ m}$ ($220\text{ mm}$) | `wheel_separation = 0.22` |
| **Khối lượng xe** | $2.5\text{ kg}$ | Đã bao gồm khung, pin 4S, Jetson, LiDAR |
| **Nav2 Footprint** | Hình chữ nhật $320 \times 260\text{ mm}$ | `[[0.16, 0.13], [0.16, -0.13], [-0.16, -0.13], [-0.16, 0.13]]` |
| **LiDAR Scanner** | RPLIDAR A2M12 | Tầm xa 12m, góc quét 360°, tần số 10Hz |
| **EKF Fusion** | `robot_localization` | Dung hợp Wheel Odom ($x, y, v_x$) và IMU ($\text{Yaw}, \omega_z$) khử trượt xích |
