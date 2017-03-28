# -*- encoding: utf-8 -*-
from supriya import DoneAction, SynthDefBuilder
from supriya import synthdeftools
from supriya import ugentools


channel_count = 2

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    source = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source += ugentools.LocalIn.ar(channel_count=channel_count)
    source *= ugentools.Line.kr(duration=0.1)
    allpasses = []
    maximum_delay = ugentools.Rand.ir(0.1, 1)
    for output in source:
        for _ in range(3):
            output = ugentools.AllpassC.ar(
                decay_time=ugentools.LFDNoise3.kr(
                    frequency=ugentools.ExpRand.ir(0.01, 0.1),
                    ).scale(-1, 1, 0.001, 1),
                delay_time=ugentools.LFDNoise3.kr(
                    frequency=ugentools.ExpRand.ir(0.01, 0.1),
                    ).scale(-1, 1, 0.001, 1) * maximum_delay,
                maximum_delay_time=maximum_delay,
                source=output,
                )
        allpasses.append(output)
    source = synthdeftools.UGenArray(allpasses)
    source = ugentools.LeakDC.ar(source=source)
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window,
        source=source * builder['level'],
        )
    ugentools.LocalOut.ar(
        source=source * -0.9 * ugentools.LFDNoise1.kr(frequency=0.1)
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(source),
        )
durated_allpass = builder.build()
