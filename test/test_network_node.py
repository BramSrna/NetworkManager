import logging
import unittest

from test.network_node_test_class import NetworkNodeTestClass


class TestNetworkNode(NetworkNodeTestClass):
    def test_error_will_be_raised_when_startup_is_called_while_node_is_runnging(self):
        test_network_node_1 = self.create_network_node()

        with self.assertRaises(Exception) as raised_error:
            test_network_node_1.startup()

        self.assertIn("Network node is already running", str(raised_error.exception))

    def test_assert_connecting_to_a_node_will_form_a_one_way_connection(self):
        test_network_node_1 = self.create_network_node()
        test_network_node_2 = self.create_network_node()

        test_network_node_1.connect_to_network_node(test_network_node_2)

        self.assertTrue(test_network_node_1.is_connected_to(test_network_node_2.get_id()))
        self.assertFalse(test_network_node_2.is_connected_to(test_network_node_1.get_id()))

    def test_assert_disconnecting_from_a_node_will_only_delete_the_connection_in_one_direction(self):
        test_network_node_1 = self.create_network_node()
        test_network_node_2 = self.create_network_node()

        test_network_node_1.connect_to_network_node(test_network_node_2)
        test_network_node_2.connect_to_network_node(test_network_node_1)

        self.assertTrue(test_network_node_1.is_connected_to(test_network_node_2.get_id()))
        self.assertTrue(test_network_node_2.is_connected_to(test_network_node_1.get_id()))

        test_network_node_1.disconnect_from_network_node(test_network_node_2.get_id())

        self.assertFalse(test_network_node_1.is_connected_to(test_network_node_2.get_id()))
        self.assertTrue(test_network_node_2.is_connected_to(test_network_node_1.get_id()))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
