#! /usr/bin/env python3
import sys
import cmd2
import argparse
import logging
from os import path
from time import sleep
from typing import Any, Dict, IO, List, Union
from cmd2 import Statement, with_argparser, with_category
from argparse import ArgumentParser, Namespace

from Point import Point
from RobotArm import RobotArm

from definitions import motor_names
import packetmaker as pk


class CreatePoint(argparse.Action):  # pragma: no cover
    def __init__(self, option_strings: str, dest: str, **kwargs: Any):
        super(CreatePoint, self).__init__(option_strings, dest, **kwargs)

    # noinspection PyMethodOverriding
    def __call__(self, _parser, namespace: Namespace, values: List[float], _option_string):  # type: ignore
        if self.dest == 'cart':
            setattr(namespace, 'point', Point(cartesian=values))
        elif self.dest == 'cyl':
            setattr(namespace, 'point', Point(cylindrical=values))
        elif self.dest == 'sphere':
            setattr(namespace, 'point', Point(spherical=values))
        else:
            raise TypeError(f'Flag not recognized: {self.dest}')


class RobotSession(cmd2.Cmd):
    intro: str = 'xArm Session initiated. Enter <help> or <?> to list commands. \n'
    prompt: str = ' (xArm) '

    # ----------------------------------------------- Argument Parsers ----------------------------------------------- #
    motor_parser: ArgumentParser = ArgumentParser()
    motor_parser.add_argument('--base',     nargs='?', type=float, help="Base motor's angle in degrees")
    motor_parser.add_argument('--shoulder', nargs='?', type=float, help="Shoulder motor's angle in degrees")
    motor_parser.add_argument('--elbow',    nargs='?', type=float, help="Elbow motor's angle in degrees")
    motor_parser.add_argument('--wrist',    nargs='?', type=float, help="Wrist motor's angle in degrees")
    motor_parser.add_argument('--hand',     nargs='?', type=float, help="Hand motor's angle in degrees")
    motor_parser.add_argument('--fingers',  nargs='?', type=float, help="Fingers motor's angle in degrees")
    motor_parser.add_argument('-t', '--time', nargs='?', type=int, default=1000, help='Time interval in milliseconds.')
    motor_parser.add_argument('-r', '--return', action='store_true', help='Returns arm to upwards position.')

    point_parser: ArgumentParser = ArgumentParser()
    point_group = point_parser.add_mutually_exclusive_group()
    point_group.add_argument('--cart', nargs=3, type=float, action=CreatePoint, metavar=('X', 'Y', 'Z'),
                             help="Define a cartesian coordinate: (X, Y, Z)")
    point_group.add_argument('--cyl', nargs=3, type=float, action=CreatePoint, metavar=('R', 'THETA', 'Z'),
                             help="Define a cylindrical coordinate: (R, THETA, Z)")
    point_group.add_argument('--sphere', nargs=3, type=float, action=CreatePoint, metavar=('RHO', 'AZIMUTH', 'THETA'),
                             help="Define a spherical coordinate: (RHO, AZIMUTH, THETA)")
    point_parser.add_argument('-a', '--angle', nargs='?', type=float, default=0.0, help='Angle of approach.')
    point_parser.add_argument('-o', '--offset', nargs='?', type=float, default=0.0, help='Offset from target point.')
    point_parser.add_argument('-t', '--time', nargs='?', type=int, default=1000, help='Time interval in milliseconds.')
    point_parser.add_argument('-f', '--fingers', nargs='?', type=float, default=None, help='Finger Position in degrees')
    point_parser.add_argument('--hand', nargs='?', type=float, default=None, help='Hand Position in degrees')

    # ----------------------------------------------- Argument Parsers ----------------------------------------------- #

    def __init__(self, stdin: IO = sys.stdin, stdout: IO = sys.stdout):
        self.arm: RobotArm = RobotArm()
        super().__init__(stdin=stdin, stdout=stdout)
        self.log: logging.Logger = logging.getLogger("RobotSession")

    @with_category('xArm Commands')
    def do_poll(self, _statement: Statement) -> None:
        """ Poll the position of each motor. """
        try:
            self.arm.request_positions()
            sleep(0.1)
            self.arm.receive_serial()
            print(self.arm.State)
        except RuntimeError:
            self.log.error('RuntimeError: Skipping poll command.')

    @with_category('xArm Commands')
    @with_argparser(motor_parser)
    def do_move(self, motors: Union[Namespace, str]) -> None:
        """ Move the arm to the position specified. Provide space separated angle for each motor. """
        degrees_dict: Dict[str, float] = vars(self.arm.State)
        # ^ This is pointing to the State object, so will update the state on each move.
        motors_dict: Dict[str, Any] = \
            {key: value for key, value in vars(motors).items() if value is not None}
        interval: int = motors_dict.pop('time')
        upright: bool = motors_dict.pop('return')
        if upright:
            motors_dict = {motor: 0 for motor in motor_names[1:]}
        degrees_dict.update(motors_dict)

        try:
            self.arm.send(pk.write_servo_move(degrees_dict, interval))
        except RuntimeError:
            self.log.error('RuntimeError: Skipping move_to_point command.')

    @staticmethod
    def help_move() -> None:  # pragma: no cover
        print(f'Move the arm to the position specified.\n'
              f'Provide space separated angle for each of the following:\n'
              f'  ({", ".join(motor_names[1:])})')

    @with_category('xArm Commands')
    @with_argparser(point_parser)
    def do_move2point(self, arguments: Namespace) -> None:
        """ Move the arm to the point specified. """
        try:
            pose = self.arm.move_to_point(arguments.point, arguments.time, arguments.fingers, arguments.hand)
            self.log.info(pose)
        except RuntimeError:
            self.log.error('RuntimeError: Skipping move_to_point command.')

    @staticmethod
    def help_move2point() -> None:  # pragma: no cover
        print(f'Move the arm to the point specified. \n'
              f'  First argument should be one of: \n'
              f'    * --cart X Y Z \n'
              f'    * --cyl R THETA Z \n'
              f'    * --sphere R AZIMUTH THETA \n'
              f'  Second argument should be time to move in milliseconds: \n'
              f'    * -t TIME')

    @with_category('xArm Commands')
    @with_argparser(point_parser)
    def do_approach(self, arguments: Namespace) -> None:
        """ Approach the arm from a given angle with a given offset. """
        try:
            self.arm.approach_from_angle(arguments.point, arguments.angle, arguments.time, arguments.offset, arguments.fingers, arguments.hand)
        except RuntimeError:
            self.log.error('RuntimeError: Skipping approach command.')

    @staticmethod
    def help_approach() -> None:  # pragma: no cover
        print(f'Approach the point specified from the angle specified. \n'
              f'  First argument should be one of: \n'
              f'    * --cart X Y Z \n'
              f'    * --cyl R THETA Z \n'
              f'    * --sphere R AZIMUTH THETA \n'
              f'  Second argument should the angle of approach, measured from the horizontal: \n'
              f'    * -a ANGLE \n'
              f'  Third argument should be time to move in milliseconds: \n'
              f'    * -t TIME')

    @with_category('xArm Commands')
    def do_unlock(self, statement: Statement) -> None:
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
    def help_unlock() -> None:  # pragma: no cover
        print(f'Unlock individual motors of the arm.\n' 
              f'Provide space separated names for any combination of:\n'
              f'  ({", ".join(motor_names[1:])})\n'
              f'The default is all motors.')

    def do_eof(self, _statement: Statement) -> bool:  # pragma: no cover
        """ Exit CLI. """
        print()
        return self._STOP_AND_EXIT

    def default(self, statement: Statement) -> None:  # pragma: no cover
        print(f'*** Command <{statement.command}> not recognized ***')


def main() -> None:  # pragma: no cover
    logging.basicConfig(level=logging.INFO,
                        format=f'[%(levelname)s] {path.basename(__file__)} %(funcName)s: \n%(message)s')
    try:
        RobotSession().cmdloop()
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    main()
