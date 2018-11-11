import mock
import unittest
from io import BytesIO
from serial import SerialException

from RobotArm import RobotArm, ensure_serial_connection
from definitions import commands


class TestRobotArm(unittest.TestCase):

    @mock.patch('RobotArm.RobotState')
    @mock.patch('RobotArm.Serial')
    def create(self, _mocked_serial, _mocked_state):
        """ Creates a RobotArms with mocked serial and state. """
        return RobotArm()

    @mock.patch('RobotArm.RobotState')
    @mock.patch('RobotArm.Serial')
    def test_try_except_serial(self, mocked_serial, _mocked_robot_state):
        """ Test that the try-except block of establishing serial connection. """
        # Arrange & Act
        test_arm = RobotArm()

        # Assert
        self.assertTrue(hasattr(test_arm, 'Ser'))

        # Arrange
        mocked_serial.side_effect = mock.Mock(side_effect=SerialException())

        # Act
        test_arm = RobotArm()

        # Assert
        self.assertFalse(hasattr(test_arm, 'Ser'))

    @mock.patch('RobotArm.ensure_serial_connection', side_effect=lambda func: func)
    @mock.patch('RobotArm.RobotState')
    @mock.patch('RobotArm.Serial', return_value=mock.MagicMock())
    def test_send(self, mocked_serial, _mocked_robot_state, _mocked_ensure_serial):
        """ Test that send passes the packet to the serial write. """
        # Arrange
        test_packet = bytes(range(10))
        test_arm = RobotArm()
        mocked_write = mocked_serial.return_value.write
        mocked_write.return_value = mock.MagicMock()

        # Act
        test_arm.send(test_packet)

        # Assert
        self.assertEqual((test_packet, ), mocked_write.call_args[0])

    @mock.patch('RobotArm.ensure_serial_connection', side_effect=lambda func: func)
    @mock.patch('RobotArm.RobotState')
    @mock.patch('RobotArm.RobotArm.handle_packet')
    @mock.patch('RobotArm.Serial')
    def test_receive_serial(self,  mocked_serial, mocked_handle, _mocked_robot_state, _mocked_ensure_serial):
        """ Test that receive_serial passes the expected message components to handle_packet. """
        # Arrange
        command_1, message_1 = 254, bytes(range(5))
        test_packet_1 = bytes([85, 85, 7, command_1]) + message_1
        command_2, message_2 = 255, bytes(range(10))
        test_packet_2 = bytes([85, 85, 12, command_2]) + message_2

        test_packets = test_packet_1 + bytes([131, 5, 100]) + test_packet_2

        class MockedSerial:
            def __init__(self, _port, _id):
                self.buffer = BytesIO(test_packets)

            def inWaiting(self):
                return len(self.buffer.getbuffer()) - self.buffer.tell()

            def read(self, n=1):
                return self.buffer.read(n)
        mocked_serial.side_effect = MockedSerial
        test_arm = RobotArm()

        # Act
        test_arm.receive_serial()

        # Assert
        self.assertEqual((command_1, message_1), mocked_handle.call_args_list[0][0])
        self.assertEqual((command_2, message_2), mocked_handle.call_args_list[1][0])

    @mock.patch('RobotArm.RobotArm.handle_position_packet')
    def test_handle_packet(self, mocked_handle_position):
        """ Test that handle_packet handles a serial packet as expected. """
        # Arrange
        invalid_command_code = -1
        valid_command_code = commands.read_multiple_servo_positions
        test_data = bytes(range(12))
        test_arm = self.create()

        # Act & Assert
        with self.assertRaises(NotImplementedError):
            test_arm.handle_packet(invalid_command_code, test_data)

        # Act
        test_arm.handle_packet(valid_command_code, test_data)

        # Assert
        self.assertEqual((test_data, ), mocked_handle_position.call_args[0])

    @mock.patch('RobotArm.Serial')
    @mock.patch('RobotArm.RobotState', return_value=mock.MagicMock())
    def test_handle_position_packet(self, mocked_state, _mocked_serial):
        """ Test that handle_position_packet decodes packets as expected. """
        # Arrange
        invalid_position_packet = bytes([100])
        valid_position_packet = bytes([3, 1, 35, 100, 2, 0, 0, 3, 100, 0])
        mocked_update_state = mocked_state.return_value.update_state
        test_arm = RobotArm()
        expected_degrees_dict = {'fingers': 120.0, 'base': -120.0, 'elbow': -96.0}

        # Act
        test_arm.handle_position_packet(invalid_position_packet)
        test_arm.handle_position_packet(valid_position_packet)

        # Assert
        self.assertEqual((expected_degrees_dict, ), mocked_update_state.call_args_list[0][0])

    @mock.patch('RobotArm.RobotArm.send')
    def test_send_beep(self, mocked_send):
        """ Test that send_beep sends an invalid command. """
        # Arrange
        proper_header = bytes([0x55, 0x55])
        test_arm = self.create()

        # Act
        test_arm.send_beep()

        # Assert
        self.assertNotEqual((proper_header, ), mocked_send.call_args[0])

    @mock.patch('RobotArm.RobotArm.send')
    @mock.patch('RobotArm.pk.write_servo_move', return_values=b'move')
    @mock.patch('RobotArm.get_pose_for_target_analytical', return_value=mock.MagicMock())
    def test_move_to_point(self, mocked_get_pose, mocked_write_servo_move, _mocked_send):
        """ Test that move_to_point tests valid messages as expected. """
        # Arrange
        test_time = 250
        test_arm = self.create()
        mocked_point = mock.MagicMock()
        mocked_computed_state = mocked_get_pose.return_value
        mocked_computed_state.is_state_safe.return_value = False

        # Act
        returned_state = test_arm.move_to_point(mocked_point, test_time)

        # Arrange
        mocked_computed_state.is_state_safe.return_value = True

        # Act
        returned_state = test_arm.move_to_point(mocked_point, test_time)

        # Assert
        self.assertIsInstance(returned_state, mock.MagicMock)
        self.assertEqual((vars(mocked_computed_state), test_time), mocked_write_servo_move.call_args[0])

    @mock.patch('RobotArm.pk.write_servo_unlock', return_values=b'unlock')
    @mock.patch('RobotArm.RobotArm.send')
    def test_unlock_servos(self, mocked_send, _mocked_write_servo_unlock):
        """ Test that unlock_servos sends an unlock message. """
        # Arrange
        test_arm = self.create()

        # Act
        test_arm.unlock_servos()

        # Assert
        self.assertNotEqual((b'unlock',), mocked_send.call_args[0])

    @mock.patch('RobotArm.pk.write_request_positions', return_values=b'request')
    @mock.patch('RobotArm.RobotArm.send')
    def test_unlock_servos(self, mocked_send, _mocked_write_request_positions):
        """ Test that request_positions sends a request message. """
        # Arrange
        test_arm = self.create()

        # Act
        test_arm.request_positions()

        # Assert
        self.assertNotEqual((b'unlock',), mocked_send.call_args[0])

    @mock.patch('RobotArm.RobotState')
    @mock.patch('RobotArm.Serial')
    def test_ensure_serial_connection(self, mocked_serial, _mocked_robot_state):
        """ Test that ensure_serial_connection correctly identifies the presence of a serial connection. """
        # Arrange
        @ensure_serial_connection
        def dummy_function(_robot_arm):
            return True

        test_arm = RobotArm()

        # Act & Assert
        self.assertTrue(dummy_function(test_arm))

        # Arrange
        mocked_serial.side_effect = mock.Mock(side_effect=SerialException())

        # Act
        test_arm = RobotArm()

        # Assert
        with self.assertRaises(RuntimeError):
            dummy_function(test_arm)