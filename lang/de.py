# coding=UTF-8
I18N = {
    "player": "Spieler",
    "bot": "Bot",
    "player_lost": "Spieler nicht mehr verf&uuml;gbar &hellip;",
    "sorry!": "Entschuldigung!",
    "just_a_moment": "Einen Moment Bitte &hellip;",
    "no_free_players": "Keine freien Spieler verf&uuml;gbar!",
    "tempo": "Tempo",
    "back_to_start": "Zur&uuml;ck zum Start",
    "back_to_game": "Zur&uuml;ck zum Spiel",
    "lost_connection": "Verbindung zum Server ist unterbrochen &hellip",
    
    "help": "Hilfe",
    "help_descr": "Sie k&ouml;nnen ihre Biene mit folgenden Befehlen programmieren. Die Befehle werden nacheinander von der Biene ausgef&uuml;hrt. Der aktuell ausgef&uumlhrte Befehl leuchtet auf der Projektion auf.",
    
    "help_visual_hint": "Wenn Sie ihre Biene auf dem Bildschirm verloren haben k&ouml;nnen sie diesen Knopf dr&uuml;cken.",
    "help_opcodes": "Befehle",
    
    "onscreen_info_1": u"Mit einem JavaScript fähigen Smartphone können sie mitmachen!",
    "onscreen_info_2": u"Verbinden Sie sich mit dem WLAN \"%(ssid)s\" surfen sie mit ihrem Browser auf die Seite %(url)s oder %(url2)s",
    
    "back_to_help": "Zur&uumlck zur Hilfe",
    "about": "Mehr Informationen",
    #html
    "about_page": """<p class='descr'>BeeNoir ist ein interaktives Klangspielzeug und stark von Dave Griffiths Spiel Al Jazari beeinflusst. Es bietet einen verst&auml;ndlichen Einblick in das Live-Coding, dem Programmieren von Kl&auml;ngen, Musik und Bildern als Teil der Performance. Die Spielfiguren in BeeNoir lassen sich mit einfachen Befehlen programmieren, um sich auf dem Spielfeld zu bewegen, es zu ver&auml;ndern oder Kl&auml;nge zu erzeugen. Die Kl&auml;nge sind abh&auml;ngig von Farbe und Position des Spielers sowie dem Feldwert, auf dem sich der Spieler im Moment befindet. Die synthetischen Kl&auml;nge wurden in der Musikprogrammiersprache SuperCollider entwickelt.</p>
    <p class='descr'>Das Spiel wurde u.a. auf der LINKS &ndash; Biennale f&uuml;r Neue Musik 2010 in Heidelberg, der ton:art 2011 in Karlsruhe, der Next Level Conference 2011 in K&ouml;ln und dem  Network Music Festival 2012  in Birmingham pr&auml;sentiert.</p>
    <p class='descr'>BeeNoir ist Open Source Software. Der Quelltext steht auf GitHub zur Verf&uuml;gung.</p>
    <h2>Credits</h2>
    <p class='descr'>BeeNoir wurde am IMWI (Institut f&uuml;r Musikwissenschaft und Musikinformatik) der Hochschule f&uuml;r Musik Karlsruhe von den Mitgliedern der Laptop-Band Benoit and the Mandelbrots &ndash; Holger Ballweg, Patrick Borgeat, Juan A. Romero und Matthias Schneiderbanger &ndash; entwickelt.</p>
    """,

    
    # maybe don't translate
    "reset_button": "Neustart",
    "clear_button": "Leeren",
    "help_button": "Hilfe",
    

    
    
    # web templates
    "404": "Die Adresse '<em>%(file)s</em>' konnte nicht ge&ouml;ffnet werden."
}

OPCODE_ALTS = (
    "Klang",
    "Vorw&auml;rts",
    "Zur&uuml;ck",
    "Nach links",
    "Nach rechts",
    "Springe",
    "Erh&ouml;he Feldwert",
    "Erniedrige Feldwert",
    "Warte"
)

OPCODE_HELP = (
    "Spielt einen Klang ab. Der Klang ist je nach Spielerfarbe, Spielerposition und Feldwert anders.",
    "Einen Schritt vorw&auml;ts.",
    "Einen Schritt r&uuml;ckw&auml;rts.",
    "Drehung nach Links.",
    "Drehung nach Rechts.",
    "Springe um den aktuellen Feldwert nach vorne.",
    "Erh&ouml;he den aktuellen Feldwert um eins.",
    "Erniedrige den aktuellen Feldwert um eins.",
    "Warte &ndash; Tu nichts."
)