# Intra-Swarm Messaging
## Introduction
Due to the nature of swarm robotics, cooperation among bots is a great concern. To facilitate cooperation, bots will need to send messages to each other to communicate. When bots are directly connected to each other, they can send messages directoly to each other. Otherwise, intermediaries are required to either act as a temporary channel to send messages between bots or as a longer term intermediary to allow the bots to form a connection between each other for more permenant connection. The messaging strategy in use will depend on the connectivity strategy in use by the swarm.

## Message Form
Depending on the physical location of the bots, the channels used for sending the messages will vary. For example, bots seperated on different physical devies will need to use HTTP or something similar to send messages while bots in the same execution environment can use the compile environment to send messages. The message structure and channel definitions shall be variable to facilitate these necessaties.

## Message Propagation
When two bots are not directly connected to each other and direct messaging is not available, the bots will need to use intermediaries to message each other. It is assumed that every bot in the swarm is reachable by some connection chain. When messaging to a non-driectly connected bot, the following strategy shall be used:
1. Origin bot shall check if it is directly connected to the target bot. If they are directly connected, the origin bot shall send the message directly to the target bot. Otherwise the next step shall be executed. 
2. The origin bot shall send the message to each bot in its list of direct connections.
3. The bots that receive the message shall check if they are the target bot. If they are, then they move to the next step. Otherwise, they shall repeat from step 1.
4. Once the target bot receives the message, it shall parse it and respond along the path of bots that resulted in the bot first receiving the message.
5. Depending on the connection strategy in use, the origin and target bots may then form a direct connection to speed up further messaging.