import argparse
# from pynput import keyboard
import qi
import sys
import os
import tty
import termios
from time import sleep


class Pepper:
    session = None
    motion_service = None
    auton_service = None
    tts = None

    def __init__(self, ip, port):
        self.session = qi.Session()
        try:
            print("Connecting to Pepper at {ip}:{port}".format(
                ip=ip, port=port))
            self.session.connect(
                "tcp://{ip}:{port}".format(ip=ip, port=str(port)))
            print("Connected!")
        except RuntimeError:
            print("Unable to connect to Pepper.")
            sys.exit(1)
        self.motion_service = self.session.service("ALMotion")
        self.auton_service = self.session.service("ALAutonomousMoves")
        self.posture_service = self.session.service("ALRobotPosture")
        self.tts = self.session.service("ALTextToSpeech")
        self.tablet_service = self.session.service("ALTabletService")
        self.tablet_service.enableWifi()
        print("Wifi On")
        self.tablet_service.loadURL("https://www.google.com")
        self.tablet_service.showWebview()
        sleep(3)

    def move_forward(self, speed):
        print("Moving")
        self.motion_service.moveToward(speed, 0, 0)

    def turn_around(self, speed):
        print("Turning")
        self.motion_service.moveToward(0, 0, speed)

    def stop_moving(self):
        print("Stopping")
        self.motion_service.stopMove()

    def disable_collision_protection(self):
        print("Disabling collision protection")
        self.motion_service.setExternalCollisionProtectionEnabled("All", False)

    def sleep(self, duration):
        sleep(duration)
        self.stop_moving()

    def speak(self, text):
        self.tts.say(text)

    def open_tip_screen(self):
        self.tablet_service.loadUrl("http://snibo.me/pepper-1.html")

    def enable_collision_protection(self):
        print("Enabling collision protection")
        self.auton_service.setBackgroundStrategy("backToNeutral")
        self.motion_service.setExternalCollisionProtectionEnabled("All", True)

    def stand(self):
        print("Applying Standing posture")
        self.posture_service.applyPosture("StandZero", 0.5)

    def on_keypress(self, key):
        if key == 'w':
            self.move_forward(1)
            self.sleep(1)
        elif key == 's':
            self.move_forward(-1)
            self.sleep(1)
        elif key == 'a':
            self.turn_around(1)
            self.sleep(1.3)
        elif key == 'd':
            self.turn_around(-1)
            self.sleep(1.3)
        elif key == '1':
            self.speak("Hi, May I take your order")
        elif key == '2':
            self.speak("Alright. One Moment Please")
        elif key == '3':
            self.open_tip_screen()

    def getkey(self):
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        try:
            while True:
                b = os.read(sys.stdin.fileno(), 3).decode()
                if len(b) == 3:
                    k = ord(b[2])
                else:
                    k = ord(b)
                key_mapping = {
                    127: 'backspace',
                    10: 'return',
                    32: 'space',
                    9: 'tab',
                    27: 'esc',
                    65: 'up',
                    66: 'down',
                    67: 'right',
                    68: 'left'
                }
                return key_mapping.get(k, chr(k))
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    def start_teleop(self):
        print("Disabling collision protection and starting teleop.")
        print(
            "W: forward, S: backward, A: turn left, D: turn right, 1: say hi, 2: say bye"
        )
        print("Press esc to exit.")
        self.disable_collision_protection()

        try:
            while True:
                k = self.getkey()
                if k == 'esc':
                    quit()
                else:
                    print(k)
                    self.on_keypress(k)
        except (KeyboardInterrupt, SystemExit):
            self.enable_collision_protection()
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="teleop.py",
        description="Teleoperation script for Pepper Robot.",
    )
    parser.add_argument(
        "--ip", type=str, default="128.237.247.249", help="Pepper's IP address")
    parser.add_argument(
        "-p", "--port", type=int, default=9559, help="Pepper's port number"
    )

    args = parser.parse_args()
    robot = Pepper(args.ip, args.port)
    robot.start_teleop()
