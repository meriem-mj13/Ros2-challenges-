# Implémenter un Lifecycle Node qui démarre un publisher seulement en état 'active' et l'arrête en 'deactivate'.

import rclpy
from rclpy.lifecycle import Node, TransitionCallbackReturn, State
from std_msgs.msg import String


class LifecyclePublisher(Node):

    def __init__(self):
        super().__init__('lifecycle_publisher')
        self.publisher_ = None
        self.timer_ = None

    def on_configure(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Configuring...')
        return TransitionCallbackReturn.SUCCESS

    def on_activate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Activating — starting publisher')
        self.publisher_ = self.create_lifecycle_publisher(String, '/lifecycle_topic', 10)
        self.timer_ = self.create_timer(1.0, self.timer_callback)
        return super().on_activate(state)

    def on_deactivate(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Deactivating — stopping publisher')
        self.destroy_timer(self.timer_)
        self.timer_ = None
        self.publisher_ = None
        return super().on_deactivate(state)

    def on_cleanup(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Cleaning up...')
        return TransitionCallbackReturn.SUCCESS

    def on_shutdown(self, state: State) -> TransitionCallbackReturn:
        self.get_logger().info('Shutting down...')
        return TransitionCallbackReturn.SUCCESS

    def timer_callback(self):
        if self.publisher_ is not None:
            msg = String()
            msg.data = 'Hello from lifecycle node!'
            self.publisher_.publish(msg)
            self.get_logger().info(f'Publishing: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = LifecyclePublisher()
    executor = rclpy.executors.SingleThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
