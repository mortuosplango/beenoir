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
           '00FFFF', 'FFFFFF', 'FFFFFF,' 'FFFFFF')

CODESIZE = 8
NUMCODES = 9

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