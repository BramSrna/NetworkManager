# Important Note
Development for this has been moved to https://github.com/BramSrna/Swarm

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
```python
from network_manager.network_manager import NetworkManager
from network_manager.network_connectivity_level import NetworkConnectivityLevel
from network_manager.network_node.network_node import NetworkNode

manager = NetworkManager(NetworkConnectivityLevel.FULLY_CONNECTED)

node_1 = NetworkNode()
node_2 = NetworkNode()
node_3 = NetworkNode()

manager.add_network_node(node_1)
manager.add_network_node(node_2)
manager.add_network_node(node_3)

def simple_handler(swarm_bot, message):
    print("HELLO WORLD FROM {}! Received payload: {}".format(swarm_bot.get_id(), message.get_message_payload()))

msg_type = "MESSAGE_TYPE"

node_2.assign_msg_handler(msg_type, simple_handler)
node_3.assign_msg_handler(msg_type, simple_handler)

node_1.create_propagation_message(msg_type, {"PAYLOAD_KEY": "PAYLOAD_VALUE"})

manager.wait_for_idle_network()

manager.teardown()
```

## Running tests
```bash
pytest
```
