import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_tank_gazebo = get_package_share_directory('tank_gazebo')
    pkg_tank_navigation = get_package_share_directory('tank_navigation')

    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default=os.path.join(pkg_tank_gazebo, 'worlds', 'indoor_obstacle.world'))

    # Gazebo simulation + robot state publisher + spawn
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tank_gazebo, 'launch', 'sim.launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': world
        }.items()
    )

    # Robot Localization (EKF)
    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_tank_navigation, 'launch', 'ekf.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation clock'
        ),
        DeclareLaunchArgument(
            'world',
            default_value=os.path.join(pkg_tank_gazebo, 'worlds', 'indoor_obstacle.world'),
            description='Gazebo world file'
        ),
        sim_launch,
        ekf_launch
    ])
