# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['TestPacketMaker::test_write_servo_unlock 1'] = b'UU\t\x14\x06\x01\x02\x03\x04\x05\x06'

snapshots['TestPacketMaker::test_write_servo_unlock 2'] = b'UU\x05\x14\x02\x04\x01'

snapshots['TestPacketMaker::test_write_request_positions 1'] = b'UU\t\x15\x06\x01\x02\x03\x04\x05\x06'

snapshots['TestPacketMaker::test_write_request_positions 2'] = b'UU\x05\x15\x02\x04\x01'

snapshots['TestPacketMaker::test_write_servo_move 1'] = b'UU\x17\x03\x06\xf4\x01\x02%\x00\x04\xe9\x00\x03\xf4\x01\x05\xf5\x01\x06k\x03\x01\x95\x03'
