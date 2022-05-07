class HttpCommunicator(object):
    def __init__(self):
        pass

    def send_message(self, sender_id, receiver_id, message_type, message_payload):
        raise Exception("ERROR: The send_message method must be implemented by the child class.")

    def receive_message(self, sender_id, message_type, message_payload):
        raise Exception("ERROR: The receive_message method must be implemented by the child class.")

    def get_id(self):
        raise Exception("ERROR: The get_id method must be implemented by the child class.")

