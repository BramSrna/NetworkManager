from http_mock.src.http_communicator import HttpCommunicator

class HttpMock(object):
    def __init__(self):
        self.http_communicator_dict = {}

    def add_http_communicator(self, new_http_communicator):
        if not isinstance(new_http_communicator, HttpCommunicator):
            raise Exception("ERROR: new_http_communicator must be of type HttpCommunicator")
        self.http_communicator_dict[new_http_communicator.get_id()] = new_http_communicator

    def send_message(self, sender_id, receiver_id, message_type, message_payload):
        self.http_communicator_dict[receiver_id].receive_message(sender_id, message_type, message_payload)
