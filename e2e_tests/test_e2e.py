import logging
import unittest

from control_centre.src.control_centre import ControlCentre
from swarm_bot.src.swarm_bot import SwarmBot
from http_mock.src.http_mock import HttpMock

class TestE2e(unittest.TestCase):
    def test_tasks_can_be_delegated_to_swarm_bots(self):
        test_http_mock = HttpMock()
        test_control_centre = ControlCentre(test_http_mock)

        test_swarm_bot = SwarmBot(test_http_mock)
        test_swarm_bot_id = test_swarm_bot.get_id()

        test_control_centre.add_swarm_bot(test_swarm_bot)

        def inner_test_task():
            import random
            num_1 = random.randint(1, 10)
            num_2 = random.randint(1, 10)
            return [num_1, num_2, num_1 + num_2]

        task_iterations = 10
        test_control_centre.delegate_task(test_swarm_bot_id, inner_test_task, task_iterations)

        run_logs = test_control_centre.get_run_logs(test_swarm_bot_id)
        self.assertEqual(task_iterations, len(run_logs))
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()