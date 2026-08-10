#!/usr/bin/env python3
"""Front-camera lane detector → /lane/offset (+ debug image)."""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

import cv2
import numpy as np
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32


LineSeg = Tuple[int, int, int, int]


class LaneDetector(Node):
    def __init__(self) -> None:
        super().__init__('lane_detector')

        self.declare_parameter('image_topic', '/prius/front_camera/image_raw')
        self.declare_parameter('offset_topic', '/lane/offset')
        self.declare_parameter('debug_topic', '/lane/debug_image')
        self.declare_parameter('roi_top_fraction', 0.50)
        self.declare_parameter('canny_low', 50)
        self.declare_parameter('canny_high', 150)
        self.declare_parameter('hough_threshold', 40)
        self.declare_parameter('hough_min_line_length', 40)
        self.declare_parameter('hough_max_line_gap', 80)
        self.declare_parameter('min_abs_slope', 0.30)
        self.declare_parameter('hold_frames', 8)
        # HSV white / yellow (tune on your world)
        self.declare_parameter('white_h_low', 0)
        self.declare_parameter('white_s_low', 0)
        self.declare_parameter('white_v_low', 180)
        self.declare_parameter('white_h_high', 180)
        self.declare_parameter('white_s_high', 60)
        self.declare_parameter('white_v_high', 255)
        self.declare_parameter('yellow_h_low', 15)
        self.declare_parameter('yellow_s_low', 60)
        self.declare_parameter('yellow_v_low', 80)
        self.declare_parameter('yellow_h_high', 40)
        self.declare_parameter('yellow_s_high', 255)
        self.declare_parameter('yellow_v_high', 255)

        image_topic = self.get_parameter('image_topic').get_parameter_value().string_value
        offset_topic = self.get_parameter('offset_topic').get_parameter_value().string_value
        debug_topic = self.get_parameter('debug_topic').get_parameter_value().string_value

        self.bridge = CvBridge()
        self._last_offset = 0.0
        self._hold_left = 0

        self.offset_pub = self.create_publisher(Float32, offset_topic, 10)
        self.debug_pub = self.create_publisher(Image, debug_topic, 10)
        self.create_subscription(Image, image_topic, self._on_image, 10)

        self.get_logger().info(f'Listening on {image_topic}')

    def _p(self, name: str):
        return self.get_parameter(name).value

    def _on_image(self, msg: Image) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f'cv_bridge failed: {exc}')
            return

        offset, debug = self._detect(frame)
        out = Float32()
        out.data = float(offset)
        self.offset_pub.publish(out)

        try:
            debug_msg = self.bridge.cv2_to_imgmsg(debug, encoding='bgr8')
            debug_msg.header = msg.header
            self.debug_pub.publish(debug_msg)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f'debug publish failed: {exc}')

    def _color_mask(self, hsv: np.ndarray) -> np.ndarray:
        white = cv2.inRange(
            hsv,
            np.array([self._p('white_h_low'), self._p('white_s_low'), self._p('white_v_low')]),
            np.array([self._p('white_h_high'), self._p('white_s_high'), self._p('white_v_high')]),
        )
        yellow = cv2.inRange(
            hsv,
            np.array([self._p('yellow_h_low'), self._p('yellow_s_low'), self._p('yellow_v_low')]),
            np.array([self._p('yellow_h_high'), self._p('yellow_s_high'), self._p('yellow_v_high')]),
        )
        return cv2.bitwise_or(white, yellow)

    def _detect(self, frame: np.ndarray) -> Tuple[float, np.ndarray]:
        h, w = frame.shape[:2]
        roi_top = int(h * float(self._p('roi_top_fraction')))
        roi = frame[roi_top:h, :].copy()
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = self._color_mask(hsv)
        blur = cv2.GaussianBlur(mask, (5, 5), 0)
        edges = cv2.Canny(
            blur,
            int(self._p('canny_low')),
            int(self._p('canny_high')),
        )

        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180.0,
            threshold=int(self._p('hough_threshold')),
            minLineLength=int(self._p('hough_min_line_length')),
            maxLineGap=int(self._p('hough_max_line_gap')),
        )

        left: List[LineSeg] = []
        right: List[LineSeg] = []
        min_slope = float(self._p('min_abs_slope'))

        if lines is not None:
            for x1, y1, x2, y2 in lines[:, 0]:
                if x2 == x1:
                    continue
                slope = (y2 - y1) / float(x2 - x1)
                if abs(slope) < min_slope:
                    continue
                # Image y grows downward: left lane has negative slope in typical view
                if slope < 0:
                    left.append((int(x1), int(y1), int(x2), int(y2)))
                else:
                    right.append((int(x1), int(y1), int(x2), int(y2)))

        y_eval = int(roi.shape[0] * 0.85)
        left_x = self._fit_x_at_y(left, y_eval)
        right_x = self._fit_x_at_y(right, y_eval)

        lane_center: Optional[float] = None
        if left_x is not None and right_x is not None:
            lane_center = 0.5 * (left_x + right_x)
        elif left_x is not None:
            lane_center = left_x + 0.28 * w
        elif right_x is not None:
            lane_center = right_x - 0.28 * w

        if lane_center is not None:
            offset = (lane_center - (w / 2.0)) / (w / 2.0)
            offset = float(np.clip(offset, -1.5, 1.5))
            self._last_offset = offset
            self._hold_left = int(self._p('hold_frames'))
        elif self._hold_left > 0:
            self._hold_left -= 1
            offset = self._last_offset
        else:
            offset = 0.0

        debug = frame.copy()
        cv2.rectangle(debug, (0, roi_top), (w - 1, h - 1), (80, 80, 80), 1)
        overlay = debug[roi_top:h, :]
        for x1, y1, x2, y2 in left:
            cv2.line(overlay, (x1, y1), (x2, y2), (255, 80, 80), 2)
        for x1, y1, x2, y2 in right:
            cv2.line(overlay, (x1, y1), (x2, y2), (80, 80, 255), 2)

        if lane_center is not None:
            cx = int(lane_center)
            cy = roi_top + y_eval
            cv2.circle(debug, (cx, cy), 6, (0, 255, 0), -1)
            cv2.line(debug, (w // 2, cy - 20), (w // 2, cy + 20), (0, 255, 255), 2)

        cv2.putText(
            debug,
            f'offset={offset:+.3f} L={len(left)} R={len(right)}',
            (12, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return offset, debug

    @staticmethod
    def _fit_x_at_y(segs: List[LineSeg], y: int) -> Optional[float]:
        if not segs:
            return None
        xs: List[float] = []
        ys: List[float] = []
        for x1, y1, x2, y2 in segs:
            xs.extend([float(x1), float(x2)])
            ys.extend([float(y1), float(y2)])
        if len(xs) < 2:
            return None
        # x = a*y + b  (more stable than y=ax+b for near-vertical lines)
        a, b = np.polyfit(ys, xs, 1)
        if not math.isfinite(a) or not math.isfinite(b):
            return None
        return float(a * y + b)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = LaneDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
