import unittest

from network_node.src.network_node import NetworkNode
from network_node.src.network_node_idle_listener_interface import NetworkNodeIdleListenerInterface

"""
NetworkNodeTestClass

Wrapper class for test classes that use NetworkNode objects.
Provides support for ensuring the nodes are torn down properly.
"""


class NetworkNodeTestClass(unittest.TestCase, NetworkNodeIdleListenerInterface):
    def setUp(self) -> None:
        """
        setUp

        Called before each test case. Initializes
        the test class as a NetworkNodeIdleListenerInterface

        @param None

        @return None
        """
        NetworkNodeIdleListenerInterface.__init__(self)
        self.test_network_nodes = []

    def tearDown(self) -> None:
        """
        tearDown

        Called after each test class. Tears down all nodes
        created by the test class.

        @param None

        @return None
        """
        for node in self.test_network_nodes:
            node.teardown()

    def create_network_node(self, additional_config_dict: dict = {}) -> NetworkNode:
        """
        create_network_node

        Creates a new network node using the given additional config
        information and adds it to the test cases list of nodes.

        @param additional_config_dict [dict] Additional config information for the node

        @return [NetworkNode] The newly created network node
        """
        new_node = NetworkNode(additional_config_dict=additional_config_dict)
        self.test_network_nodes.append(new_node)
        new_node.add_idle_listener(self)
        return new_node
