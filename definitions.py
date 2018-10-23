from os import path
from attrdict import AttrDict


ROOT_DIR = path.dirname(__file__)

commands = AttrDict({
    'move_servo': 3,
    'run_action_group': 6,
    'stop_action': 7,
    'action_speed': 11,
    'get_battery_voltage': 11,  # two 11's -- might be error in doc
    'unload_multiple_servo': 20,
    'read_multiple_servo_positions': 21
})

motor_id = AttrDict(
    {'base': 2, 'shoulder': 4, 'elbow': 3, 'wrist': 5, 'hand': 6, 'fingers': 1}
)

motor_names = {1 : 'fingers', 2: 'base', 3: 'elbow', 4: 'shoulder', 5 : 'wrist', 6 : 'hand'}