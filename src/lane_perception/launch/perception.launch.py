from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package='lane_perception',
            executable='lane_detector',
            name='lane_detector',
            output='screen',
        ),
    ])
