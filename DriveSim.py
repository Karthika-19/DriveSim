import carla # type: ignore
import pygame # type: ignore
import numpy as np # type: ignore
import sys

# CAN Message Interpreter Class
class CANMessageInterpreter:
    def __init__(self):
        self.throttle = 0.0
        self.steering = 0.0
        self.brake = 0.0

    def interpret_message(self, can_message):
        # Assuming can_message is a dictionary with relevant keys
        self.throttle = can_message.get('throttle', 0.0)
        self.steering = can_message.get('steering', 0.0)
        self.brake = can_message.get('brake', 0.0)

    def get_actuation_signals(self):
        return {
            'throttle': self.throttle,
            'steering': self.steering,
            'brake': self.brake
        }

# Vehicle Control Class
class VehicleControl:
    def __init__(self, vehicle):
        self.vehicle = vehicle

    def apply_control(self, signals):
        throttle = signals['throttle']
        steering = signals['steering']
        brake = signals['brake']
        
        # Apply control to the vehicle
        self.vehicle.apply_control(carla.VehicleControl(throttle=throttle, steer=steering, brake=brake))

# Dashboard Class
class Dashboard:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Vehicle Control Dashboard")
        
    def update_display(self, speed, throttle, steering, brake):
        self.screen.fill((255, 255, 255))  # Clear screen
        font = pygame.font.Font(None, 36)

        # Display vehicle state
        texts = [
            f'Speed: {speed:.2f} m/s',
            f'Throttle: {throttle:.2f}',
            f'Steering: {steering:.2f}',
            f'Brake: {brake:.2f}'
        ]

        for i, text in enumerate(texts):
            label = font.render(text, True, (0, 0, 0))
            self.screen.blit(label, (20, 20 + i * 40))

        pygame.display.flip()

    def close(self):
        pygame.quit()
        sys.exit()

# Main Function
def main():
    # Initialize CARLA client
    client = carla.Client('localhost', 2000)
    world = client.get_world()

    # Spawn vehicle
    blueprint = world.get_blueprint_library().find('vehicle.tesla.model3')
    spawn_point = world.get_map().get_spawn_points()[0]
    vehicle = world.spawn_actor(blueprint, spawn_point)

    # Initialize components
    interpreter = CANMessageInterpreter()
    vehicle_control = VehicleControl(vehicle)
    dashboard = Dashboard()

    try:
        while True:
            # Simulate CAN messages
            can_message = {
                'throttle': np.random.uniform(0.0, 1.0),
                'steering': np.random.uniform(-1.0, 1.0),
                'brake': np.random.uniform(0.0, 1.0)
            }

            interpreter.interpret_message(can_message)
            signals = interpreter.get_actuation_signals()
            vehicle_control.apply_control(signals)

            # Get vehicle speed
            speed = vehicle.get_velocity()
            speed_magnitude = np.sqrt(speed.x ** 2 + speed.y ** 2 + speed.z ** 2)

            # Update dashboard
            dashboard.update_display(speed_magnitude, signals['throttle'], signals['steering'], signals['brake'])

            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    dashboard.close()

            # Tick the simulation
            world.tick()

    finally:
        vehicle.destroy()
        dashboard.close()

if __name__ == "__main__":
    main()
