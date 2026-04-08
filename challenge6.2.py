#!/usr/bin/env python3
"""
Challenge 7 – MultiThreadedExecutor + ReentrantCallbackGroup
Deux timers dans le même node :
  • Timer rapide  :  50 ms  → traitement léger
  • Timer lent    : 500 ms  → traitement long (simule un calcul)

Problème avec l'exécuteur par défaut (SingleThreadedExecutor) :
──────────────────────────────────────────────────────────────────────
  Un seul thread traite tous les callbacks en séquence.
  Quand le callback lent est en cours (500 ms), le callback rapide
  est bloqué en file d'attente → il ne s'exécute pas à 50 ms.

Solution : MultiThreadedExecutor + ReentrantCallbackGroup :
──────────────────────────────────────────────────────────────────────
  • MultiThreadedExecutor alloue un pool de threads (ici : 2).
  • ReentrantCallbackGroup autorise l'exécution simultanée des
    callbacks du groupe dans des threads différents.
  • Les deux timers tournent en parallèle, sans se bloquer.

Groupes disponibles :
  ReentrantCallbackGroup   → callbacks parallèles (ce qu'on veut ici)
  MutuallyExclusiveCallbackGroup → un seul callback à la fois (défaut)
"""

import time
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup


class DualTimerNode(Node):
    def __init__(self):
        super().__init__('dual_timer_node')

        # Un seul groupe réentrant partagé par les deux timers
        cb_group = ReentrantCallbackGroup()

        # Timer rapide : toutes les 50 ms
        self.fast_timer = self.create_timer(
            0.05,                       # 50 ms
            self.fast_callback,
            callback_group=cb_group,
        )

        # Timer lent : toutes les 500 ms
        self.slow_timer = self.create_timer(
            0.5,                        # 500 ms
            self.slow_callback,
            callback_group=cb_group,
        )

        self._fast_count = 0
        self._slow_count = 0
        self.get_logger().info('DualTimerNode started — fast=50ms | slow=500ms')

    # ── Callback rapide ────────────────────────────────────────────────────
    def fast_callback(self) -> None:
        """Traitement léger, doit tourner à ~20 Hz sans être bloqué."""
        self._fast_count += 1
        self.get_logger().info(
            f'[FAST #{self._fast_count}] tick at {self._now_ms():.0f} ms'
        )

    # ── Callback lent ──────────────────────────────────────────────────────
    def slow_callback(self) -> None:
        """Simule un traitement long (ex : inférence, calcul de chemin)."""
        self._slow_count += 1
        self.get_logger().info(
            f'[SLOW #{self._slow_count}] start — sleeping 400 ms…'
        )
        time.sleep(0.4)   # simule un traitement de 400 ms
        self.get_logger().info(
            f'[SLOW #{self._slow_count}] done  at {self._now_ms():.0f} ms'
        )

    # ── Utilitaire ─────────────────────────────────────────────────────────
    def _now_ms(self) -> float:
        return self.get_clock().now().nanoseconds / 1e6


def main(args=None):
    rclpy.init(args=args)
    node = DualTimerNode()

    # MultiThreadedExecutor avec 2 threads (un par timer)
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
