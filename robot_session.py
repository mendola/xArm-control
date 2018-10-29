#! /usr/bin/env python3
import sys
import cmd2
from time import sleep
from typing import Dict, List
from cmd2 import Statement

from definitions import motor_ids, motor_names
import packetmaker as pk


from RobotArm import RobotArm


class RobotSession(cmd2.Cmd):
    intro: str = 'xArm Session initiated. Enter <help> or <?> to list commands. \n'
    prompt: str = ' (xArm) '

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout) -> None:
        self.arm: RobotArm = RobotArm()
        super().__init__(stdin=stdin, stdout=stdout)

    def do_poll(self, _statement: Statement):
        """ Poll the position of each motor. """
        try:
            self.arm.request_positions()
            sleep(0.1)
            self.arm.receive_serial()
            print(self.arm.State)
        except RuntimeError:
            pass

    def do_move(self, statement: Statement):
        """ Move the arm to the position specified. Provide space separated angle for each motor. """
        angles: List[float] = [float(angle) for angle in statement.args.split(' ')]
        assert len(angles) == len(motor_ids), f"Must input an angle for each motor: {motor_names[1:]}"

        degrees_dict: Dict[str, float] = {motor: angle for motor, angle in zip(motor_names[1:], angles)}
        try:
            self.arm.send(pk.write_servo_move(degrees_dict, 500))
        except RuntimeError:
            pass

    @staticmethod
    def help_move():  # pragma: no cover
        print(f'Move the arm to the position specified.\n'
              f'Provide space separated angle for each of the following:\n'
              f'  ({", ".join(motor_names[1:])})')

    def do_unlock(self, statement: Statement):
        """ Unlock servo motors. """
        input_motors: List[str] = [motor for motor in statement.args.split()]
        assert all([motor in motor_names for motor in input_motors]), \
            f'Input motors must be one of {motor_names[1:]}. Found: {input_motors}'

        try:
            if len(input_motors) == 0:
                self.arm.unlock_servos()
            else:
                self.arm.send(pk.write_servo_unlock(input_motors))
        except RuntimeError:
            pass

    @staticmethod
    def help_unlock():  # pragma: no cover
        print(f'Unlock individual motors of the arm.\n' 
              f'Provide space separated names for any combination of:\n'
              f'  ({", ".join(motor_names[1:])})\n'
              f'The default is all motors.')

    def do_eof(self, _statement: Statement) -> bool:  # pragma: no cover
        """ Exit CLI. """
        print()
        return self._STOP_AND_EXIT

    def do_exit(self, _statement: Statement) -> bool:  # pragma: no cover
        """ Exit CLI. """
        return self._STOP_AND_EXIT

    def default(self, statement: Statement):  # pragma: no cover
        print(f'*** Command <{statement.command}> not recognized ***')


def main():  # pragma: no cover
    try:
        RobotSession().cmdloop()
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    main()
