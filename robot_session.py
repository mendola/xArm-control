#! /usr/bin/env python3
import cmd
import sys
from os import system
from time import sleep
from typing import Dict, List

from definitions import motor_ids, motor_names
import packetmaker as pk


from RobotArm import RobotArm


class RobotSession(cmd.Cmd):
    intro: str = 'xArm Session initiated. Enter <help> or <?> to list commands. \n'
    prompt: str = 'Input Command: '

    def __init__(self, stdin=sys.stdin, stdout=sys.stdout) -> None:
        self.arm: RobotArm = RobotArm()
        super().__init__(stdin=stdin, stdout=stdout)

    def do_poll(self, _line: str):
        """ Poll the position of each motor. """
        self.arm.request_positions()
        sleep(0.1)
        self.arm.receive_serial()
        print(self.arm.State)

    def do_move(self, line: str):
        """ Move the arm to the position specified. Provide space separated angle for each motor. """
        angles: List[float] = [float(angle) for angle in line.split(' ')]
        assert len(angles) == len(motor_ids), f"Must input an angle for each motor: {motor_names[1:]}"

        degrees_dict: Dict[str, float] = {motor: angle for motor, angle in zip(motor_names[1:], angles)}
        self.arm.send(pk.write_servo_move(degrees_dict, 500))

    @staticmethod
    def help_move():  # pragma: no cover
        print(f'Move the arm to the position specified. '
              f'Provide space separated angle for each motor: '
              f'{", ".join(motor_names[1:])}')

    def do_unlock(self, line: str):
        """ Unlock servo motors. """
        input_motors: List[str] = [motor for motor in line.split()]
        assert all([motor in motor_names for motor in input_motors]), \
            f'Input motors must be one of {motor_names[1:]}. Found: {input_motors}'

        if len(input_motors) == 0:
            self.arm.unlock_servos()
        else:
            self.arm.send(pk.write_servo_unlock(input_motors))

    @staticmethod
    def help_unlock():  # pragma: no cover
        print(f'Unlock individual motors of the arm.' 
              f'Provide space separated names for each motor: '
              f'{", ".join(motor_names[1:])}. '
              f'The default is all motors.')

    @staticmethod
    def do_shell(shell_command: str):  # pragma: no cover
        """ Run a shell command. (! shell_command) """
        system(shell_command)

    @staticmethod
    def do_exit(_line: str) -> bool:  # pragma: no cover
        """ Exit CLI. """
        return True

    def default(self, line: str):  # pragma: no cover
        print(f'*** Command <{line}> not recognized ***')


def main():  # pragma: no cover
    RobotSession().cmdloop()


if __name__ == '__main__':
    main()
