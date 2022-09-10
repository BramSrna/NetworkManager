from swarm_bot.src.propagation_strategy.propagation_strategy import PropagationStrategy


class NaivePropagation(PropagationStrategy):
    def __init__(self, owner_swarm_bot):
        super().__init__(owner_swarm_bot)

    def determine_prop_targets(self, message):
        return self.swarm_bot.get_message_channels().keys()

    def track_message_propagation(self, message):
        pass
