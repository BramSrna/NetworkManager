# NetworkManager
This module provides an extensible utility for deploying and controlling a network of nodes. Nodes can be added to a network connected in several different ways. Messages can then be sent between nodes or propagated to the entire network.

## Installation
```bash
git clone https://github.com/BramSrna/NetworkManager.git
cd NetworkManager
python3 setup.py develop
```

## Contributing
* Bugfixes are always welcome!
* New features, especially propagation strategies, are also welcome. Please make sure to add test cases as well.
* Test coverage is great. Please ensure tests are non-brittle.

## Example
from NetworkManager.network_manager import NetworkManager

manager = NetworkManager(NetworkConnectivityLevel.FULLY_CONNECTED)

node_1 = NetworkNode()
node_2 = NetworkNode()
node_3 = NetworkNode()

manager.add_network_node(node_1)
manager.add_network_node(node_2)
manager.add_network_node(node_3)

node_1.create_propagation_message("MESSAGE_TYPE", {"PAYLOAD_KEY": "PAYLOAD_VALUE"})

self.wait_for_idle_network()

## Running tests
```bash
python3 -m pytest
```
