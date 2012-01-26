I18N = {
    "player": "Player",
    "bot": "Bot",
    "player_lost": "Player isn't available anymore &hellip;",
    "sorry!": "Sorry!",
    "just_a_moment": "Just a moment &hellip;",
    "no_free_players": "No free players available verf&uuml;gbar!",
    "tempo": "Tempo",
    "back_to_start": "Back to Start",
    "back_to_game": "Return to the Game",
    "lost_connection": "Lost connection to server &hellip",
    
    "help": "Help",
    "help_descr": "You can program your bee with the following instructions. The instructions will be executed one after another. The game screen shows which instruction is currently executed.",
    
    "help_visual_hint": "If you lost your bee on the screen you can press this button to give you a visual hint.",
    "help_opcodes": "Instructions",
    
    "onscreen_info_1": "Connect your JavaScript enabled smart phone/device to WiFi \"%(ssid)s\".",
    "onscreen_info_2": "Now you can browse to %(url)s or %(url2)s to join the game!",
    
    # maybe don't translate
    "reset_button": "Reset",
    "clear_button": "Clear",
    "help_button": "Help",
    
    "back_to_help": "Return to Help",
    "about": "More Info",
    #html
    "about_page": """<p class='descr'>BeeNoir is an interactive sound toy inspired by Dave Griffiths' Al Jazari. It provides an easy insight into live coding, the programming of sound, music and pictures as part of a performance. The bees can be programmed with simple instructions, in order to move, modify the playing field or produce sounds. The sounds depend on the colour and position of the bee, as well as the current value of the field. The synthetic sounds were all developed in the audio programming environment SuperCollider.</p>
    <p class='descr'>The game was presented amongst others at LINKS &ndash; Biennale f&uuml;r Neue Musik 2010 in Heidelberg, ton:art 2011 in Karlsruhe, Next Level Conference 2011 in Cologne and Network Music Festival 2012 in Birmingham.</p>
    <p class='descr'>BeeNoir is open source software. The source code is available on GitHub. </p>
    <h2>Credits</h2>
    <p class='descr'>BeeNoir was developed at the IMWI (Institute for Musicology und Music Informatics) at the Karlsruhe University of Music by the members of the laptop band Benoit and the Mandelbrots &ndash; Holger Ballweg, Patrick Borgeat, Juan A. Romero and Matthias Schneiderbanger.</p>
    """,
    
    # web templates
    "404": "The adress '<em>%(file)s</em>' could not be opened."
}

OPCODE_ALTS = (
    "Sound",
    "Forward",
    "Backward",
    "Left",
    "Right",
    "Jump",
    "Increase",
    "Decrease",
    "Wait"
)

OPCODE_HELP = (
    "Plays a sound. The sound depends on the player's colour, position and the current field value.",
    "One step forward.",
    "One step back.",
    "Turn to the left.",
    "Turn to the right.",
    "Jump the current field value forward.", # bad
    "Increase the current field value by one.",
    "Decrease the current field value by one.",
    "Wait &ndash; do nothing."
)