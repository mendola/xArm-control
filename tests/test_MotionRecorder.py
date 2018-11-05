import mock
import snapshottest
from os import path
from tempfile import TemporaryDirectory

from MotionRecorder import MotionRecorder


class TestMotionRecorder(snapshottest.TestCase):
    test_motionpath = path.join(path.dirname(__file__), 'test_data', 'test_motionpath')

    @mock.patch('MotionRecorder.RobotArm.request_positions')
    @mock.patch('MotionRecorder.RobotArm.receive_serial')
    def test_try_update_state(self, mocked_receive_serial, mocked_request_positions):
        """ Test that try_update_state calls the expected RobotArm methods. """
        # Arrange & Act
        MotionRecorder().try_update_state()

        # Assert
        mocked_receive_serial.assert_called_once()
        mocked_request_positions.assert_called_once()

    @mock.patch('MotionRecorder.open')
    def test_load_pose_queue(self, mocked_open):
        """ Test that load_pose_queue loads a motion path as expected. """
        # Arrange
        mocked_open.side_effect = lambda _file, option: open(self.test_motionpath, option)
        recorder = MotionRecorder()

        # Act
        recorder.load_pose_queue('this_file_is_already_mocked')

        # Assert
        self.assertMatchSnapshot(str(recorder.pose_queue))

    @mock.patch('MotionRecorder.open')
    def test_save_pose_queue(self, mocked_open):
        """ Test that load_pose_queue loads a motion path as expected. """
        # Arrange
        with TemporaryDirectory() as tempdir:
            test_file = path.join(tempdir, 'temp_motionpath')
            mocked_open.side_effect = lambda _file, option: open(test_file, option)
            recorder = MotionRecorder()
            recorder.pose_queue.append({'motor': 'angle'})

            # Act
            recorder.save_pose_queue('this_file_is_already_mocked')

            # Assert
            self.assertTrue(path.isfile(test_file))
