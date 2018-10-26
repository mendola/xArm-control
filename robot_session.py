#! /usr/bin/env python3
from time import sleep
import cmd

from RobotArm import RobotArm


class RobotSession(cmd.Cmd):
    intro = 'xArm Session initiated. Enter <help> or <?> to list commands. \n'
    prompt = 'Input Command: '
    arm = RobotArm()

    def do_poll(self, _line):
        """ Poll the position of each motor. """
        self.arm.request_positions()
        sleep(0.1)
        self.arm.receive_serial()

    def default(self, line):
        print(f'*** Command <{line}> not recognized ***')


def main():
    RobotSession().cmdloop()


if __name__ == '__main__':
    main()
