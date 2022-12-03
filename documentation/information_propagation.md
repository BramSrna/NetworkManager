# Information Propagation
To support a variety of functionality, nodes will need to be able to broadcast information to the whole network either for a form of messaging or for information sharing. There are a variety of areas to address with information propagation:
- The strategy used for propagation
- Ensuring the information is propagated to the entire network while minimizing circular messaging

## Propagation Strategy
### Naive Propagation
#### Description
The most starightforward form of message propagation is naive propagation. The strategy used for propagation is as follows:
1. Source node sends the message to each node it is connected to
2. When a node receives the message:
    - If receiving the message for the first time
        - Send the message to each connected node
    - If receiving the message a subsequent time
        - Ignore the message

The benefit to this method is that it is very resilient to connection issues. If a connection is slow or broken, the message will be propagated using a different path if available. Additionally, messages will naturally follow the shortest path to each node. The downside to this method is that there will be a lot of repeated message sending.

#### Implementation
The Naive Propagation implementation can be seen here: swarm_bot\src\propagation_strategy\naive_propagation.py

#### Expected Messaging Count
Where N is the number of nodes a node is connected to:
Source node:
- Send: N - 1 messages
- Receive: N - 1 messages
- Ignore: N - 1 messages

Receiver nodes:
- Send: N - 1 messages
- Receive: N - 1 messages
- Ignore: N - 2 messages

### Smart Propagation
Smart Propagation is the same as Naive Propagation with two additional strategies used to increase efficiency:
- Remove message echoing: In Naive Propagation, the receiver node sends the message to every node it is connected to, including the source node. Since the node knows that the source node has already received the message, it does not need to receive it again. This will help to decrease the number of unnecessary messages sent.
- Prioritize the order that messages are sent to the connected nodes: When a node receives a propagated message that it has already dealt with, it will ignore the message. By tracking when these messages are received and which node sent them, the receiver node can get a rough estimate of the second shortest path to the sender node. Then when sending out a message, the source node can start with the nodes that have no second path or have a very long second path before moving onto the ones with short second paths. This strategy will decrease the amount of times it takes to fully propagate a message while maintaining the reslience offered by naive propagation.

The strategy used for propagation is as follows:
1. Source node sends the message to each node it is connected to
2. When a node receives the message:
    - If receiving the message for the first time: 
        - Send the message to each connected node, excluding the sender node, in descending order according to the average message receive time for each node
        - Record the time when the message was received
        - Calculate the new average time for the node
    - If receiving the message a subsequent time:
        - Calculate the difference in time from when the message was first received and when it was subsequentally received
        - Calculate the new average time for the node

#### Implementation
The Smart Propagation implementation can be seen here: swarm_bot\src\propagation_strategy\smart_propagation.py

#### Expected Messaging Count
Where N is the number of nodes a node is connected to:
Source node:
- Send: N - 1 messages
- Receive: 0
- Ignore: 0

Receiver nodes:
- Send N - 2 messages
- Receive N - 1 messages
- Ignore N - 2 messages