import snapshottest
from packetmaker import *


class TestPacketMaker(snapshottest.TestCase):

    def test_with_header(self):
        """ Test that with_header properly prepends the header. """
        # Arrange
        test_packet = bytes(range(16))
        expected_packet = bytes([85, 85]) + test_packet

        @with_header
        def dummy_function(packet):
            return packet

        # Act & Assert
        self.assertEqual(expected_packet, dummy_function(test_packet))

    def test_write_servo_move(self):
        """ Test that write_servo_move returns an expected packet. """
        # Arrange
        degrees_dict = {
            'base': -111.11,
            'shoulder': -64,
            'elbow':  0,
            'wrist': 0.123456789,
            'hand': 90.0000000,
            'fingers': 99.9987,
        }

        # Act & Assert
        self.assertMatchSnapshot(write_servo_move(degrees_dict, 500))

    def test_write_servo_unlock(self):
        """ Test that write_servo_unlock returns an expected packet. """
        # Arrange
        test_joint_list = ['shoulder', 'fingers']

        # Act & Assert
        self.assertMatchSnapshot(write_servo_unlock())
        self.assertMatchSnapshot(write_servo_unlock(test_joint_list))

    def test_write_request_positions(self):
        """ Test that write_request_positions returns an expected packet. """
        # Arrange
        test_joint_list = ['shoulder', 'fingers']

        # Act & Assert
        self.assertMatchSnapshot(write_request_positions())
        self.assertMatchSnapshot(write_request_positions(test_joint_list))