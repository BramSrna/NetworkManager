class PropagationStrategy(object):
    def __init__(self, owner_swarm_bot):
        self.swarm_bot = owner_swarm_bot

    def determine_prop_targets(self, message):
        raise Exception("ERROR: The determine_prop_targets method must be implemented by the child class")
