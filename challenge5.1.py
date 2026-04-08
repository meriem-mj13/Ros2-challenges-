# Launch file avec arguments

"""
Challenge 4 – Launch file avec arguments
Démarre 'camera_node' avec les arguments :
  - resolution (défaut : '720p')
  - fps        (défaut : 30)

Usage :
  ros2 launch <package> challenge4_camera_launch.py
  ros2 launch <package> challenge4_camera_launch.py resolution:=1080p fps:=60
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # ── Déclaration des arguments ──────────────────────────────────────────
    resolution_arg = DeclareLaunchArgument(
        'resolution',
        default_value='720p',
        description='Camera resolution (e.g. 480p, 720p, 1080p, 4k)'
    )

    fps_arg = DeclareLaunchArgument(
        'fps',
        default_value='30',
        description='Camera frames per second'
    )

    # ── Récupération des valeurs (résolues au runtime) ─────────────────────
    resolution = LaunchConfiguration('resolution')
    fps = LaunchConfiguration('fps')

    # ── Définition du node ─────────────────────────────────────────────────
    camera_node = Node(
        package='your_package',          # ← remplacez par votre package
        executable='camera_node',
        name='camera_node',
        output='screen',
        parameters=[
            {'resolution': resolution},
            {'fps': fps},
        ]
    )

    return LaunchDescription([
        resolution_arg,
        fps_arg,
        camera_node,
    ])
