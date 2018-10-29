# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestRobotSession::test_move 1'] = "call(b'UU\\x17\\x03\\x06\\xf4\\x01\\x01\\x95\\x03\\x02\\xc4\\x02\\x03\\x1e\\x02\\x04w\\x01\\x05*\\x00\\x06\\xf4\\x01')"

snapshots['TestRobotSession::test_poll 1'] = '''call(Servo fingers  : +0.00
Servo base     : +0.00
Servo elbow    : +0.00
Servo shoulder : +0.00
Servo wrist    : +0.00
Servo hand     : +0.00)'''

snapshots['TestRobotSession::test_unlock 1'] = "call(b'UU\\t\\x14\\x06\\x01\\x02\\x03\\x04\\x05\\x06')"

snapshots['TestRobotSession::test_unlock 2'] = "call(b'UU\\x06\\x14\\x03\\x01\\x02\\x04')"
