#!/usr/bin/env python3

import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

BANNER = """
======================================================
  🎮 BỘ ĐIỀU KHIỂN BÀN PHÍM WASD CHO ROBOT TANK YP100
======================================================
  Di chuyển:
          [W] : Tiến tới
    [A]   [S]   [D] : [Quay trái]   [Lùi lại]   [Quay phải]

  Cua kết hợp:
    [Q] : Tiến rẽ trái         [E] : Tiến rẽ phải
    [Z] : Lùi rẽ trái          [C] : Lùi rẽ phải

  Dừng xe:
    [Space] hoặc [X] : Dừng khẩn cấp (v = 0, w = 0)

  Điều chỉnh tốc độ:
    [R] : Tăng tốc độ (+10%)
    [F] : Giảm tốc độ (-10%)

  Thoát chương trình: Ctrl + C
======================================================
"""

MOVE_BINDINGS = {
    'w': (1.0, 0.0),
    's': (-1.0, 0.0),
    'a': (0.0, 1.0),
    'd': (0.0, -1.0),
    'q': (1.0, 1.0),
    'e': (1.0, -1.0),
    'z': (-1.0, -1.0),
    'c': (-1.0, 1.0),
    'W': (1.0, 0.0),
    'S': (-1.0, 0.0),
    'A': (0.0, 1.0),
    'D': (0.0, -1.0),
    'Q': (1.0, 1.0),
    'E': (1.0, -1.0),
    'Z': (-1.0, -1.0),
    'C': (-1.0, 1.0),
}

SPEED_BINDINGS = {
    'r': (1.1, 1.1),
    'f': (0.9, 0.9),
    'R': (1.1, 1.1),
    'F': (0.9, 0.9),
}


def get_key(settings):
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
        # Handle arrow keys (ANSI escape sequence: \x1b[A, \x1b[B, \x1b[C, \x1b[D)
        if key == '\x1b':
            extra = sys.stdin.read(2)
            if extra == '[A':
                key = 'w'  # Up arrow
            elif extra == '[B':
                key = 's'  # Down arrow
            elif extra == '[C':
                key = 'd'  # Right arrow
            elif extra == '[D':
                key = 'a'  # Left arrow
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


def main():
    settings = termios.tcgetattr(sys.stdin)
    rclpy.init()
    node = rclpy.create_node('tank_teleop_wasd')
    pub = node.create_publisher(Twist, '/cmd_vel', 10)

    speed = 0.25      # Linear speed m/s
    turn = 0.8        # Angular speed rad/s
    target_linear = 0.0
    target_angular = 0.0

    print(BANNER)
    print(f"👉 Tốc độ ban đầu: Tuyến tính = {speed:.2f} m/s | Góc quay = {turn:.2f} rad/s\n")

    try:
        while True:
            key = get_key(settings)

            if key in MOVE_BINDINGS:
                x_dir, th_dir = MOVE_BINDINGS[key]
                target_linear = x_dir * speed
                target_angular = th_dir * turn
                action_name = "DI CHUYỂN"
                if key in ['w', 'W']:
                    action_name = "TIẾN TỚI"
                elif key in ['s', 'S']:
                    action_name = "LÙI LẠI"
                elif key in ['a', 'A']:
                    action_name = "QUAY TRÁI"
                elif key in ['d', 'D']:
                    action_name = "QUAY PHẢI"
                print(f"\r[{action_name}] Linear: {target_linear:+.2f} m/s | Angular: {target_angular:+.2f} rad/s    ", end="", flush=True)

            elif key in [' ', 'x', 'X']:
                target_linear = 0.0
                target_angular = 0.0
                print(f"\r[DỪNG LẠI] Linear: 0.00 m/s | Angular: 0.00 rad/s                     ", end="", flush=True)

            elif key in SPEED_BINDINGS:
                s_factor, t_factor = SPEED_BINDINGS[key]
                speed = max(0.05, min(1.0, speed * s_factor))
                turn = max(0.1, min(3.0, turn * t_factor))
                print(f"\r[TỐC ĐỘ MỚI] Linear Max: {speed:.2f} m/s | Angular Max: {turn:.2f} rad/s    ", end="", flush=True)

            elif key == '\x03':  # Ctrl+C
                break

            # Publish twist message
            twist = Twist()
            twist.linear.x = float(target_linear)
            twist.linear.y = 0.0
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = float(target_angular)
            pub.publish(twist)

    except Exception as e:
        print(f"\nLỗi: {e}")

    finally:
        # Publish final zero stop
        twist = Twist()
        pub.publish(twist)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()
        print("\n\nĐã dừng xe và thoát teleop WASD an toàn.")


if __name__ == '__main__':
    main()
