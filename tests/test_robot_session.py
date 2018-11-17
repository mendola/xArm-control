import mock
import snapshottest
from cmd2 import Statement
from sys import stdin, stdout
from serial import SerialException

from robot_session import RobotSession
from Point import Point


# noinspection PyUnresolvedReferences
class TestRobotSession(snapshottest.TestCase):
    def setUp(self):
        self.mock_stdin = mock.create_autospec(stdin)
        self.mock_stdout = mock.create_autospec(stdout)

    @mock.patch('RobotArm.Serial')
    def create(self, mocked_serial):
        mocked_serial.return_value = mock.MagicMock()
        mocked_serial.return_value.inWaiting.return_value = False
        mocked_serial.return_value.write = mock.MagicMock()
        return RobotSession(stdin=self.mock_stdin, stdout=self.mock_stdout)

    @mock.patch('RobotArm.Serial', side_effect=SerialException())
    def no_serial_create(self, mocked_serial):
        mocked_serial.return_value = mock.MagicMock()
        mocked_serial.return_value.inWaiting.return_value = False
        mocked_serial.return_value.write = mock.MagicMock()
        return RobotSession(stdin=self.mock_stdin, stdout=self.mock_stdout)

    @mock.patch('robot_session.print')
    def test_poll(self, mocked_print):
        """ Test that poll returns expected results. """
        # Arrange
        no_serial_session = self.no_serial_create()
        session = self.create()

        # Act
        no_serial_session.do_poll(Statement(''))
        session.do_poll(Statement(''))

        # Assert
        self.assertTrue(len(mocked_print.call_args_list) == 1)
        self.assertMatchSnapshot(str(mocked_print.call_args_list[0]))

    def test_move(self):
        """ Test that move sends the expected command. """
        # Arrange
        no_serial_session = self.no_serial_create()
        session = self.create()
        move_command = '--fingers 100 --base 50 --elbow 10 --shoulder -30 --wrist -110 --hand 0 -t 500'
        return_command = '-r'

        # Act
        no_serial_session.do_move(move_command)
        session.do_move(move_command)
        session.do_move(return_command)

        # Assert
        self.assertTrue(len(session.arm.Ser.write.call_args_list) == 2)
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[0]))
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[1]))

    # noinspection PyTypeChecker
    def test_move2point(self):
        """ Test that move2point sends the expected arguments to the arm. """
        # Arrange
        no_serial_session = self.no_serial_create()
        session = self.create()

        test_command = '--cart 10 10 10 -t 150'
        test_point = Point(cartesian=(10, 10, 10))
        test_time = 150

        # Act
        no_serial_session.do_move2point(test_command)

        with mock.patch('RobotArm.RobotArm.move_to_point') as mocked_move_to_point:
            session.do_move2point(test_command)

            # Assert
            self.assertEqual((test_point, test_time), mocked_move_to_point.call_args[0])

    # noinspection PyTypeChecker
    def test_approach(self):
        """ Test that approach sends the expected command. """
        # Arrange
        no_serial_session = self.no_serial_create()
        session = self.create()

        test_command = '--cart 10 10 10 -a -30 -t 150'
        test_point = Point(cartesian=(10, 10, 10))
        test_angle = -30
        test_time = 150
        test_offset = 0.0

        # Act
        no_serial_session.do_approach(test_command)

        with mock.patch('RobotArm.RobotArm.approach_from_angle') as mocked_approach_from_angle:
            session.do_approach(test_command)

            # Assert
            self.assertEqual((test_point, test_angle, test_time, test_offset), mocked_approach_from_angle.call_args[0])

    def test_unlock(self):
        """ Test that unlock sends the expected command. """
        # Arrange
        no_serial_session = self.no_serial_create()
        session = self.create()
        unlock_command = Statement("fingers base shoulder")

        # Act
        no_serial_session.do_unlock(Statement(''))
        session.do_unlock(Statement(''))
        session.do_unlock(unlock_command)

        # Assert
        self.assertTrue(len(session.arm.Ser.write.call_args_list) == 2)
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[0]))
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[1]))
