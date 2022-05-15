from common.src.message_types import MessageTypes
from http_mock.src.http_communicator import HttpCommunicator

class HttpMock(object):
    def __init__(self):
        self.http_communicator_dict = {}

    def add_http_communicator(self, new_http_communicator: HttpCommunicator) -> None:
        self.http_communicator_dict[new_http_communicator.get_id()] = new_http_communicator

    def send_message(self, sender_id: str, receiver_id: str, message_type: int, message_payload: dict) -> None:
        self.http_communicator_dict[receiver_id].receive_message(sender_id, message_type, message_payload)
