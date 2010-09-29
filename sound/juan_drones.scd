// drones test... should be a synthdef...

// fifhts drone in C !
(
Ndef(\fifths, { |xpos, ypos, value, gate=1|
	
	var snd = Blip.ar([60-24, 60-17].midicps + LFNoise2.ar(0.5).range(0, ypos.linlin(0,1,0,5)), value.linlin(0,1,1,5));
	snd = snd *	LFNoise2.ar([value.linlin(0,1,1,8), value.linlin(0,1,4,20)]).range(0.25, 1);
	snd = snd * LFNoise2.ar(40).range(0.5, 1);
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.7, 1) * 0.25;
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2)
}).play;

)

Ndef(\fifths).xset(\value, 0, \ypos, 1,  \xpos, 0) // achtung mit fade times?


// bass drone in C with modulation

(
Ndef(\bass, { |xpos, ypos, value, gate=1|
	
	var snd = Splay.ar(
		Ringz.ar(PinkNoise.ar(0.002), [60,63,65,71,72].midicps, 2).distort *
		LFNoise2.ar({rrand(0.25, 2)}!5).range(0.1, 1)
	);
	snd = LPF.ar(Compander.ar(snd, snd, 0.01, 0.1, 1), 60.midicps * value.linlin(0,1,1,10).lag(1)) * 2;
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.5, 1);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2)
}).play;

)

Ndef(\bass).set(\value, 1, \ypos, 0, \xpos, 0) // achtung mit fade times?

