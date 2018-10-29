from RobotArm import RobotArm
import time

xArm = RobotArm()
for i in range(3):
	xArm.poweroff_servos()
	time.sleep(0.5)

print("Motors should be relaxed")
	
