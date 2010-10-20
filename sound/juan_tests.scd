// load sounds from sound file



///////////////////////////////////////////////////////////////////////

/* Tester

Synth.grain(\wtf, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, rrand(0, 1.0)]);


~master.set(\wet, 0.01, \room, 1)

*/

/////////////////////////////////////////////////////////////////////

Multi tester

Ndef(\bees).play
Ndef(\fifths).play
Ndef(\texture).play

/*
 CHANGE GRUNDTON HERE!!!!

d = e.next

*/


(

Tdef(\tester, {
	
	inf.do{ |i|

		0.05.coin.if { Synth.grain(\teleport, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };
		0.2.coin.if { Synth.grain(\wtf, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };

		0.3.coin.if { Synth.grain(\marimba, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };
		0.3.coin.if { Synth.grain(\perc, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };
		0.3.coin.if { Synth.grain(\bell, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };

		0.3.coin.if { Synth.grain(\clicks, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };
		0.3.coin.if { Synth.grain(\kick, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };
		0.3.coin.if { Synth.grain(\noise, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \grundTon, d]) };

		0.3.coin.if { Ndef(\bees).set(\amp, 1, \xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \t_trig, 1, \grundTon, d) };
		0.3.coin.if { Ndef(\fifths).set(\amp, 1, \xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \t_trig, 1, \grundTon, d) };
		0.3.coin.if { Ndef(\texture).set(\amp, 1, \xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \t_trig, 1, \grundTon, d) };

		(0.25/1.5).wait;
	}
}).play


)



Tdef(\tester).clear

