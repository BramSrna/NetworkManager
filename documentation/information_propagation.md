# Information Propagation
To support a variety of functionality, bots will need to be able to broadcast information to the whole swarm either for a form of messaging or for information sharing. There are a variety of areas to address with information propagation:
- The strategy used for propagation
- Ensuring the information is propagated to the entire network while minimizing circular messaging
There are also some related areas:
- Message validation and evaluation to ensure it was received from a trusted source
- Handling conflicting messages

## Propagation Strategy
For decentralized propagation, there are a variety of methods that can be used for propagation. The methods that can be employed will be limited depending on the physical nature and topology of the system. In terms of the propagation strategies, these include:
- Direct Messaging / Naive Propagation: The source bot delivers the message directly to every other bot in the swarm. This only works when the swarm is fully connected. In the case where the swarm is not fully connected, Naive Propagation can be used as a close counterpart. For Naive Propagation, the source bot delivers the message to just the bots it is connected to directly. These receiver bots then repeat the process. 
- Shortest Path Propagation: The swarm maintains a ledger containing the messaging history. This history is then used to determine the optimum path from a source bot to every other bot for use when propagating messages.
- Smart Propagation: Similar to shortest path propagation, but the path can be changed based on the current load on the machine.

## Ensuring Full Network Propagation
Ensuring full-network message propagation is difficult in a decentralized network. Since data can follow different paths and bots may not have knowledge of every other bot in the network, the swarm will need to have a mechanism to ensure full network propagation. There are a few ways to implement this mechanism:
- System Syncing: Bots will maintain a history of the messages they have received. Then periodically or based on a trigger, the bots will sync their history with the their connected bots to ensure message propagation. This can still introduce bubbles or lag for message propagation, but helps as an extra layer of verification.
- Trailing Ledger: In the trailing ledger strategy, the swarm periodically propagates a sinle message containing a ledger. The ledger keeps track of all the propagated messages and a list of bots that have received them. If it finds a message that has not been received by a bot, then the missing message is sent to that bot. For this mmethod to be effective, the message containing the ledger is propagated bot-by-bot.
