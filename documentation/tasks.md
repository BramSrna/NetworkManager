# Tasks
## Introduction
Tasks are how the user tells the swarm what to do. The tasks is defined by the user through the swarm manager. It then gets propagated onto the network and executed by bots in the swarm. Tasks are sets of instructions that the bots executing the task shall follow. Tasks are essentially wrappers for methods and have three stages called the execution contract: setup, body, and teardown. The setup is responsible for telling the swarm how many bots are required, how to connect, and other similar information. The body contains the instructions to execute by the execution units. The teardown section describes what state the network and environment should be when the task is finished executing. In addition to these components, the task shall also have metadata given to the swarm manager that can be used to tell the manager to schedule the task, repeat the task, and other similar information.

## Execution Contracts
Execution contracts are the core of a task. They are defined by the user to specify to the swarm how a task must be executed.

### Setup
The setup stage is used to specify what state the swarm shall be in before executing the task. This information includes:
- The number of bots required to execute the task
- Abstraction layer definitions

### Body
The body stage of the task is used to define the instructions that make up the task. These are the core steps that the execution unit will follow to complete the task.

### Teardown
The teardown stage of the task is used to define the end conditions of the task. This information includes:
- What state the execution environment shall be in when the task is complete
- What state the swarm shall be in when the task is complete
Essentially this is a condition that the executor can use to determine if the task is complete or not.

### Metadata
The metadata of the task is used by the swarm manager to determine extra information regarding the task. This information includes:
- How many times to execute the task
- When to execute the task
- When to regenerate the task

## Task Propagation
After the swarm manager receives the task, the next step is to propagate the task to the swarm. There are two ways to approach task propagation: a centralized approach and a decentralized approach.

### Centralized Task Propagation
The swarm manager is directly connected to each bot in the swarm. This approach takes advantage of this architecture where the manager directly sends the task to each bot in the network.

### Decentralized Task Propagation
In a decentralized apporach, the task is directly delivered to a subset of machines. The task is then propagated to the network using the message propagation strategy of the swarm.

## Executing the Task
1. Definition: The task is defined by the user through the swarm manager
2. Metadata Parsing: The swarm manager parses the metadata from the task to determine extra setup related information
3. Task Propagation: The task is propagated to the network
4. Task Acquiring: According to the parameters specified in the setup of the task, swarm bots signup to work on the task
5. Abstraction Layer Forming: Bots connect to form the abstraction layers described in the abstraction layer of the setup. Setup is now complete.
6. Task Execution: The bots execute the task using the teardown definition check to determine when the task is complete.
7. Teardown: The bots complete the remainder of the steps defined in the teardown section to ensure the environment and swarm are in the expected state.
8. Task Looping: The swarm manager repeats the task according to the metadata information.