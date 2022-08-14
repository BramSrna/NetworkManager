# Intra-Swarm Messaging
## Introduction
Due to the nature of swarm robotics, cooperation among bots is a great concern. To facilitate cooperation, bots will need to send messages to each other to communicate. There are two kinds of messaging. The first is messaging directly to connected bots. This is the basic use case where bots are sending messages back-and-forth between each other. The other case is propagating messages where information is broadcasted to the entire network.

## Message Form
Depending on the physical location of the bots, the channels used for sending the messages will vary. For example, bots seperated on different physical devices will need to use HTTP or something similar to send messages while bots in the same execution environment can use the execution environment to send messages. The message structure and channel definitions shall be variable to facilitate these necessaties.

## Message Propagation
This section has been moved to a seperate file in documentation\information_propagation.md.