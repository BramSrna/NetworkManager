# Swarm Connectivity Levels
A core principle of swarm robotics is cooperation amongst bots. As such, bots will need to transfer information between each other. To facilitate this, bots will need to be aware of each other. Depending on the level of connectivity between bots, various swarm types can be defined, including:
- Fully Connected Swarms
- Partially Connected Swarms
- Centralized Swarms
- ML-Enabled Variable Connectivity Swarms

## Bot Isolation
Bot isolation is when a bot becomes isolated from the swarm. This occurs when no other bot in the swarm has a connection to the isolated bot. In this case, the bot needs to reconnect to the swarm.

## Swarm Types
### Fully Connected Swarms
In a fully connected swarm, each bot is aware of every other bot in the swarm. Bots are directly connected to each other.

Pros:
- No intermediaries are required to facilitate communication. Bots can communicate directly with each other as needed.
- Low risk of bot isolation as every single bot would need to be disconnected from the isolated bot.

Cons:
- Overhead in ensuring that each bot is updated when new bots are added or removed from the swarm.
- Memory usage of bot connections scales linearly with each new bot added to the network.

### Paritally Connected Swarms
In a partially connected swarm, each bot is connected to at least one other bot in the swarm but there are no guarantees that it is connected to every other bot in the network. It is assured that each bot can communicate with every other bot in the swarm, but intermediaries may be required to facilitate the communication.

Pros:
- Low memory usage in bot connections as bots require as low as one connection.
- Allows for flexible data flows when there is prior knowledge of how data will flow.

Cons:
- Intermediaries are required for communication. In a worse case scenario, the bots in the swarm form more of a chain then a swarm and messages may need to pass through every other bot in the swarm to get from bot X to bot Y.
- High risk of bot isolation as there is a chance only one bot was connected to the isolated bot.
- Bots are not aware of path required to send data to every other bot, so messages need to be broadcast across the network.

### Centralized Swarms
In a centralized swarm, all bots are connected to a single central bot that facilitates all communication.

Pros:
- Low memory usage in bot connections as bots are only connected to one other bot.
- Connecting to the swarm requires minimal time.

Cons:
- If the central bot crashes, the swarm fails.
- Central bot is a bottleneck in communication.

### ML-Enabled Variable Connectivity Swarms
In a ML-enabled variable connectivity swarm, bots connect and disconnect from each other as needed depending on the flow of data. For example, if two bots do not communicate with each other, or rarely communicate with each other, then they may disconnect from each other and use intermediaries when needed.

Pros:
- Optimum connections are generally maintained.
- Algorithmic protection against bot isolation.

Cons:
- Extremely heavy overhead of running the ML in the background.
- Connections will need to be remade if data flow changes.
