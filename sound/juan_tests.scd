// RHYTHM


SynthDef(\noise) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.01|
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

SynthDef(\kick, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.5|
	// kick by otophilia @ synth def pool
	
	var env0, env1, env1m, son;
	
	env0 =  EnvGen.ar(Env.new([0.5, 1, 0.5, 0], [0.005, 0.06, 0.26], [-4, -2, -4]), doneAction:2);
	env1 = EnvGen.ar(Env.new([110, 59, 29], [0.005, 0.29], [-4, -5]));
	env1m = env1.midicps;
	
	son = LFPulse.ar(env1m, 0, 0.5, 1, -0.5);
	son = son + WhiteNoise.ar(1);
	son = LPF.ar(son, env1m*1.5, env0);
	son = son + SinOsc.ar(env1m, 0.5, env0);
	
	son = son * 1.2;
	son = son.clip2(1);
	
	Out.ar(out, Pan2.ar(son * amp));
}).add;

// MELODIC

// TODO: distort the signal and control amplitude
SynthDef(\pentaPerc) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	snd = SinOsc.ar(
		DegreeToKey.kr(
			LocalBuf.newFrom(FloatArray[0,3,5,7,10]), // minorPenta
			ypos.linlin(0,1,0,12), // how many y waben??
			12,
			1,
			61	// c#?
		).midicps * [1,2],
		0, 0.25
	).sum;
	env = EnvGen.ar(Env.perc(0.001,value.linlin(0,1,0.5,2)), doneAction:2);
	Out.ar(0, Pan2.ar( snd * amp * env, xpos.linlin(0,1,-0.5,0.5) ));
}.add;

SynthDef(\pentaPulse) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env, freq, len;
	len = value.linlin(0,1,0.1,1);
	freq = 	DegreeToKey.kr(
		LocalBuf.newFrom(FloatArray[0,3,5,7,10]), // minorPenta
		ypos.linlin(0,1,0,12), // how many y waben??
		12,
		1,
		61-24	// c#?
	).midicps;
	snd = Pulse.ar(freq);
	snd = RLPF.ar(snd, XLine.kr(freq * value.linlin(0,1,1,8), freq, len)).lag(0.001);
	env = EnvGen.ar(Env.perc(0.001,len));
	snd = snd * env;
	snd = snd + CombC.ar(snd, dur*2, dur/value.linlin(0,1,8,24), dur);
	snd = snd * EnvGen.ar(Env([1,1], [dur]), doneAction:2);
	Out.ar(0, Pan2.ar( snd * amp, xpos.linlin(0,1,-0.5,0.5) ));
}.add;



///////////////////////////////////////////////////////////////////////

/* Tester

Synth(\pentaPulse, [\xpos, 0.5, \ypos, 0, \value, 1]);

*/

/////////////////////////////////////////////////////////////////////

/* Multi tester

(
var name = \pentaPulse;

Tdef(\tester, {
	inf.do{ |i|
		0.7.coin.if { Synth(name, [\xpos, i%12/12, \ypos, i%12/12, \value, [0,0.25,0.5,1,0.75].choose]) };
		0.4.coin.if { Synth(\pentaPerc, [\xpos, i%6/12, \ypos, i%8/12, \value, [0,0.25,0.5,1,0.75].choose]) };
		0.8.coin.if { Synth(\noise, [\xpos, i%6/12, \ypos, i%8/12, \value, [0,0.25,0.5,1,0.75].choose]) };
		0.7.coin.if { Synth(\clicks, [\xpos, i%6/12, \ypos, i%8/12, \value, [0,0.25,0.5,1,0.75].choose]) };
		0.4.coin.if { Synth(\kick, [\xpos, i%6/12, \ypos, i%8/12, \value, [0,0.25,0.5,1,0.75].choose]) };
		0.25.wait;
	}
}).play


)
*/