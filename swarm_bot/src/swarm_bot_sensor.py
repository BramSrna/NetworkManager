class SwarmBotSensor(object):
    def __init__(self):
        self.id = id(self)

    def get_id(self):
        return self.id

    def read_from_sensor(self, additional_params):
        raise Exception("ERROR: The read_from_sensor method must be implemented by the concrete class.")
