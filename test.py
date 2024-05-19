
import time

def test():
    frameskip = int(os.environ["FRAMESKIP"])
    framecount = frameskip-1
    while True:
        time.sleep(1)
        framecount += 1
        if framecount != frameskip:
            continue
        if framecount >= frameskip:
            framecount = 0
            

test()


# ! FRAMESKIP
frameskip = int(os.environ["FRAMESKIP"])
framecount = frameskip-1

framecount += 1
if framecount != frameskip:
    continue
if framecount >= frameskip:
    framecount = 0