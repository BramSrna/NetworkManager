class MessageChannel(object):
    def __init__(self):
        pass

    def send_message(self, message_type, message_payload):
        raise Exception("The send_message method must be implemented by the child class.")