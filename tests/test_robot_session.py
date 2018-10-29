import mock
import snapshottest
from cmd2 import Statement
from sys import stdin, stdout

from robot_session import RobotSession


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

    @mock.patch('robot_session.print')
    def test_poll(self, mocked_print):
        """ Test that poll returns expected results. """
        # Arrange
        no_serial_session = RobotSession()
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
        no_serial_session = RobotSession()
        session = self.create()
        move_command = Statement("100 50 10 -30 -110 0")

        # Act
        no_serial_session.do_move(move_command)
        session.do_move(move_command)

        # Assert
        self.assertTrue(len(session.arm.Ser.write.call_args_list) == 1)
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[0]))

    def test_unlock(self):
        """ Test that unlock sends the expected command. """
        # Arrange
        no_serial_session = RobotSession()
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