# Network Connectivity Levels
A core principle of networks is cooperation amongst nodes. As such, nodes will need to transfer information between each other. To facilitate this, nodes will need to be aware of each other. Depending on the level of connectivity between nodes, various network types can be defined, including:
- Fully Connected Networks
- Partially Connected Networks
- Centralized Networks

## Node Isolation
Node isolation is when a node becomes isolated from the network. This occurs when no other node in the network has a connection to the isolated node. In this case, the node needs to reconnect to the network by connecting to a new node.

## Network Types
### Fully Connected Networks
In a fully connected network, each node is aware of every other node in the network. Nodes are directly connected to each other.

Pros:
- No intermediaries are required to facilitate communication. Nodes can communicate directly with each other as needed.
- Low risk of node isolation as every single node would need to be disconnected from the isolated node.

Cons:
- Overhead in ensuring that each node is updated when new nodes are added or removed from the network.
- Memory usage of node connections scales linearly with each new node added to the network.

### Partially Connected Networks
In a partially connected network, each node is connected to at least one other node in the network but there are no guarantees that it is connected to every other node in the network. It is assured that each node can communicate with every other node in the network, but intermediaries may be required to facilitate the communication.

Pros:
- Low memory usage in node connections as nodes require as low as one connection.
- Allows for flexible data flows when there is prior knowledge of how data will flow.

Cons:
- Intermediaries are required for communication. In a worse case scenario, the nodes in the network form more of a chain then a network and messages may need to pass through every other node in the network to get from node X to node Y.
- High risk of node isolation as there is a chance only one node was connected to the isolated node.
- Nodes are not aware of path required to send data to every other node, so messages need to be broadcast across the network.

### Centralized Networks
In a centralized network, all nodes are connected to a single central node that facilitates all communication.

Pros:
- Low memory usage in node connections as nodes are only connected to one other node.
- Connecting to the network requires minimal time.

Cons:
- If the central node crashes, the network fails.
- Central node is a bottleneck in communication.