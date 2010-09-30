/*

instrument ditribution:

- 3 drones (d)
- 3 rhythmic (r)
- 3 melodic (m)
- 1 wtf? {last player} (w) : BEE NOIR!

[ d r m d r m d r m WTF ]

master effects:

- compressor
- limiter
- reverb

trigger effects:

- black hole

*/

(

s.freeAll;

a = NetAddr.new("127.0.0.1", nil);
b = Buffer.alloc(s, 12);
c = [
	// scales with 12 values! (for bending the melodies to the y axis)
	FloatArray[0,2,3,5,7,8,10,12,14,15,17,18],	// minor ext
	FloatArray[0,2,3,5,7,8,10,12,10,8,7,3],		// minor pseudo mirror
	FloatArray[0,3,5,7,10,12,15,10,7,5,3,0],	// pent minor mirror
	FloatArray[0,3,5,7,10,12,15,17,19,22,24,0], // pent ext
	FloatArray[0,2,3,5,7,9,10,12,10,9,7,3],		// dorian + penta
	FloatArray[0,2,3,5,7,9,10,12,14,15,17,19],	// dorian full
	FloatArray[0,2,3,5,7,8,8,7,5,3,2,0],		// minor full mirror
	FloatArray[0,2,4,5,7,9,11,12,14,16,17,19],	// major ext
	FloatArray[0,2,4,5,7,9,11,12,7,5,4,2],		// major pseudo mirror
];
b.setn(0, c[2]); // start with pent minor mirrored

// need a responder to start the drones!

Ndef.all.clear;
Ndef(\bees).play;
Ndef(\fifths).play;
Ndef(\texture).play;


u = OSCresponder(a, '/alj/action', { |t, r, msg| 
	var addr, playerid, xpos, ypos, value, dur;
	#addr, playerid, xpos, ypos, value, dur = msg;
	msg.postln;
	if ( [0,3,6].includes(playerid) ) {
		// DRONES!
		Ndef(
			// use just 0, 3 and 6
			[\bees, nil, nil, \fifths, nil, nil, \texture, nil, nil, nil][playerid]
		).set(
			\xpos, xpos,
			\ypos, ypos,
			\dur, dur,
			\value, value,
			\amp, 1,
			\t_trig, 1
		);
	} {
		// TRIGGER SYNTHS
		Synth(
			[
				nil,		//  0 DRONE
				\clicks,	//  1
				\perc,		//  2
				nil,		//  3 DRONE
				\noise,		//  4
				\pulse,		//  5
				nil,		//  6 DRONE
				\kick,		//  7
				\bell,		//  8
				\wtf		//	9
			][playerid], 
			[\out, 0, \xpos, xpos, \ypos, ypos, \dur, dur, \value, value]
		);
	};
}).add;

t = OSCresponder(a, '/alj/teleport', { |t, r, msg| 
	var addr, playerid, xpos, ypos, value, dur;
	#addr, playerid, xpos, ypos, value, dur = msg;
	msg.postln;
	// change scale
	b.setn(0, c.choose);
	// make random effect
	
}).add;


///////////////// DRONES //////////////////////////////////

Ndef(\bees, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Splay.ar(Gendy1.ar(minfreq:[60-24, 60, 60-12].midicps, maxfreq:[62-24, 62, 62-12].midicps) * 0.2);
	snd = snd.lag(0.001);
	snd = LPF.ar(snd, (ypos.linlin(0,1,70,100)).midicps * value.linexp(0,1,1,4).lag(0.2));
	snd = FreeVerb2.ar(snd[0], snd[1], 0.3, 1, 1);
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * amp.lag(1)
});

Ndef(\fifths, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Blip.ar([61-24, 73-24].midicps + LFNoise2.ar([0.3, 0.2]).range(0, ypos.linlin(0,1,0,5)), ypos.linlin(0,1,1,16).lag(0.1));
	snd = snd *	LFNoise2.ar([value.linlin(0,1,1,8), value.linlin(0,1,4,20)]).range(0.25, 1);
	snd = snd * LFNoise2.ar(40).range(0.5, 1);
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.7, 1) * 0.25;
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.perc(0.001, 0.25), t_trig, 1, 1);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * amp.lag(1) * 4
});

Ndef(\texture, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Splay.ar(
		Ringz.ar(PinkNoise.ar(0.005 * ypos.linlin(0, 1, 1, 2)), [60,63,65,71,72].midicps *
			Select.kr(ypos.linlin(0,1,0,11), [0.5,1,2,4,2,1].mirror),
			2
		).distort *
		LFNoise2.ar({rrand(0.25, 2)}!5).range(0.1, 1)
	);
	snd = LPF.ar(Compander.ar(snd, snd, 0.01, 0.1, 1), 60.midicps * value.linlin(0,1,1,10).lag(1)) * 3;
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.5, 1);
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * amp.lag(1)
});

///////////////// SYNTHS //////////////////////////////////

// RYTHMIC

SynthDef(\clicks) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env;
	snd = Crackle.ar() * 10;
	snd = HPF.ar(snd, ypos.linlin(0,1,1000,8000)) * ypos.linlin(0,1,1,8);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.01,0.001),0));
	snd = snd * env;
	snd = snd + CombC.ar(snd, dur, dur/Select.kr((value*4).round, [1,2,4,8] * 10), dur/2);
	snd = snd * EnvGen.ar(Env([1,1], [dur]), doneAction:2); // for the combz
	Out.ar(0, Pan2.ar( snd * amp, xpos.linlin(0,1,-1,1) ));
}.add;

SynthDef(\noise) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.01|
	var snd, env;
	snd = WhiteNoise.ar() * 4;
	snd = RHPF.ar(snd, ypos.linlin(0,1,800,4000)) * ypos.linlin(0,1,1,8);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.005,0.05),0), doneAction:2);
	Out.ar(0, Pan2.ar( snd * env * amp, xpos.linlin(0,1,-1,1) ));
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

SynthDef(\perc) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	snd = SinOsc.ar(
		DegreeToKey.kr(
			LocalBuf.newFrom(FloatArray[0,3,5,7,10]), // minorPenta
			ypos.linlin(0,1,0,12), // how many y waben??
			12,
			1,
			61-12	// c#?
		).midicps +
		SinOsc.kr(value.linlin(0,1,0,4) + Rand(0.0, 2.0), 0, value.linlin(0,1,0,10))
	);
	env = EnvGen.ar(Env.perc(0.001,value.linlin(0,1,0.25,4)), doneAction:2);
	Out.ar(0, Pan2.ar( snd * amp * env, xpos.linlin(0,1,-0.5,0.5) ));
}.add;

SynthDef(\pulse) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
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



// WTF

)


NetAddr.langPort

u.remove;

/*
OLD CODE

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

*/

