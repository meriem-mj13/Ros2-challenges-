# Subscriber avec filtre


#!/usr/bin/env python3
"""
Challenge 3 – Subscriber avec filtre de température
Abonne le node à /temperature (Float64) et affiche un warning
si la valeur dépasse 30°C ou est inférieure à 10°C.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64

TEMP_MAX = 30.0  # °C
TEMP_MIN = 10.0  # °C


class TemperatureMonitor(Node):
    def __init__(self):
        super().__init__('temperature_monitor')

        self.subscription = self.create_subscription(
            Float64,
            '/temperature',
            self.temperature_callback,
            10
        )
        self.get_logger().info(
            f'Monitoring /temperature — warn if < {TEMP_MIN}°C or > {TEMP_MAX}°C'
        )

    def temperature_callback(self, msg: Float64) -> None:
        temp = msg.data

        if temp > TEMP_MAX:
            self.get_logger().warn(
                f'Temperature too HIGH: {temp:.1f}°C (threshold: {TEMP_MAX}°C)'
            )
        elif temp < TEMP_MIN:
            self.get_logger().warn(
                f'Temperature too LOW: {temp:.1f}°C (threshold: {TEMP_MIN}°C)'
            )
        else:
            self.get_logger().info(f'Temperature OK: {temp:.1f}°C')


def main(args=None):
    rclpy.init(args=args)
    node = TemperatureMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
