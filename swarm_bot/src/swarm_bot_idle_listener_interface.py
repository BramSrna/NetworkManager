import time

class SwarmBotIdleListenerInterface(object):
    def __init__(self):
        self.num_busy_bots = 0

    def notify_idle_state(self, new_state):
        if new_state:
            self.num_busy_bots -= 1
        else:
            self.num_busy_bots += 1
        print("Num busy bots: {}".format(self.num_busy_bots))

    def swarm_is_idle(self):
        return self.num_busy_bots == 0

    def wait_for_idle_swarm(self, timeout=10):
        start_time = time.time()
        while (time.time() < start_time + timeout):
            if self.swarm_is_idle():
                time.sleep(1)
                if self.swarm_is_idle():
                    return True

        if (time.time() >= start_time + timeout):
            raise Exception("ERROR: Swarm was not idle before timeout was hit. # Busy Bots: {}".format(self.num_busy_bots))