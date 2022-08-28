class PropagationStrategy(object):
    def __init__(self, owner_swarm_bot):
        self.swarm_bot = owner_swarm_bot

    def determine_prop_targets(self, message):
        raise Exception("ERROR: The determine_prop_targets method must be implemented by the child class")

    def track_message_propagation(self, message):
        raise Exception("ERROR: The track_message_propagation method must be implemented by the child class")
