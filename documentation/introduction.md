# Introduction
Robots are often equipped with numerous sensors to track a wide variety data including external and internal data. In a robot swarm (https://en.wikipedia.org/wiki/Swarm_robotics), the amount of information scales with each new robot added to the swarm. This introduces an issue of information management in three regards:
1. What information to collect
2. What information to keep on the local machine
3. In the case of a centralized swarm: what information to send back to the central machine. In the case of a decentralized swarm: what information to store on the network.
4. How to parse the information for task and swarm improvement

This project is a bare bones implementation for defining data tensors to control how data is stored and flows to control what to do with the information.

## Data Tensors
The first issue with data storage and transmission is defining how data will be stored. Having a unified data model throughout the network simplifies the maintainance process as well as storage and parsing process. To facilitate this, the data transfer process should support a wide range of data types (JSON, XML, etc) in addition to supporting user defined models.

## Data Flows
Data flows define what the system shall do with data tensors as they are populated. The flows are rulesets that accompany the tensor collection definition and can be changed as needed.

## Data Propagatopm
Data propagation in the network is dependent on how the robots are connected to each other:
- Centralized Network: In this network configuration, all bots are directly connected a central computer. The individual bots are not directly connected to each other, but instead use the central computer as an intermediary.
- Fully-Connected Decentralized Network: In this network configuration, all bots are directly connected to each other. No intermdefiaries are needed as bots can communicate directly with each other.
- Partially-Connected Network: In this configuration, bots are directly connected to other bots, but are not connected to every bot. Every bot is still able to communicate with each other bot in the network, but other bots form a chain of intermediaries to allow for communication.


NOTE: Investigate data propagation methods in a swarm

