///////////////// DRONES //////////////////////////////////

Ndef(\bees, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Splay.ar(Gendy1.ar(minfreq:[60-24, 60, 60-12].midicps, maxfreq:[62-24, 62, 62-12].midicps) * 0.4);
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
		Ringz.ar(PinkNoise.ar(0.005 * ypos.linlin(0, 1, 1, 2)), ([60,67,71,72]+1).midicps *
			Select.kr(ypos.linlin(0,1,0,11), [0.5,1,2,4,2,1].mirror),
			2
		).distort
		* LFNoise2.ar({rrand(0.25, 2)}!5).range(0.1, 1)
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
	snd = HPF.ar(snd, ypos.linlin(0,1,500,18000)) * ypos.linlin(0,1,1,8);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.01,0.001),0));
	snd = snd * env;
	snd = snd + CombC.ar(snd, dur, dur/Select.kr((value*4).round, [4,6,8,12] * 10), dur);
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
	env1m = env1.midicps * ypos.linlin(0,1,0.5,3);
	
	son = LFPulse.ar(env1m, 0, 0.5, 1, -0.5);
	son = son + WhiteNoise.ar(1);
	son = LPF.ar(son, env1m*1.5, env0);
	son = son + SinOsc.ar(env1m, 0.5, env0);
	
	son = son * value.linlin(0, 1, 0.3, 1.7);
	son = son.clip2(1);
	
	Out.ar(out, Pan2.ar(son * amp, xpos.linlin(0,1,-1,1)));
}).add;

// MELODIC

SynthDef(\perc, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.2|
	var snd, env, freq;
	freq = DegreeToKey.kr(
		b.bufnum, // minorPenta
		ypos.linlin(0,1,0,12), // how many y waben??
		12,
		1,
		61-12	// c#?
	).midicps;
	snd = VarSaw.ar(
		freq
		+ SinOsc.kr(value.linlin(0,1,0,5) + Rand(0.0, 0.5), 0, value.linlin(0,1,0,3))
	);
	env = EnvGen.ar(Env.perc(0.01,value.linlin(0,1,0.25,4)), doneAction:2);
	snd = RLPF.ar(snd, Rand(freq*2, freq*4), Rand(0.1, 1.0));
	snd = DelayN.ar(snd, 0.1, [0, 0.001]);
	Out.ar(0, Pan2.ar( snd * amp * env, xpos.linlin(0,1,-0.5,0.5) ));
}).add;

SynthDef(\bell, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.05|
	var snd, env, freq, len;
	len = value.linlin(0,1,2,8);
	freq = 	DegreeToKey.kr(
		b.bufnum, // minorPenta
		ypos.linlin(0,1,0,12), // how many y waben??
		12,
		1,
		61	// c#?
	).midicps;
	snd = Ringz.ar(
		Decay2.ar(Impulse.ar(0), 0.005, 0.5),
		freq * [1,1.501,2,3.6,6],
		len,
		[0.4, 0.4, 0.3, 0.25, 0.4]
	) * SinOsc.kr(Rand(0.5, [1,2,3,4,5]), 0, 0.3, 0.7);
	env = EnvGen.ar(Env.perc(0.001,len));
	snd = snd.sum * env;
	snd = snd * EnvGen.ar(Env([1,1], [len]), doneAction:2) * amp * ypos.linexp(0,1,0.3,2);
	snd = DelayN.ar(snd, 0.1, [0, 0.001]);
	Out.ar(0, Pan2.ar(snd, xpos.linlin(0,1,-0.5,0.5) ));
}).add;

SynthDef(\marimba, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	// inspired by an akadinda by adc
	var freq = DegreeToKey.kr(
		b.bufnum, // minorPenta
		ypos.linlin(0,1,0,12), // how many y waben??
		12,
		1,
		61-12	// c#?
	).midicps;
	var clippedfreq = freq.clip(100, 2000);
	var durcomp = (440 / clippedfreq) ** 0.4 * 0.5;
	var ampcomp = ((440 / freq) ** 0); 
	var cutenv = EnvGen.kr(Env([1,1,0], [durcomp, 0.01]), doneAction: 2); 
	var noisebal = 0.7; 
	
	var sound = Formlet.ar(
		Decay.ar(
			Impulse.ar(0), 
			0.03
		) 
		* PinkNoise.ar(noisebal, 1 - noisebal) 
		* (amp * ampcomp), 
		freq, 
		0.002, durcomp
	).softclip;
	sound = DelayN.ar(sound, 0.1, [0, 0.001]);
	Out.ar(out, Pan2.ar(sound, xpos.linlin(0,1,-1,1), cutenv));
}).add;

// WTF
SynthDef(\wtf, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	snd = SinOsc.ar(SinOsc.ar(Rand(1.0, 400.0), 0, Rand(0, 100), Rand(400, 4000)));
	env = EnvGen.ar(Env.sine(dur), doneAction:2);
	Out.ar(0, Pan2.ar( snd * amp * env, xpos.linlin(0,1,-0.5,0.5) ));
}).add;
)


///////////////////////////////////////////////////////////////////////

/* Tester

Synth.grain(\wtf, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, rrand(0, 1.0)]);

*/

/////////////////////////////////////////////////////////////////////

/* Multi tester

Ndef(\bees).play
Ndef(\fifths).play
Ndef(\texture).play

(

Tdef(\tester, {
	inf.do{ |i|
		0.3.coin.if { Synth.grain(\marimba, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose]) };
		0.3.coin.if { Synth.grain(\perc, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose]) };
		0.3.coin.if { Synth.grain(\bell, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose]) };

		0.3.coin.if { Synth.grain(\clicks, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose]) };
		0.3.coin.if { Synth.grain(\kick, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose]) };
		0.3.coin.if { Synth.grain(\noise, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose]) };

		0.3.coin.if { Ndef(\bees).set(\amp, 1, \xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \t_trig, 1) };
		0.3.coin.if { Ndef(\fifths).set(\amp, 1, \xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \t_trig, 1) };
		0.3.coin.if { Ndef(\texture).set(\amp, 1, \xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,0.25,0.5,1,0.75].choose, \t_trig, 1) };

		0.25.wait;
	}
}).play


)



Tdef(\tester).clear

*/