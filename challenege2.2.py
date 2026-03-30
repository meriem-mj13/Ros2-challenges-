# Créer un service /calcule qui reçoit deux Float64 et une opération (+,-,*,/) et retourne le résultat.

import rclpy
from rclpy.node import Node
from my_package.srv import Calculate


class CalculatorService(Node):

    def __init__(self):
        super().__init__('calculator_service')
        self.srv = self.create_service(Calculate, '/calcule', self.calculate_callback)
        self.get_logger().info('Calculator service is ready!')

    def calculate_callback(self, request, response):
        a = request.a
        b = request.b
        op = request.op

        if op == '+':
            response.result = a + b
        elif op == '-':
            response.result = a - b
        elif op == '*':
            response.result = a * b
        elif op == '/':
            if b != 0.0:
                response.result = a / b
            else:
                self.get_logger().warn('Division by zero! Returning 0.0')
                response.result = 0.0
        else:
            self.get_logger().error(f'Unknown operator: {op}')
            response.result = 0.0

        self.get_logger().info(f'{a} {op} {b} = {response.result}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = CalculatorService()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
