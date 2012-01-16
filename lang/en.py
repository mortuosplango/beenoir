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
    
    # Hilfe
    "help": "Help",
    "help_descr": "You can program your bee with the following instructions. The instructions will be executed one after another. The game screen shows which instruction is currently executed.",
    
    
    # maybe don't translate
    "reset_button": "Reset",
    "clear_button": "Clear",
    "help_button": "Help",
    
    "back_to_help": "Return to Help",
    "about": "More Info",
    #html
    "about_page": "<p class='descr'>This should be written ...</p>",
    
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