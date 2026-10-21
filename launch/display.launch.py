import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration

from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    pkg_dir = get_package_share_directory('roboracer_description')

    # 1. Ścieżki do plików
    xacro_file = os.path.join(pkg_dir, 'urdf', 'roboracer.urdf.xacro')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'roboracer.rviz')

    # 2. Argument wyglądu nadwozia: shell (karoseria F1TENTH) lub open (otwarte podwozie)
    body_arg = DeclareLaunchArgument('body', default_value='shell', choices=['shell', 'open'])

    # 3. Konwersja Xacro do URDF
    robot_description = ParameterValue(
        Command(['xacro ', xacro_file, ' body:=', LaunchConfiguration('body')]),
        value_type=str
    )

    # 4. Robot State Publisher: TF z URDF i stanów przegubów
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description}]
    )

    # 5. Suwaki do ręcznego ustawiania przegubów (skręt i obrót kół) zamiast symulacji
    node_joint_state_publisher_gui = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui'
    )

    # 6. RViz z ramką bazową pojazdu (bez symulacji nie ma ramki odom)
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config, '-f', 'base_footprint'],
        output='screen'
    )

    return LaunchDescription([
        body_arg,
        node_robot_state_publisher,
        node_joint_state_publisher_gui,
        rviz
    ])
