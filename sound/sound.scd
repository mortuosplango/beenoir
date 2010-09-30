/*

instrument ditribution:

- 3 drones (d)
- 3 rhythmic (r)
- 3 melodic (m)
- 1 wtf? {last player} (w) : BEE NOIR!

[ r m d r m d r m d w ]

master effects:

- compressor
- limiter
- reverb

trigger effects:

- black hole

*/

(
a = NetAddr.new("127.0.0.1", nil);
u = OSCresponder(a, '/alj/action', { |t, r, msg| 
	var addr, playerid, xpos, ypos, value, dur;
	#addr, playerid, xpos, ypos, value, dur = msg;
	msg.postln;
	Synth(
		[
			\clicks,	//  0 r
			\pentaPerc,	//  1 m
			\ping,		//  3 d
			\noise,		//  4 r
			\pentaPulse,//  5 m
			\pang,		//  6 d
			\drummer,	//  7 r
			\ping,		//  8 m
			\pong,		//  9 d
			\pang		// 10 w
		][playerid], 
		[\out, 0, \xpos, xpos, \ypos, ypos, \dur, dur, \value, value]
	).play;
}).add;

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

SynthDef(\noise) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.01|
	var snd, env;
	snd = WhiteNoise.ar() * 4;
	snd = RHPF.ar(snd, ypos.linlin(0,1,2000,14000)) * ypos.linlin(0,1,1,8);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.005,0.05),0), doneAction:2);
	Out.ar(0, Pan2.ar( snd * env * amp, xpos.linlin(0,1,-1,1) ));
}.add;

SynthDef(\pentaPerc) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	snd = SinOsc.ar(
		DegreeToKey.kr(
			LocalBuf.newFrom(FloatArray[0,3,5,7,10]), // minorPenta
			ypos.linlin(0,1,0,12), // how many y waben??
			12,
			1,
			61-12	// c#?
		).midicps
	);
	env = EnvGen.ar(Env.perc(0.001,value.linlin(0,1,0.25,4)), doneAction:2);
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


SynthDef(\ping) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env, len;
	snd = SinOsc.ar(ypos.linexp(0,1,400,800) * [1, 1.01]);
	env = EnvGen.ar(Env.perc(0.01, dur));
	len = value.linlin(0,1,2,10);
	snd = CombN.ar(snd * env, 0.1, 0.1, len) ;
	Line.kr(0,1,len+1,doneAction:2);
	Out.ar(0, Pan2.ar(snd.sum * env * amp,xpos.linlin(0,1,-1,1)));
}.add;

SynthDef(\pong) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.2|
	var snd, env;
	snd = WhiteNoise.ar + BrownNoise.ar;
	snd = MoogFF.ar(snd, ypos.linexp(0,1,1400,1800), value.linlin(0,1,3,3.8));
	env = EnvGen.ar(Env.linen(0.01, dur,0.1), doneAction:2);
	Out.ar(0, Pan2.ar(snd * env * amp,xpos.linlin(0,1,-1,1)));
}.add;

SynthDef(\pang) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env;
	snd = Saw.ar(ypos.linexp(0,1,50,500) * IRand(1,3!10)).sum/10;
	snd = MoogFF.ar(snd, 5000, value.linlin(0,1,3,3.8));
	env = EnvGen.ar(Env.linen(0.1, dur,0.5), doneAction:2);
	Out.ar(0, Pan2.ar(snd * env * amp,xpos.linlin(0,1,-1,1)));
}.add;

SynthDef(\drummer, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.2|
	var snd = Select.ar((value * 4), [
		// make 5 drum kind of sounds
		// and use value for it
		// ignore XY?
		
		// 0 - FM Bass Drum
		SinOsc.ar(XLine.ar(Rand(400, 1000), 60, 0.1))!2 * Decay2.ar(Impulse.ar(0), 0.0001, dur),
		
		// 1 - Snare Drum (shitty, synth def pool? sample?)
		BPF.ar(HPF.ar(WhiteNoise.ar(1), 200, 2), 900, 0.6, 3) * EnvGen.ar(Env.perc(0.01, dur/4));

	]);
	snd =  snd * EnvGen.ar(Env.linen(0, dur, 0), doneAction:2);
	Out.ar(out, snd*amp);
}).add;


)


NetAddr.langPort

u.remove;