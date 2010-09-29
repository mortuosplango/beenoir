SynthDef(\noise) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env;
	snd = WhiteNoise.ar() * 4;
	snd = RHPF.ar(snd, ypos.linlin(0,1,2000,14000)) * ypos.linlin(0,1,1,8);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.005,0.05),0), doneAction:2);
	Out.ar(0, Pan2.ar( snd * env * amp, xpos.linlin(0,1,-1,1) ));
}.add;

SynthDef(\clicks) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env;
	snd = Crackle.ar() * 4;
	snd = HPF.ar(snd, ypos.linlin(0,1,1000,4000)) * ypos.linlin(0,1,1,8);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.01,0.001),0));
	snd = snd * env;
	snd = snd + CombC.ar(snd, dur, dur/Select.kr((value*4).round, [1,2,3,4,5] * 10), dur/2);
	snd = snd * EnvGen.ar(Env([1,1], [dur]), doneAction:2); // for the combz
	Out.ar(0, Pan2.ar( snd * amp, xpos.linlin(0,1,-1,1) ));
}.add;

SynthDef(\perc_dorian) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env;
	snd = SinOsc.ar(
		DegreeToKey.kr(
			LocalBuf.newFrom(FloatArray[0, 2, 3.2, 5, 7, 9, 10]),
			ypos.linlin(0,1,0,24).round, // how many y waben??
			12,
			1,
			60-24	// c?
		).midicps
	);
	env = EnvGen.ar(Env.perc(0,value.linlin(0,1,0.1,2)), doneAction:2);
	Out.ar(0, Pan2.ar( snd * amp * env, xpos.linlin(0,1,-1,1) ));
}.add;

///////////////////////////////////////////////////////////////////////

/* Tester

Synth(\minor, [\xpos, 0.5, \ypos, 0, \value, 5]);

*/

/////////////////////////////////////////////////////////////////////

/* Multi tester

(
var name = \perc_dorian;

fork{
	24.do{ |i|
		Synth(name, [\xpos, i/16, \ypos, i/16, \value, 0.5]);
		0.5.wait;
	}
}


)
*/