(
a = NetAddr.new("127.0.0.1", nil);
u = OSCresponder(a, '/alj/action', { |t, r, msg| 
	var addr, playerid, xpos, ypos, value, dur;
	#addr, playerid, xpos, ypos, value, dur = msg;
	msg.postln;
	Synth(
		[\ping, \pong, \pang, \pong, \pang, 
			\pong, \ping, \ping, \ping, \ping][playerid], 
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
)

NetAddr.langPort

u.remove;