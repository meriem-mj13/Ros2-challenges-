# Broadcaster une transformation dynamique entre 'world' et 'robot' qui tourne sur l'axe Z à 0.5 rad/s.

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler
import math


class DynamicTFBroadcaster(Node):

    def __init__(self):
        super().__init__('dynamic_tf_broadcaster')
        self.broadcaster = TransformBroadcaster(self)
        self.angle = 0.0
        self.create_timer(0.05, self.timer_callback)  # 20 Hz

    def timer_callback(self):
        self.angle += 0.5 * 0.05  # omega * dt = 0.5 rad/s * 0.05s

        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'robot'

        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0

        q = quaternion_from_euler(0.0, 0.0, self.angle)
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]

        self.broadcaster.sendTransform(t)

        self.get_logger().info(
            f'Broadcasting: world -> robot | angle = {self.angle:.2f} rad'
        )


def main(args=None):
    rclpy.init(args=args)
    node = DynamicTFBroadcaster()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
