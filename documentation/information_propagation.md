# Information Propagation
To support a variety of functionality, bots will need to be able to broadcast information to the whole swarm either for a form of messaging or for information sharing. There are a variety of areas to address with information propagation:
- The strategy used for propagation
- Ensuring the information is propagated to the entire network while minimizing circular messaging
There are also some related areas:
- Message validation and evaluation to ensure it was received from a trusted source
- Handling conflicting messages

## Propagation Strategy
### Naive Propagation
#### Description
The most starightforward form of message propagation is naive propagation. The strategy used for propagation is as follows:
1. Source bot sends the message to each bot it is connected to
2. When a bot receives the message:
    - If receiving the message for the first time
        - Send the message to each connected bot
    - If receiving the message a subsequent time
        - Ignore the message

The benefit to this method is that it is very resilient to connection issues. If a connection is slow or broken, the message will be propagated using a different path if available. Additionally, messages will naturally follow the shortest path to each bot. The downside to this method is that there will be a lot of repeated message sending.

#### Implementation
The Naive Propagation implementation can be seen here: swarm_bot\src\propagation_strategy\naive_propagation.py

#### Expected Messaging Count
Where N is the number of bots a bot is connected to:
Source bot:
- Send: N - 1 messages
- Receive: N - 1 messages
- Ignore: N - 1 messages

Receiver bots:
- Send: N - 1 messages
- Receive: N - 1 messages
- Ignore: N - 2 messages

### Smart Propagation
Smart Propagation is the same as Naive Propagation with two additional strategies used to increase efficiency:
- Remove message echoing: In Naive Propagation, the receiver bot sends the message to every bot it is connected to, including the source bot. Since the bot knows that the source bot has already received the message, it does not need to receive it again. This will help to decrease the number of unnecessary messages sent.
- Prioritize the order that messages are sent to the connected bots: When a bot receives a propagated message that it has already dealt with, it will ignore the message. By tracking when these messages are received and which bot sent them, the receiver bot can get a rough estimate of the second shortest path to the sender bot. Then when sending out a message, the source bot can start with the bots that have no second path or have a very long second path before moving onto the ones with short second paths. This strategy will decrease the amount of times it takes to fully propagate a message while maintaining the reslience offered by naive propagation.

The strategy used for propagation is as follows:
1. Source bot sends the message to each bot it is connected to
2. When a bot receives the message:
    - If receiving the message for the first time: 
        - Send the message to each connected bot, excluding the sender bot, in descending order according to the average message receive time for each bot
        - Record the time when the message was received
        - Calculate the new average time for the bot
    - If receiving the message a subsequent time:
        - Calculate the difference in time from when the message was first received and when it was subsequentally received
        - Calculate the new average time for the bot

#### Implementation
The Smart Propagation implementation can be seen here: swarm_bot\src\propagation_strategy\smart_propagation.py

#### Expected Messaging Count
Where N is the number of bots a bot is connected to:
Source bot:
- Send: N - 1 messages
- Receive: 0
- Ignore: 0

Receiver bots:
- Send N - 2 messages
- Receive N - 1 messages
- Ignore N - 2 messages


## Ensuring Full Network Propagation
Ensuring full-network message propagation is difficult in a decentralized network. Since data can follow different paths and bots may not have knowledge of every other bot in the network, the swarm will need to have a mechanism to ensure full network propagation. There are a few ways to implement this mechanism:
- System Syncing: Bots will maintain a history of the messages they have received. Then periodically or based on a trigger, the bots will sync their history with the their connected bots to ensure message propagation. This can still introduce bubbles or lag for message propagation, but helps as an extra layer of verification.
- Trailing Ledger: In the trailing ledger strategy, the swarm periodically propagates a sinle message containing a ledger. The ledger keeps track of all the propagated messages and a list of bots that have received them. If it finds a message that has not been received by a bot, then the missing message is sent to that bot. For this mmethod to be effective, the message containing the ledger is propagated bot-by-bot. The issue with this method is that it violates the bot knowledge limit.
