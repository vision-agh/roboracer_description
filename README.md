# roboracer_description

Model samochodu RoboRacer (F1TENTH, skala 1:10) dla ROS 2 Jazzy i Gazebo Harmonic:

- podwozie z napędem Ackermann (tylne koła napędowe, przednie skrętne),
- lidar RPLIDAR C1 (360°, 10 Hz),
- kamera RealSense D435 (obraz kolorowy + kamera głębi, model z `realsense2_description`),
- siatki karoserii i kół F1TENTH.

Pakiet zawiera wyłącznie model. Świat, mostek ROS ↔ Gazebo i uruchamianie symulacji są w pakiecie, który go używa (np. `simple_example`).

## Zawartość

```
roboracer_description/
├── urdf/roboracer.urdf.xacro   model: wymiary, koła, czujniki, wtyczki Gazebo
├── meshes/f1tenth/             siatki STL (karoseria, koła, zwrotnice) + licencja
├── launch/display.launch.py    podgląd modelu w RViz bez symulacji
└── rviz/roboracer.rviz         konfiguracja RViz (model, lidar, odometria, kamera)
```

## Instalacja

W workspace (np. przez plik `.repos`):

```bash
cd ~/ros2_ws
vcs import src < src/roboracer.repos
rosdep install -i --from-paths src --rosdistro $ROS_DISTRO -y
colcon build --symlink-install --packages-select roboracer_description
source install/setup.bash
```

## Podgląd modelu

```bash
ros2 launch roboracer_description display.launch.py            # karoseria F1TENTH
ros2 launch roboracer_description display.launch.py body:=open  # otwarte podwozie z elektroniką
```

Suwakami w oknie *Joint State Publisher* skręcasz i obracasz koła.

## Użycie we własnym pakiecie

W `package.xml`:

```xml
<exec_depend>roboracer_description</exec_depend>
```

W pliku launch:

```python
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue

xacro_file = os.path.join(get_package_share_directory('roboracer_description'),
                          'urdf', 'roboracer.urdf.xacro')
robot_description = ParameterValue(
    Command(['xacro ', xacro_file, ' body:=', LaunchConfiguration('body')]),
    value_type=str
)
```

`robot_description` przekaż do `robot_state_publisher`, a robota w Gazebo utwórz przez `ros_gz_sim create -topic robot_description`. Gazebo znajduje siatki (`package://roboracer_description/...`) dzięki eksportowi `gazebo_ros` w `package.xml`, jeśli Gazebo jest uruchamiane przez `ros_gz_sim/launch/gz_sim.launch.py`.

### Argumenty xacro

| Argument | Wartości | Znaczenie |
|----------|----------|-----------|
| `body`   | `shell` (domyślnie), `open` | karoseria F1TENTH albo otwarte podwozie z płytą i elektroniką |

### Tematy Gazebo (do przekazania mostkiem `ros_gz_bridge`)

| Temat | Typ Gazebo | Kierunek | Opis |
|-------|-----------|----------|------|
| `/cmd_vel` | `gz.msgs.Twist` | do modelu | prędkość liniowa x i kątowa z (Ackermann) |
| `/odom` | `gz.msgs.Odometry` | z modelu | odometria, 30 Hz |
| `/tf` | `gz.msgs.Pose_V` | z modelu | `odom → base_footprint` |
| `/joint_states` | `gz.msgs.Model` | z modelu | stany kół i zwrotnic, 30 Hz |
| `/scan` | `gz.msgs.LaserScan` | z modelu | lidar, 720 próbek, 10 Hz |
| `/camera/color/image_raw` | `gz.msgs.Image` | z modelu | 640×480, 15 Hz |
| `/camera/color/camera_info` | `gz.msgs.CameraInfo` | z modelu | parametry kamery |
| `/camera/depth/points` | `gz.msgs.PointCloudPacked` | z modelu | chmura punktów 424×240, 15 Hz |

### Ramki

`base_footprint` (ziemia) → `base_link` (środek tylnej osi) → `laser`, `camera_link` (+ ramki optyczne RealSense), koła. Dane czujników mają `frame_id`:
- `/scan`: `laser`,
- obraz: `camera_color_optical_frame`,
- chmura punktów: `camera_depth_frame`.

### Główne parametry (początek `urdf/roboracer.urdf.xacro`)

| Właściwość | Wartość | |
|------------|---------|---|
| `wheelbase` | 0.325 m | rozstaw osi |
| `track_width` | 0.245 m | rozstaw kół |
| `wheel_radius` | 0.05 m | promień koła |
| `steering_limit` | 0.42 rad | maksymalny skręt |
| `lidar_height` | 0.175 m | wysokość skanu nad osią (powyżej dachu karoserii) |

Karoseria `shell` pasuje tylko do domyślnych `wheelbase` i `track_width`. Przy innych wymiarach używaj `body:=open`.

## Licencja

Apache License 2.0 (plik `LICENSE`). Siatki w `meshes/f1tenth` pochodzą z [f1tenth-dev/simulator](https://github.com/f1tenth-dev/simulator), również na licencji Apache 2.0 (szczegóły w `meshes/f1tenth/README.md`).
