import mock
import snapshottest
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
        session = self.create()

        # Act
        session.do_poll('')

        # Assert
        self.assertMatchSnapshot(str(mocked_print.call_args_list[0]))

    def test_move(self):
        """ Test that move sends the expected command. """
        # Arrange
        session = self.create()
        move_command = "100 50 10 -30 -110 0"

        # Act
        session.do_move(move_command)

        # Assert
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[0]))

    def test_unlock(self):
        """ Test that unlock sends the expected command. """
        # Arrange
        session = self.create()
        unlock_command = "fingers base shoulder"

        # Act
        session.do_unlock('')
        session.do_unlock(unlock_command)

        # Assert
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[0]))
        self.assertMatchSnapshot(str(session.arm.Ser.write.call_args_list[1]))
