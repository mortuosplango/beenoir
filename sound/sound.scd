(
/*
(
Server.local.quit;
Server.internal.quit;
Server.default = Server.local;
Server.local.options.device_("Digidesign Mbox 2 Mini");
s = Server.local;
s.boot;

)
*/

var out_offset = 100;
var spec = [-60, 12, \lin, 0.1, 0, "dB"].asSpec;
var net = NetAddr.new("127.0.0.1", nil);

s.freeAll;

//////////////////////////////////////////////////////////////////////////
// GLOBALS

b = Buffer.alloc(s, 12);
c = [
	// scales with 12 values! (for binding the melodies to the y axis)
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

//////////////////////////////////////////////////////////////////////////
// SPECS AND MIXER

10.do{ |i| Spec.add(("Player"++i).asSymbol, spec) }; Spec.add(\Special, spec);

Ndef.all.clear;
Ndef(\MASTER).playN([0,1], addAction:\addToTail);
Ndef(\MASTER, {
	var inctl = 10.collect{ |i| ("Player"++i).asSymbol.kr(0) };
	var input = 10.collect{ |i| In.ar(100+(i*2), 2) * inctl[i].dbamp }; // from chan 100-120 is private then! !!!
	var special = In.ar(124, 2) * \Special.kr(0);
	var snd = Mix(input ++ special);
	
	// Master FX
	snd = MidEQ.ar(snd, 120, 1, 8); // crank the bass
	snd = MidEQ.ar(snd, 60, 0.3, 20); // crank the bass

//	snd = Select.ar(CheckBadValues.ar(input, 0, 0), [input, DC.ar(0), DC.ar(0), input]);
//	snd = FreeVerb2.ar(input[0], input[1], wet.lag, room.lag, 1);
	snd	
});

Ndef(\MASTER).edit;
Ndef(\bees).play(100, addAction:\addToHead);
Ndef(\fifths).play(106, addAction:\addToHead);
Ndef(\texture).play(112, addAction:\addToHead);

//////////////////////////////////////////////////////////////////////////
// RESPONDERS
// ignore warnings???

u = OSCresponder(net, '/beenoir/action', { |t, r, msg|
	var drone, synth; 
	var cmd, playerid, xpos, ypos, value, dur, out;
	#cmd, playerid, xpos, ypos, value, dur = msg;
	out = out_offset+(playerid*2);
	if ( [0,3,6].includes(playerid) ) {
		drone = [\bees, nil, nil, \fifths, nil, nil, \texture, nil, nil, nil][playerid];
		Ndef(drone).set(
			\xpos, xpos,
			\ypos, ypos,
			\dur, dur,
			\value, value,
			\amp, 1,
			\t_trig, 1
		);
	} {
		// TRIGGER SYNTHS
		synth = [
			nil,		//  0 DRONE
			\clicks,	//  1
			\perc,	//  2
			nil,		//  3 DRONE
			\noise,	//  4
			\marimba,	//  5
			nil,		//  6 DRONE
			\kick,	//  7
			\bell,	//  8
			\wtf		//  9
		][playerid];

		Synth.grain(synth, [\out, out, \xpos, xpos, \ypos, ypos, \dur, dur, \value, value]);
	};
}).add;

OSCresponder(net, '/beenoir/teleport', { |t, r, msg| 
	var cmd, playerid, xpos, ypos, value, dur;
	#cmd, playerid, xpos, ypos, value, dur = msg;
	msg.postln;
	b.setn(0, c.choose); // change scale
	Synth(\teleport, [\out, 124]);
}).add;

OSCresponder(net, '/beenoir/playerdeleted', { |t, r, msg| 
	var cmd, playerid, xpos, ypos, value, dur, drone;
	#cmd, playerid, xpos, ypos, value, dur = msg;
	drone = [\bees, nil, nil, \fifths, nil, nil, \texture, nil, nil, nil][playerid];
	if ( [0,3,6].includes(playerid) ) {
		Ndef(drone).end(2);
	};
}).add;

OSCresponder(net, '/beenoir/newplayer', { |t, r, msg| 
	var cmd, playerid, xpos, ypos, value, dur, drone;
	#cmd, playerid, xpos, ypos, value, dur = msg;
	drone = [\bees, nil, nil, \fifths, nil, nil, \texture, nil, nil, nil][playerid];
	if ( [0,3,6].includes(playerid) ) {
		Ndef(drone).fadeTime = 0;
		Ndef(drone).play(out_offset + (playerid*2), addAction:\addToHead);
	};
}).add;

OSCresponder(net, '/beenoir/stop', { |t, r, msg| 
	Ndef(\MASTER).stop;
}).add;

//////////////////////////////////////////////////////////////////////////
// SYNTHS

///////////////// DRONES //////////////////////////////////

Ndef(\bees, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Splay.ar(Gendy1.ar(minfreq:[60-24, 60, 60-12].midicps, maxfreq:[62-24, 62, 62-12].midicps) * 0.4);
	snd = snd.lag(0.001);
	snd = LPF.ar(snd, (ypos.linlin(0,1,50,100)).midicps * value.linexp(0,1,1,8).lag(0.1));
	snd = FreeVerb2.ar(snd[0], snd[1], 0.3, 1, 1) * 0.6;
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.perc(value.linlin(0,1,0.3,0.1), 4, 24, -16), t_trig, 1, 0.5);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * amp.lag(1);
	snd * 0.1
});

Ndef(\fifths, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Blip.ar(([61-24, 73-24] + 24).midicps + LFNoise2.ar([0.3, 0.2]).range(0, ypos.linlin(0,1,0,5)), ypos.linexp(0,1,1,8).lag(0.1));
	snd = snd * LFNoise2.ar([value.linlin(0,1,1,8), value.linlin(0,1,4,20)]).range(0.25, 1);
	snd = snd + SinOsc.ar((61 - [24,24.1]).midicps, 0, 0.35);
	snd = snd * LFNoise2.ar(40).range(0.5, 1);
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.3, 1) * 0.15;
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = snd * EnvGen.ar(Env.perc(value.linlin(0,1,0.01,0.005), value.linlin(0,1,0.01,0.8), value.linlin(0,1,2,10)), t_trig, 1, 1);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * amp.lag(1) * 2
});

Ndef(\texture, { |xpos, ypos, value, gate=1, amp=0, t_trig=1|
	var snd = Splay.ar(
		Ringz.ar(ClipNoise.ar(0.005 * ypos.linlin(0, 1, 1, 2)), ([60,67,72,79]+1+12).midicps *
			Select.kr(ypos.linlin(0,1,0,11), [0.75,1,2,0.5,2,1.5].mirror),
			0.5
		).distort
		* LFNoise2.ar({rrand(0.25, 2)}!5).range(0.1, 1)
	);
	snd = LPF.ar(Compander.ar(snd, snd, 0.001, 0.1, 1), 60.midicps * value.linlin(0,1,1,10).lag(1));
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.5, 1) * 0.3;
	snd = HPF.ar(snd, EnvGen.ar(Env.perc(0.07, 0.5, 1, -8), t_trig, 1000, 80));
	snd = Balance2.ar(snd[0], snd[1], xpos.linlin(0,1,-0.8,0.8).lag(0.2));
	snd = CombC.ar(snd, 1, value.linlin(0,1,1,0.1), 1);
	snd = snd * EnvGen.ar(Env.perc(value.linlin(0,1,0.1, 0.001), 1, value.linlin(0,1,2,4)), t_trig, 1, 1);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2) * 4 * amp.lag(1)
});

///////////////// SYNTHS //////////////////////////////////

// RYTHMIC

SynthDef(\clicks) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env;
	snd = Crackle.ar() * 10;
	snd = BPF.ar(snd, ypos.linlin(0,1,500,14000), 0.25) * ypos.linlin(0,1,12,1);
	env = EnvGen.ar(Env.linen(0,value.linlin(0,1,0.01,0.001),0));
	snd = snd * env;
	snd = snd + CombC.ar(snd, dur, dur/Select.kr((value*4).round, [4,6,8,12] * 6), dur);
	snd = snd * EnvGen.ar(Env([1,1], [dur]), doneAction:2); // for the combz
	Out.ar(out, Pan2.ar( snd * amp, xpos.linlin(0,1,-1,1) ));
}.add;

SynthDef(\noise) { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.01|
	var snd, env;
	snd = GrayNoise.ar() * 4;
	snd = RHPF.ar(snd, ypos.linlin(0,1,200,2000)) * ypos.linlin(0,1,4,8);
	env = Select.ar((value * 5).round, [
		EnvGen.ar(Env.linen(0,dur,0)),
		EnvGen.ar(Env.perc(dur, 0, 2, 4)),
		EnvGen.ar(Env.linen(0,dur,0)),
		EnvGen.ar(Env.perc(dur, 0, 2, 4)),
		EnvGen.ar(Env.perc(0,dur)),
	]);
	Line.kr(0, 1, dur, doneAction:2);
	Out.ar(out, Pan2.ar( snd * 0.5 * env * amp, xpos.linlin(0,1,-1,1) ));
}.add;

SynthDef(\kick, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.5|
	// kick by otophilia @ synth def pool
	var env0, env1, env1m, son;
	
	env0 =  EnvGen.ar(Env.new([0.5, 1, 0.5, 0], [0.005, dur/2, dur/2], [-4, -2, -4]), doneAction:2);
	env1 = EnvGen.ar(Env.new([110, 59, 29, 20], [0.005, 0.29, dur/2], [-4, -5, 1]));
	env1m = env1.midicps * ypos.linlin(0,1,1,2);
	
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
		+ SinOsc.kr(value.linlin(0,1,0,10) + Rand(0.0, 0.5), 0, value.linlin(0,1,0,5))
	);
	env = EnvGen.ar(Env.perc(0.01,dur), doneAction:2);
	snd = RLPF.ar(snd, freq * (value + 1), 0.01 + abs(1 - (value/5)));
	snd = DelayN.ar(snd, 0.1, [0, 0.003]);
	Out.ar(out, Pan2.ar( snd * amp * 1.5 * env, xpos.linlin(0,1,-0.5,0.5) ));
}).add;

SynthDef(\bell, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.1|
	var snd, env, freq, len;
	len = value.linlin(0,1,0.2,6);
	freq = DegreeToKey.kr(
		b.bufnum, // minorPenta
		ypos.linlin(0,1,0,12), // how many y waben??
		12,
		1,
		61+12	// c#?
	).midicps;
	snd = Ringz.ar(
		Decay2.ar(Impulse.ar(0), 0.01, dur),
		freq * [1,2,2.01,4, 8],
		len,
		[0.4, 0.4, 0.3, 0.1, 0.025]
	) * SinOsc.ar(Rand(0.5, [0.5, 0.7, 1.0, 1.5, 2.0]), 0.5pi, 0.3, 0.7);
	env = EnvGen.ar(Env.perc(0.001,len));
	snd = snd.sum * env;
	snd = snd * EnvGen.ar(Env([1,1], [len]), doneAction:2) * amp * 4 * ypos.linexp(0,1,1,2);
	snd = DelayN.ar(snd, 0.1, [0, 0.001]);
	Out.ar(out, Pan2.ar(snd, xpos.linlin(0,1,-0.5,0.5) ));
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
	var clippedfreq = freq.clip(20, 10000);
	var durcomp = (440 / clippedfreq) ** 0.4 * 0.5;
	var ampcomp = ((440 / freq) ** 0); 
	var cutenv = EnvGen.kr(Env([1,1,0], [durcomp, 0.01]), doneAction: 2); 
	var noisebal = value.linlin(0, 1, 0.3, 1.0); 
	
	var sound = Formlet.ar(
		Decay2.ar(
			Impulse.ar(0),
			0.01,
			dur
		) 
		* PinkNoise.ar(noisebal, 1 - noisebal) 
		* (amp * ampcomp), 
		freq, 
		0.002, durcomp
	).softclip;
//	sound = DelayN.ar(sound, 0.1, [0, 0.005]);
	Out.ar(out, Pan2.ar(sound * 1.5, xpos.linlin(0,1,-1,1), cutenv));
}).add;

// WTF
SynthDef(\wtf, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	var freq = DegreeToKey.kr(
		b.bufnum,
		ypos.linlin(0,1,0,12),
		12,
		1,
		61+48	
	).midicps;
	snd = Gendy1.ar(1, 0, freq, 1.0, 50, 1000, 1, 0.005, 12, 12, 1).distort;
	snd = (1 + (snd * 0.1)) * FBSineC.ar(freq, 0.8, 0.8);
//	snd = snd * 20;

	snd = LPF.ar(snd, 5000);
	env = EnvGen.ar(Env([0, 2, 0.3, 0.2, 0], [0.01, 0.3, dur, 0.3]), doneAction:2);
	Out.ar(out, Pan2.ar( snd * amp * env, Line.kr(0 - value, xpos, dur) ));
}).add;

//////////////////// FX!!!!
SynthDef(\teleport, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.25|
	var snd, env;
	snd = SinOsc.ar(
		SinOsc.ar(Rand(8.0, 400.0), 0, Rand(40, 800), Rand(1000, 10000))
	).distort;
	env = EnvGen.ar(Env.sine(dur), doneAction:2);
	Out.ar(out, Pan2.ar( snd * amp * 2 * env, Rand(-0.5, 0.5) ));
}).add;

// master FX
//SynthDef(\stageLimiter, { |wet=0.1, room=0.3|
//	var input = In.ar(0, 2);
//	input = MidEQ.ar(input, 120, 1, 8); // crank the bass
//	input = MidEQ.ar(input, 60, 0.3, 20); // crank the bass
//
//	input = Select.ar(CheckBadValues.ar(input, 0, 0), [input, DC.ar(0), DC.ar(0), input]);
//	input = FreeVerb2.ar(input[0], input[1], wet.lag, room.lag, 1);
//	ReplaceOut.ar(0, Limiter.ar(input)) ;
//}).add;
//
//{
//~master = Synth(\stageLimiter,
//	target: RootNode(Server.default), 
//	addAction: \addToTail
//);
//b.setn(0, c[2]); // start with pent minor mirrored
//
//}.defer(1);
//
/* MASTER Ctrl

//~master.set(\wet, 1, \room, 1)

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
