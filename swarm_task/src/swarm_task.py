class SwarmTask(object):
    def __init__(self, req_num_bots, task_body):
        self.req_num_bots = req_num_bots

    def task_body(self):
        return self.task_body

    def is_task_complete(self):
        raise Exception("ERROR: The is_task_complete method must be implemented by the concrete class.")
