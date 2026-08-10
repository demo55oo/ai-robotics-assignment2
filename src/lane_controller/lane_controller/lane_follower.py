#!/usr/bin/env python3
"""PD lane follower: /lane/offset → /cmd_vel."""

from __future__ import annotations

import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import Float32


class LaneFollower(Node):
    def __init__(self) -> None:
        super().__init__('lane_follower')

        self.declare_parameter('offset_topic', '/lane/offset')
        self.declare_parameter('cmd_vel_topic', '/cmd_vel')
        self.declare_parameter('v_cruise', 2.0)
        self.declare_parameter('kp', 1.4)
        self.declare_parameter('kd', 0.35)
        self.declare_parameter('max_w', 1.2)
        self.declare_parameter('max_offset_for_full_speed', 0.35)
        self.declare_parameter('timeout_sec', 0.5)
        self.declare_parameter('control_rate_hz', 30.0)

        offset_topic = self.get_parameter('offset_topic').get_parameter_value().string_value
        cmd_topic = self.get_parameter('cmd_vel_topic').get_parameter_value().string_value

        self._offset = 0.0
        self._last_offset = 0.0
        self._last_offset_time = time.monotonic()
        self._last_msg_time = 0.0
        self._have_msg = False

        self.cmd_pub = self.create_publisher(Twist, cmd_topic, 10)
        self.create_subscription(Float32, offset_topic, self._on_offset, 10)

        rate = float(self.get_parameter('control_rate_hz').value)
        self.create_timer(1.0 / max(rate, 1.0), self._tick)

        self.get_logger().info(
            f'Controller ready: v_cruise={self.get_parameter("v_cruise").value} '
            f'kp={self.get_parameter("kp").value} kd={self.get_parameter("kd").value}'
        )

    def _on_offset(self, msg: Float32) -> None:
        now = time.monotonic()
        self._last_offset = self._offset
        dt = max(now - self._last_offset_time, 1e-3)
        self._offset = float(msg.data)
        self._d_offset = (self._offset - self._last_offset) / dt
        self._last_offset_time = now
        self._last_msg_time = now
        self._have_msg = True

    def _tick(self) -> None:
        cmd = Twist()
        timeout = float(self.get_parameter('timeout_sec').value)
        if (not self._have_msg) or (time.monotonic() - self._last_msg_time > timeout):
            self.cmd_pub.publish(cmd)
            return

        kp = float(self.get_parameter('kp').value)
        kd = float(self.get_parameter('kd').value)
        max_w = float(self.get_parameter('max_w').value)
        v_cruise = float(self.get_parameter('v_cruise').value)
        max_off = float(self.get_parameter('max_offset_for_full_speed').value)

        d_off = getattr(self, '_d_offset', 0.0)
        # Positive offset = lane center right of image center → turn right (negative ω in ROS ENU? )
        # For differential / Ackermann Twist: positive angular.z = CCW (left). Drift right → steer left.
        w = -kp * self._offset - kd * d_off
        w = max(-max_w, min(max_w, w))

        # Slow down when far from center or commanding hard turn
        scale = 1.0
        abs_off = abs(self._offset)
        if abs_off > max_off:
            scale = max(0.35, 1.0 - (abs_off - max_off))
        if abs(w) > 0.6 * max_w:
            scale = min(scale, 0.7)

        cmd.linear.x = v_cruise * scale
        cmd.angular.z = w
        self.cmd_pub.publish(cmd)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LaneFollower()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        stop = Twist()
        node.cmd_pub.publish(stop)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
