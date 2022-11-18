import sys
import tty
import os
import termios





try:
    while True:
        k = getkey()
        print("Detected key: {}".format(k))
        if k == 'esc':
            quit()
        else:
            print(k)
except (KeyboardInterrupt, SystemExit):
    os.system('stty sane')
    print('stopping.')
