#!/usr/bin/env python3
"""
Challenge 5 – Action Client non-bloquant
Correction de NavClient : remplacement de send_goal() (bloquant)
par send_goal_async() + callbacks (non-bloquant).

Problème original :
    send_goal() est synchrone → bloque le thread ROS 2 entier,
    empêchant le traitement des callbacks (odométrie, capteurs…).

Solution :
    send_goal_async() retourne un Future.
    On chaîne les callbacks pour gérer :
      1. L'acceptation / refus du goal
      2. Le résultat final
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose


class NavClient(Node):
    def __init__(self):
        super().__init__('nav_client')
        self._client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    # ──────────────────────────────────────────────────────────────────────
    # VERSION ORIGINALE — BLOQUANTE ❌
    # ──────────────────────────────────────────────────────────────────────
    # def go_to(self, x, y):
    #     goal = NavigateToPose.Goal()
    #     goal.pose.pose.position.x = x
    #     goal.pose.pose.position.y = y
    #     result = self._client.send_goal(goal)   # bloque jusqu'à la fin !
    #     return result

    # ──────────────────────────────────────────────────────────────────────
    # VERSION CORRIGÉE — NON-BLOQUANTE ✅
    # ──────────────────────────────────────────────────────────────────────
    def go_to(self, x: float, y: float) -> None:
        """Envoie le goal de façon asynchrone et retourne immédiatement."""
        goal = NavigateToPose.Goal()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.header.frame_id = 'map'

        self.get_logger().info(f'Sending goal → x={x}, y={y}')

        # send_goal_async() retourne un Future (non bloquant)
        self._client.wait_for_server()
        send_future = self._client.send_goal_async(
            goal,
            feedback_callback=self._feedback_callback
        )
        # Callback déclenché quand le serveur accepte ou refuse le goal
        send_future.add_done_callback(self._goal_response_callback)

    def _goal_response_callback(self, future) -> None:
        """Appelé quand le serveur répond à l'envoi du goal."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by server')
            return

        self.get_logger().info('Goal accepted — waiting for result…')

        # Demande du résultat de façon asynchrone
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._result_callback)

    def _result_callback(self, future) -> None:
        """Appelé quand l'action est terminée (succès ou échec)."""
        result = future.result().result
        status = future.result().status
        self.get_logger().info(f'Navigation finished — status={status}, result={result}')

    def _feedback_callback(self, feedback_msg) -> None:
        """Appelé périodiquement pendant l'exécution de l'action."""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Feedback: remaining distance = '
            f'{feedback.distance_remaining:.2f} m'
        )


def main(args=None):
    rclpy.init(args=args)
    node = NavClient()

    # Exemple : aller en (2.0, 3.0)
    node.go_to(2.0, 3.0)

    try:
        # spin() tourne librement → tous les callbacks sont traités
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
