import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_tank_bringup = get_package_share_directory('tank_bringup')
    pkg_tank_navigation = get_package_share_directory('tank_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Simulation + EKF Base
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tank_bringup, 'launch', 'tank_sim.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # SLAM Toolbox Node
    slam_params_file = os.path.join(pkg_tank_navigation, 'config', 'slam_toolbox.yaml')
    node_slam = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params_file, {'use_sim_time': use_sim_time}]
    )

    # RViz2
    rviz_config_file = os.path.join(pkg_tank_navigation, 'rviz', 'tank_default.rviz')
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),
        sim_launch,
        node_slam,
        node_rviz
    ])
