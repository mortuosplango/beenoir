# globally used variables and functions

DEBUG = False

if DEBUG:
    def debug_print(string):
        print string
else:
    def debug_print(string):
        pass

colors = ('EDFF00', 'FF0000', '2600FF', 
           '006100', '6400A3', 'FF7100', 
           'B4B4B4', 'FF00FF', '00FF3F', 
           '00FFFF', 'FFFFFF', 'FFFFFF,' 'FFFFFF')

opcode_alts = (
    "Warte",
    "Vorw&auml;rts",
    "Zur&uuml;ck",
    "Nach links",
    "Nach rechts",
    "Springe",
    "Vergr&ouml;&szlig;ere Feldwert",
    "Verkleinere Feldwert",
    "Zeit",
    "Sound"
)

CODESIZE = 8
NUMCODES = 10 # number of OpCodes