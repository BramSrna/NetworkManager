import sys
import pygame
import math
import threading

from pygame.locals import QUIT

sys.path.append('../..')

from swarm_bot.src.swarm_bot import SwarmBot  # noqa: E402
from swarm_manager.src.swarm_manager import SwarmManager  # noqa: E402
from swarm_manager.src.swarm_connectivity_level import SwarmConnectivityLevel  # noqa: E402


class Visualizer(object):
    def __init__(self, swarm_bot):
        self.visualizer_width = 500
        self.visualizer_height = 500

        self.border_percent = 5

        self.background_colour = (255, 255, 255)
        self.swarm_bot_colour = (0, 0, 255)
        self.connection_colour = (0, 255, 255)
        self.font_colour = (0, 0, 0)

        self.swarm_bot = swarm_bot

    def visualize_swarm(self):
        pygame.init()

        display = self.__generate_display()
        self.__populate_display(display)

        self._display_screen()
        #thread = threading.Thread(target=self._display_screen)
        #thread.start()

    def _display_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.update()

    def __generate_display(self):
        display = pygame.display.set_mode((self.visualizer_width, self.visualizer_height), 0, 32)

        display.fill(self.background_colour)

        return display

    def __populate_display(self, display):
        # Add a border to the display so that objects and text are not cut off
        border_width = self.visualizer_width * self.border_percent / 100
        border_height = self.visualizer_height * self.border_percent / 100

        drawing_width = self.visualizer_width - border_width * 2
        drawing_height = self.visualizer_height - border_height * 2

        # Determine the bot diameter and placement area
        min_dim = drawing_width
        if drawing_height < min_dim:
            min_dim = drawing_height

        swarm_snapshot = self.swarm_bot.get_swarm_snapshot()
        print(swarm_snapshot)
        swarm_bot_ids = list(swarm_snapshot.keys())
        num_bots = len(swarm_bot_ids)

        bot_diameter = min_dim / (num_bots * 2)
        placement_circle_radius = (min_dim - bot_diameter) / 2
        bot_centres = {}

        # Draw the bots and label them with their IDs
        bot_ind = 0
        for curr_angle in range(0, 360, math.ceil(360 / num_bots)):
            bot_id = swarm_bot_ids[bot_ind]

            # Calculate the angle of the bot on the unit circle
            # Then expand and shift the value to place properly
            radian_angle = math.radians(curr_angle)
            x = (math.cos(radian_angle) * placement_circle_radius) + placement_circle_radius + border_width + bot_diameter / 2
            y = (math.sin(radian_angle) * placement_circle_radius) + placement_circle_radius + border_height + bot_diameter / 2

            bot_centres[bot_id] = {}
            bot_centres[bot_id]["CENTRE"] = (x, y)

            pygame.draw.circle(display, self.swarm_bot_colour, (x, y), bot_diameter / 2)

            # Label the bot with its ID
            font = pygame.font.SysFont('Arial', 10)
            text_surface = font.render(str(bot_id), True, self.font_colour)
            left_wall = x - bot_diameter / 2
            if left_wall < border_width:
                left_wall = border_width
            right_wall = left_wall + text_surface.get_width()
            if right_wall > drawing_width + border_width:
                left_wall -= right_wall - (drawing_width + border_width)
            display.blit(text_surface, (left_wall, y + bot_diameter / 2))

            bot_ind += 1

        # Draw the connections between the bots
        for bot_id, connection_list in swarm_snapshot.items():
            for connection in connection_list:
                pygame.draw.line(display, self.connection_colour, bot_centres[bot_id]["CENTRE"], bot_centres[connection]["CENTRE"])


if __name__ == "__main__":
    visualizer = Visualizer()

    swarm_manager = SwarmManager(SwarmConnectivityLevel.FULLY_CONNECTED)

    num_bots = 10

    for bot in range(num_bots):
        new_bot = SwarmBot()

        swarm_manager.add_swarm_bot(new_bot)

    visualizer.set_swarm_manager(swarm_manager)

    visualizer.visualize_swarm()
