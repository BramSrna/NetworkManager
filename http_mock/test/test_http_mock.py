import http
import logging
import unittest
from unittest.mock import MagicMock
from http_mock.src.http_communicator import HttpCommunicator

from swarm_bot.src.swarm_bot import SwarmBot
from http_mock.src.http_mock import HttpMock
from swarm_manager.src.swarm_manager import SwarmManager
from swarm_manager.src.swarm_connectivity_level import SwarmConnectivityLevel

class MockHttpCommunicator(HttpCommunicator):
    def __init__(self):
        self.id = id(self)

    def get_id(self):
        return self.id

class TestHttpMock(unittest.TestCase):
    def test_http_mock_can_send_message_between_communicators(self):
        test_http_mock = HttpMock()

        http_comm_1 = MockHttpCommunicator()
        http_comm_2 = MockHttpCommunicator()

        test_http_mock.add_http_communicator(http_comm_1)
        test_http_mock.add_http_communicator(http_comm_2)

        http_comm_2.receive_message = MagicMock()

        sender_id = http_comm_1.get_id()
        receiver_id = http_comm_2.get_id()
        message_type = 0
        payload = {"TEST_PAYLOAD": 2}

        test_http_mock.send_message(sender_id, receiver_id, message_type, payload)

        http_comm_2.receive_message.assert_called_once_with(sender_id, message_type, payload)


        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()