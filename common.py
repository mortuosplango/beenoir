# globally used variables and functions

# select language here
from lang.en import *

DEBUG = False

if DEBUG:
    def debug_print(string):
        print string
else:
    def debug_print(string):
        pass

COLORS = ('EDFF00', 'FF0000', '2600FF', 
           '006100', '6400A3', 'FF7100', 
           'B4B4B4', 'FF00FF', '00FF3F', 
           '00FFFF', 
           
           'FFFFFF', 'FFFFFF,' 'FFFFFF') #unused

CODESIZE = 8
NUMCODES = 9

UI_BEENOIR_COLOR = (40, 88, 89, 255)
UI_TEXT_COLOR = (222,) * 4

# On Screen Info

DISPLAY_ONSCREEN_INFO = True
INFO_SSID = 'BeeNoir'
INFO_URL = 'http://192.168.0.10/'

TEMPOS = (32, 24, 16, 12, 8)
NUMTEMPOS = len(TEMPOS)

# old timing: [12,8,6,4,3]
# [8, 6, 4, 3, 2]
# 1/2, 3/8, 1/4, 3/16, 1/8

TEMPO_NAMES = (
    "1/1",
    "3/4",
    "1/2",
    "3/8",
    "1/4"
)