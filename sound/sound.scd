(
a = NetAddr.new("127.0.0.1", nil);
u = OSCresponder(a, '/alj/action', { |t, r, msg| 
	var addr, playerid, xpos, ypos, value, dur;
	#addr, playerid, xpos, ypos, value, dur = msg;
	msg.postln;
	Synth(
		[\ping, \pong, \pang, \wow, \fm, 
			\drummer, \ping, \ping, \ping, \ping][playerid], 
		[\out, 0, \xpos, xpos, \ypos, ypos, \dur, dur, \value, value]
	).play;
}).add;

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

SynthDef(\wow, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.2|
	var freq = ypos.linexp(0,1,40, 1200);
	var formant = XLine.kr(xpos.linexp(0, 1, 1200, 1800), freq, dur);
	var snd = Formant.ar(freq, formant, freq * Rand(2.0, 4.0))!2;
	snd = Select.ar((value * 4), [
		snd,
		snd.distort,
		snd.softclip,
		snd.distort.softclip,
		BPF.ar(snd.wrap2(0.5) * 5, freq, 1.5)
	]);
	snd = snd * EnvGen.ar(Env.perc(0.1, dur), doneAction:2);
	Out.ar(out, snd*amp);
}).add;

SynthDef(\fm, { |out=0, xpos=0, ypos=0, dur=1, value=0, amp=0.2|
	
	// whats the reange o value? 0 .. 4 ? 0 .. 5 ?
	var snd = SinOsc.ar(SinOsc.ar(value.linlin(0,4,0.1,40.0), 0, ypos * 100, xpos.linexp(0, 1, 400, 1800)))!2;
	snd = Select.ar((value * 4), [
		snd,
		snd.distort,
		snd.softclip,
		snd.distort.softclip,
		snd.distort.softclip.distort.softclip,
	]);
	snd = snd * EnvGen.ar(Env.perc(0.01, dur), doneAction:2);
	Out.ar(out, snd*amp);
}).add;

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

Synth(\fm, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, 4])
Synth(\drummer, [\xpos, rrand(0, 1.0), \ypos, rrand(0, 1.0), \value, [0,1].choose])

NetAddr.langPort

u.remove;