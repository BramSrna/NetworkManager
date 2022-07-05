import logging
import unittest
import time

from random import randint

from swarm_bot.test.swarm_bot_test_class import SwarmBotTestClass
from map_simulator.src.map_creator import create_map, EMPTY_SPACE, WALL
from swarm_bot.src.swarm_bot_sensor import SwarmBotSensor
from swarm_task.src.swarm_task import SwarmTask


class VisualSensor(SwarmBotSensor):
    def __init__(self, map):
        super().__init__()
        self.map = map

    def read_from_sensor(self, additional_params):
        row = additional_params[0]
        col = additional_params[1]

        if (row < 0) or (row >= len(self.map)):
            return WALL
        if (col < 0) or (col >= len(self.map[0])):
            return WALL
        return self.map[row][col]


def map_using_bots(swarm_bot, map):
    visual_sensor = VisualSensor(map)
    swarm_bot.add_sensor(visual_sensor)

    class MapArea(SwarmTask):
        def __init__(self):
            super().__init__()

            self.curr_row = 0
            self.curr_col = 0

            self.visited_locations = set([])
            self.known_empty_locations = set([])

            self.map = []

            self.num_executions = 0

        def check_surroundings(self):
            if self.executor_interface.read_from_sensor(visual_sensor.get_id(), (self.curr_row - 1, self.curr_col)) == EMPTY_SPACE:
                self.known_empty_locations.add((self.curr_row - 1, self.curr_col))
            if self.executor_interface.read_from_sensor(visual_sensor.get_id(), (self.curr_row + 1, self.curr_col)) == EMPTY_SPACE:
                self.known_empty_locations.add((self.curr_row + 1, self.curr_col))
            if self.executor_interface.read_from_sensor(visual_sensor.get_id(), (self.curr_row, self.curr_col - 1)) == EMPTY_SPACE:
                self.known_empty_locations.add((self.curr_row, self.curr_col - 1))
            if self.executor_interface.read_from_sensor(visual_sensor.get_id(), (self.curr_row, self.curr_col + 1)) == EMPTY_SPACE:
                self.known_empty_locations.add((self.curr_row, self.curr_col + 1))

        def is_task_complete(self):
            return (len(self.known_empty_locations) == 0) and (self.num_executions > 0)

        def execute_task(self):
            self.check_surroundings()

            new_row = self.curr_row
            new_col = self.curr_col

            direction = randint(0, 3)
            if direction == 0:
                new_col += 1
            elif direction == 1:
                new_row -= 1
            elif direction == 2:
                new_col -= 1
            else:
                new_row += 1

            if self.executor_interface.read_from_sensor(visual_sensor.get_id(), (new_row, new_col)) == EMPTY_SPACE:
                self.curr_row = new_row
                self.curr_col = new_col

            while self.curr_row + 1 > len(self.map):
                self.map.append([])
            while self.curr_col + 1 > len(self.map[self.curr_row]):
                self.map[self.curr_row].append(WALL)

            self.map[self.curr_row][self.curr_col] = EMPTY_SPACE

            self.check_surroundings()

            self.num_executions += 1

        def get_task_output(self):
            return self.map

    task = MapArea()
    swarm_bot.receive_task(task)

    start_time = time.time()
    while ((time.time() < start_time + 10) and (not task.is_task_complete())):
        pass

    swarm_bot.teardown()

    return task.get_task_output()


class TestSwarmMessaging(SwarmBotTestClass):
    def test_swarm_bot_can_solve_map_creator_when_given_naive_search_task(self):
        map = create_map(10, 10)

        for row in map:
            print(row)

        print("\n\n")

        swarm_bot = self.create_swarm_bot()
        bot_map = map_using_bots(swarm_bot, map)

        for row in bot_map:
            print(row)

        for row in range(len(bot_map)):
            for col in range(len(bot_map[row])):
                self.assertEqual(bot_map[row][col], map[row][col])

        for row in range(len(map)):
            for col in range(len(map[row])):
                if map[row][col] == EMPTY_SPACE:
                    self.assertEqual(bot_map[row][col], map[row][col])


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
