import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class StatusPub(Node):
    """
    A simple ROS 2 node that publishes a status message to /robot/status
    every second.

    Bugs fixed:
        1. Topic name changed from 'robot/status' to '/robot/status'
           (absolute path avoids namespace resolution issues).
        2. msg = String()  — instantiated the message class instead of
           referencing the class itself (String vs String()).
        3. self.pub.publish(msg) — passed the message object as an argument
           (publish() requires the message to send).
    """

    def __init__(self):
        super().__init__('status')

        # FIX 1: Use an absolute topic name with a leading '/'
        # Without it, ROS 2 resolves the topic relative to the node's
        # namespace, which can cause mismatches when using 'ros2 topic echo'.
        self.pub = self.create_publisher(String, '/robot/status', 10)

        self.timer = self.create_timer(1.0, self.cb)
        self.get_logger().info("StatusPub node started, publishing on /robot/status")

    def cb(self):
        # FIX 2: Instantiate the message with String() instead of String
        msg = String()
        msg.data = 'OK'

        # FIX 3: Pass the message object to publish()
        self.pub.publish(msg)
        self.get_logger().info(f"Published: '{msg.data}'")


def main(args=None):
    rclpy.init(args=args)
    node = StatusPub()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
