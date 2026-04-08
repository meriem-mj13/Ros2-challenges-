# QoS Profil Capteur

#!/usr/bin/env python3
"""
Challenge 6 – QoS Profil Capteur
Configure les QoS adaptés pour :
  (1) Subscriber LiDAR haute fréquence → BEST_EFFORT + KEEP_LAST(1)
  (2) Publisher de commandes critiques  → RELIABLE  + KEEP_LAST(10)

Pourquoi ces choix ?
──────────────────────────────────────────────────────────────────────
LiDAR (BEST_EFFORT + KEEP_LAST(1)) :
  • La donnée LiDAR est obsolète en quelques millisecondes.
  • Inutile de retransmettre un scan raté : le suivant arrive aussitôt.
  • KEEP_LAST(1) évite de traiter des scans en retard (backpressure).
  • BEST_EFFORT réduit la latence en supprimant les accusés de réception.

Commandes critiques (RELIABLE + KEEP_LAST(10)) :
  • Une commande manquée peut causer un comportement dangereux.
  • RELIABLE garantit la livraison (retransmission si perte).
  • KEEP_LAST(10) conserve un historique court pour les nouveaux
    subscribers qui se connectent après la publication.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSReliabilityPolicy,
    QoSHistoryPolicy,
    QoSDurabilityPolicy,
)
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

# ── Profil 1 : LiDAR haute fréquence ──────────────────────────────────────
QOS_LIDAR = QoSProfile(
    reliability=QoSReliabilityPolicy.BEST_EFFORT,   # pas de retransmission
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,                                         # 1 seul scan en mémoire
    durability=QoSDurabilityPolicy.VOLATILE,         # pas d'historique tardif
)

# ── Profil 2 : Commandes critiques ────────────────────────────────────────
QOS_CMD = QoSProfile(
    reliability=QoSReliabilityPolicy.RELIABLE,       # livraison garantie
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,                                        # tampon de 10 messages
    durability=QoSDurabilityPolicy.VOLATILE,
)


class SensorCommandNode(Node):
    def __init__(self):
        super().__init__('sensor_command_node')

        # (1) Subscriber LiDAR avec QoS BEST_EFFORT
        self.lidar_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            QOS_LIDAR,
        )

        # (2) Publisher de commandes avec QoS RELIABLE
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            QOS_CMD,
        )

        # Timer de démonstration : publie une commande toutes les secondes
        self.timer = self.create_timer(1.0, self.publish_command)

        self.get_logger().info('Node started — LiDAR BEST_EFFORT | CMD RELIABLE')

    # ── Callbacks ──────────────────────────────────────────────────────────
    def lidar_callback(self, msg: LaserScan) -> None:
        """Reçoit les scans LiDAR. Seul le dernier compte."""
        min_range = min(r for r in msg.ranges if r > msg.range_min)
        self.get_logger().info(f'[LiDAR] Closest obstacle: {min_range:.2f} m')

    def publish_command(self) -> None:
        """Publie une commande critique avec livraison garantie."""
        cmd = Twist()
        cmd.linear.x = 0.5   # m/s
        cmd.angular.z = 0.0  # rad/s
        self.cmd_pub.publish(cmd)
        self.get_logger().info(f'[CMD] Published: linear.x={cmd.linear.x}')


def main(args=None):
    rclpy.init(args=args)
    node = SensorCommandNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
