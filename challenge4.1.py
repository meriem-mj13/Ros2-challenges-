# Créer un Action Server qui simule un déplacement vers une cible (Pose2D) avec feedback de distance restante.

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from my_package.action import MoveToPose
import math
import asyncio


class MoveToPoseServer(Node):

    def __init__(self):
        super().__init__('move_to_pose_server')

        self._action_server = ActionServer(
            self,
            MoveToPose,
            'move_to_pose',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
        )

        # Simulated current position
        self.current_x = 0.0
        self.current_y = 0.0

        self.get_logger().info('Move to Pose action server is ready!')

    def goal_callback(self, goal_request):
        self.get_logger().info(
            f'Received goal: x={goal_request.x:.2f}, y={goal_request.y:.2f}'
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info('Cancel request received')
        return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        target_x = goal_handle.request.x
        target_y = goal_handle.request.y

        feedback_msg = MoveToPose.Feedback()
        result = MoveToPose.Result()

        step_size = 0.1  # meters per step
        sleep_time = 0.5  # seconds between steps

        while True:
            # Check if cancel was requested
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info('Goal cancelled')
                result.final_distance = self._distance(target_x, target_y)
                return result

            dx = target_x - self.current_x
            dy = target_y - self.current_y
            distance = self._distance(target_x, target_y)

            if distance < step_size:
                # Reached the target
                self.current_x = target_x
                self.current_y = target_y
                break

            # Move one step toward target
            self.current_x += step_size * (dx / distance)
            self.current_y += step_size * (dy / distance)

            # Publish feedback
            feedback_msg.remaining_distance = self._distance(target_x, target_y)
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(
                f'Position: ({self.current_x:.2f}, {self.current_y:.2f}) '
                f'| Remaining: {feedback_msg.remaining_distance:.2f} m'
            )

            await asyncio.sleep(sleep_time)

        goal_handle.succeed()
        result.final_distance = 0.0
        self.get_logger().info('Goal reached!')
        return result

    def _distance(self, target_x, target_y):
        return math.sqrt(
            (target_x - self.current_x) ** 2 +
            (target_y - self.current_y) ** 2
        )


def main(args=None):
    rclpy.init(args=args)
    node = MoveToPoseServer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
