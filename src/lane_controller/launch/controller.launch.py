from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package='lane_controller',
            executable='lane_follower',
            name='lane_follower',
            output='screen',
            parameters=[{
                'v_cruise': 2.0,
                'kp': 1.4,
                'kd': 0.35,
                'max_w': 1.2,
            }],
        ),
    ])
