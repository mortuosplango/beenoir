Requirements:
Processing
oscP5 (OSC library for Processing)
Python 2.6
Chuck

Usage:

0. Go to the project directory.

1. Start the OSC bridge.
python polosc/polosc.py 8000 cs2.map cs.not

2. Start the model.
chuck circlesequencer.ck

3. Start the view.
Open up the csview directory using Processing.

4. Go to the controller URL in a web browser. 
http://HOSTNAME:8000/cscontrol.html
