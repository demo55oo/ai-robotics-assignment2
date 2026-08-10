"""Start perception + control (bridge is usually launched in its own terminal for the video)."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    share = get_package_share_directory('lane_bringup')
    default_params = os.path.join(share, 'config', 'race_params.yaml')

    return LaunchDescription([
        DeclareLaunchArgument('params_file', default_value=default_params),
        DeclareLaunchArgument('v_cruise', default_value='2.0'),
        DeclareLaunchArgument('kp', default_value='1.4'),
        DeclareLaunchArgument('kd', default_value='0.35'),
        Node(
            package='lane_perception',
            executable='lane_detector',
            name='lane_detector',
            output='screen',
            parameters=[LaunchConfiguration('params_file')],
        ),
        Node(
            package='lane_controller',
            executable='lane_follower',
            name='lane_follower',
            output='screen',
            parameters=[
                LaunchConfiguration('params_file'),
                {
                    'v_cruise': LaunchConfiguration('v_cruise'),
                    'kp': LaunchConfiguration('kp'),
                    'kd': LaunchConfiguration('kd'),
                },
            ],
        ),
    ])
