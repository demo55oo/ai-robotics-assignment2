"""Launch ros_gz_bridge with the assignment car YAML."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    default_cfg = os.path.join(
        get_package_share_directory('lane_bringup'),
        'config',
        'gz_sim_bridge_car.yaml',
    )
    return LaunchDescription([
        DeclareLaunchArgument('config_file', default_value=default_cfg),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='gz_bridge',
            output='screen',
            parameters=[{'config_file': LaunchConfiguration('config_file')}],
        ),
    ])
