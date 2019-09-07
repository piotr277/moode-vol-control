#!/usr/local/bin/python3
# <bitbar.title>Moode audio player volume controller</bitbar.title>
# <bitbar.version>v1.0</bitbar.version>
# <bitbar.author>Piotr</bitbar.author>
# <bitbar.author.github>piotr277</bitbar.author.github>
# <bitbar.desc>This plugin allows volume controlling of local running Moode audio player. For more information about Moode check this: http://moodeaudio.org/</bitbar.desc>
# <bitbar.image>http://www.hosted-somewhere/pluginimage</bitbar.image>
# <bitbar.dependencies>python</bitbar.dependencies>
# <bitbar.abouturl>https://github.com/piotr277/</bitbar.abouturl>
import json
import requests
import sys
import os

# leave as it is if your moode and network supports mDNS or enter direct ip address
moodeUrl = "http://moode.local"
# set full path of this script
scriptFilepath = ""
# value for volume incrementation / decrementation
delta = 3

icon_online = "iVBORw0KGgoAAAANSUhEUgAAACQAAAAkCAQAAABLCVATAAAAAmJLR0QA/4ePzL8AAAAJcEhZcwAAFiUAABYlAUlSJPAAAAAHdElNRQfjCQcKKCCnZ5LwAAAEd0lEQVRIx5VWXWwUVRT+zp2Zndlu92922253t9uytaT/Lf2zEhVsIgrG1DbRRIsaqzUkihFJ0IgIVqMS39AHIxGUhBhMiMKLCSbyoI3Ellq0KRUVRcA20kJbW9ou3T0+7A7702mp9z7szbnnfPPde8757hKWGCwCjbPV82vmg1khwsxf2kV5IHvwdK9vwdyfzIwFeZGdY1tjEWlcPSUP2K8AUx5umG2KeoTF+6HSfWkEtxqlAFzfgfXfGiohb0v7zC5S5Poy/SzY1cdUsjRIHYDCl4gdp/KLAaBrkcfTAIDAKte3xIEdQKUZTDUAx36FA08CVcuyrgcQfExhxyfxE6SNWgCez+WJjTpWOB52yePuY0B55obzoDwBQECAEjO5okRSjFXiVx5zHAZeToKUIPiKwu2utMDMiRSIxHzGrrCvO4XNpAwueBRYxGJZGBBQ1AZ+05Y81o/ukynU43AisRIm4XnJCnQftw9zfBkIgkOFTViGUQqffGE9rfzLgggErEUoQBwoBADkHXH3pFR6GsCd+XXZKeAAger8gtVvkpw8J/QvATxnF1wVWAyjCMDxPrG8x+DjRZsKEAHO18Che41v1+QKbnchp4WmQ/LWVCBBBKryqX1gMN5IplvrU7+PQymj8qVcEQ9aLdGUdwPcO7Tf+ebJXpShPm4Bcu4mBmcCubaA/R0A4OiiaCDLiLINu3fD+UX+AcMQLo6HW6fBSAMqkHMJBGQNUaRRAflWgws6jLjgB7bjIlbq6DUMFz+Nc5u1pVd9jX30SnQPGFC3szSsA6PnCJObjH1PP8rEvKpcMAw3JPO+OjMlD1x7vVMSFPkTIqICgBqLhI398/1zmmBEoyvo0WjyHpkyFVGKkiy0BSm0rFwyUOm80aC/fSAaY0sRYuocwJgTyh+Gy6oq5bpYGJ6qNQy+vWQqxoNTud7ILhAwv5eipVcBXwnD9ZXh8ndZ7Bz0t+xDCaUG0KDA0uTIKdAuwCz9XWD/E0b6gzfT7x5wvwd9I01USIsqG7Z9tAhI61d/AEgAlhH5si9RkLUSruqtuCtHcLXTpNOQ+5CYSQAJCJAsWjQWRIDjVXDwfuNK6+2C1/gBuHryD5u2LNXZLGPubWmqICDqfYItJ5O58X/k/jne/SXE5d4HTfufEc4Ad0vWM8rMIYkIAtiMWp04VAEAeEFYx737zBgtpZZFvqSO576rTXaK7XESG0KCSxvT5B0ZD4AweQ4IqKoR3Jz6JrkPaZMAZapiUnpNgIgAbcz5WQrMAwBsPdovca1JEVYsgkyDsZ619QPrU8s3jKcU+3nrMP7HsA7ZRtot4UxzgB5RbL3aWGUV8OyyAM8DqC61jmT/1KaaOhQDcB6ROKe72bkc0DpH3k7BjqNAeCmXFgDNldo0sf+dO6zrROb+erHW6t9NbLne2ADcc6s/WvdJv9ZeOzYRoHG9z3rU17dpBvy17XLjdOvE7VGv6x9Pa3HfiYUVXOIWAEDFbXpH9n77YNZcFmexbd4+lP2xvrm8BAA6TaL+A1qkORgvHNnaAAAAAElFTkSuQmCC"
icon_offline = "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"
icon_v_up = "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"
icon_v_down = "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"


def getVolume():
    r = requests.get(moodeUrl + "/command/moode.php?cmd=readcfgsystem")
    result = r.json()
    return result['volknob']


def setVolume(volume):
    requests.post(
        moodeUrl + "/command/moode.php?cmd=updvolume", data={'volknob': volume})


# get cli arguments
if len(sys.argv) > 1:
    cmd = sys.argv[1]
    if cmd == "up":
        try:
            v = min(int(getVolume())+delta, 100)
            setVolume(v)
        except:
            pass
    elif cmd == "down":
        try:
            v = max(int(getVolume())-delta, 0)
            setVolume(v)
        except:
            pass

try:
    volume = int(getVolume())
except:
    volume = -1


if volume != -1:
    print(str(volume) + " | templateImage=" + icon_online)
    print("---")
    print("Volume up | color=orange terminal=false refresh=true bash=\"" +
          scriptFilepath + "\" param1=up templateImage=" + icon_v_up)
    print("Volume down | color=blue terminal=false refresh=true bash=\"" +
          scriptFilepath + "\" param1=down templateImage=" + icon_v_down)
    print("---")          
    print("Open moode | href=" + moodeUrl)
else:
    print("| templateImage=" + icon_offline)
    print("---")
    print("Moode is offline")