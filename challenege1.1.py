# Écrire un node qui logue 'Hello ROS2!' toutes les 2 secondes.

import rclpy
from rclpy.node import Node


class HelloROS2Node(Node):

    def __init__(self):
        super().__init__('hello_ros2_node')
        self.create_timer(2.0, self.timer_callback)

    def timer_callback(self):
        self.get_logger().info('Hello ROS2!')


def main(args=None):
    rclpy.init(args=args)
    node = HelloROS2Node()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
