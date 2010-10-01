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
		Synth.grain(
			[
				nil,		//  0 DRONE
				\clicks,	//  1
				\perc,		//  2
				nil,		//  3 DRONE
				\noise,		//  4
				\marimba,	//  5
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
	b.setn(0, c.choose); // change scale
	Synth(\teleport)
}).add;


///////////////// DRONES //////////////////////////////////

Ndef(\bees, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Splay.ar(Gendy1.ar(minfreq:[60-24, 60, 60-12].midicps, maxfreq:[62-24, 62, 62-12].midicps) * 0.4);
	snd = snd.lag(0.001);
	snd = LPF.ar(snd, (ypos.linlin(0,1,70,100)).midicps * value.linexp(0,1,1,4).lag(0.2));
	snd = FreeVerb2.ar(snd[0], snd[1], 0.3, 1, 1) * 0.6;
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.perc(0.03, 1, 5), t_trig, 1, 1);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * amp.lag(1)
});

Ndef(\fifths, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Blip.ar([61-24, 73-24].midicps + LFNoise2.ar([0.3, 0.2]).range(0, ypos.linlin(0,1,0,5)), ypos.linlin(0,1,1,16).lag(0.1));
	snd = snd *	LFNoise2.ar([value.linlin(0,1,1,8), value.linlin(0,1,4,20)]).range(0.25, 1);
	snd = snd * LFNoise2.ar(40).range(0.5, 1);
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.3, 1) * 0.15;
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.perc(0.1, 2, 5), t_trig, 1, 1);
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
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.5, 1) * 0.3;
	snd = HPF.ar(snd, EnvGen.ar(Env.perc(0.07, 0.5, 1, -8), t_trig, 1000, 80));
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.perc(0.03, 1, 3), t_trig, 1, 1);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * 4 * amp.lag(1)
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
	snd = GrayNoise.ar() * 4;
	snd = RHPF.ar(snd, ypos.linlin(0,1,200,2000)) * ypos.linlin(0,1,1,8);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.005,0.1),0), doneAction:2);
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
		61	// c#?
	).midicps;
	snd = VarSaw.ar(
		freq
		+ SinOsc.kr(value.linlin(0,1,0,5) + Rand(0.0, 0.5), 0, value.linlin(0,1,0,3))
	);
	env = EnvGen.ar(Env.perc(0.01,value.linlin(0,1,0.25,4)), doneAction:2);
	snd = RLPF.ar(snd, Rand(freq*2, freq*4), Rand(0.1, 1.0));
	snd = DelayN.ar(snd, 0.1, [0, 0.001]);
	Out.ar(0, Pan2.ar( snd * amp * 2 * env, xpos.linlin(0,1,-0.5,0.5) ));
}).add;

SynthDef(\bell, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env, freq, len;
	len = value.linlin(0,1,2,8);
	freq = 	DegreeToKey.kr(
		b.bufnum, // minorPenta
		ypos.linlin(0,1,0,12), // how many y waben??
		12,
		1,
		61+24	// c#?
	).midicps;
	snd = Ringz.ar(
		Decay2.ar(Impulse.ar(0), 0.005, 0.5),
		freq * [1,1.501,2,3.6,6],
		len,
		[0.4, 0.4, 0.3, 0.25, 0.4]
	) * SinOsc.kr(Rand(0.5, [1,2,3,4,5]), 0, 0.3, 0.7);
	env = EnvGen.ar(Env.perc(0.001,len));
	snd = snd.sum * env;
	snd = snd * EnvGen.ar(Env([1,1], [len]), doneAction:2) * amp * 3 * ypos.linexp(0,1,1,2);
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
	Out.ar(out, Pan2.ar(sound * 1.3, xpos.linlin(0,1,-1,1), cutenv));
}).add;

// WTF
SynthDef(\wtf, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	snd = Gendy1.ar(1, 0, ypos,1.0, 50, 1000, 1, 0.005, 12, 12, 0.75);
	env = EnvGen.ar(Env.sine(dur), doneAction:2);
	Out.ar(0, Pan2.ar( snd * amp * env, xpos.linlin(0,1,-0.5,0.5) ));
}).add;

//////////////////// FX!!!!
SynthDef(\teleport, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	snd = SinOsc.ar(
		SinOsc.ar(Rand(8.0, 400.0), 0, Rand(40, 800), Rand(1000, 10000))
	).distort;
	env = EnvGen.ar(Env.sine(dur), doneAction:2);
	Out.ar(0, Pan2.ar( snd * amp * 2 * env, Rand(-0.5, 0.5) ));
}).add;

// master FX
SynthDef(\stageLimiter, { |wet=0.1, room=0.3|
	var input = In.ar(0, 2);
	input = Select.ar(CheckBadValues.ar(input, 0, 0), [input, DC.ar(0), DC.ar(0), input]);
	input = FreeVerb2.ar(input[0], input[1], wet.lag, room.lag, 1);
	ReplaceOut.ar(0, Limiter.ar(input)) ;
}).add;

{
	~master = Synth(\stageLimiter,
	target: RootNode(Server.default), 
	addAction: \addToTail
)}.defer(1);

/* MASTER Ctrl

~master.set(\wet, 0.1, \room, 1)

*/

)


// NetAddr.langPort
// u.remove;

/*

instrument ditribution:

x 3 drones (d)
x 3 rhythmic (r)
x 3 melodic (m)
x 1 wtf? {last player} (w) : BEE NOIR!

[ d r m d r m d r m WTF ]

master effects:

? compressor
x limiter
x reverb

trigger effects:

x black hole

*/
