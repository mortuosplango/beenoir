// drones test... should be a synthdef...

(
Ndef(\fifths, { |xpos, ypos, value, gate=1|
	
	var snd = Blip.ar([60-24, 60-17].midicps + LFNoise2.ar(0.5).range(0, ypos.linlin(0,1,0,5)), value.linlin(0,1,1,5));
	snd = snd *	LFNoise2.ar([value.linlin(0,1,1,8), value.linlin(0,1,4,20)]).range(0.25, 1);
	snd = snd * LFNoise2.ar(40).range(0.5, 1);
	snd = FreeVerb2.ar(snd[0], snd[1], 1, 0.7, 1);
	snd = snd * EnvGen.ar(Env.asr(1, 1, 1, 8), gate, doneAction:2)
}).play;

)

Ndef(\fifths).xset(\value, 0, \ypos, 1) // achtung mit fade times?