# -*- encoding: utf-8 -*-
from supriya import DoneAction, SynthDefBuilder
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
    in_ = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source = in_ * window
    source = source[0] + source[1]
    source += ugentools.LocalIn.ar(channel_count=1)
    allpasses = []
    allpass_count = 16
    maximum_delay_time = 0.01
    for _ in range(allpass_count):
        allpass = ugentools.AllpassC.ar(
            decay_time=ugentools.LFDNoise3.kr(
                frequency=ugentools.ExpRand.ir(0.1, 5),
                ).scale(-1, 1, 0., 0.1),
            delay_time=ugentools.LFDNoise3.kr(
                frequency=ugentools.ExpRand.ir(0.1, 5),
                ).scale(-1, 1, 0., maximum_delay_time),
            maximum_delay_time=maximum_delay_time,
            source=source,
            )
        allpasses.append(allpass)
    source = ugentools.Mix.new(allpasses) / allpass_count
    source = ugentools.LeakDC.ar(source=source)
    #source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window * builder['level'],
        source=[source, source],
        )
    ugentools.LocalOut.ar(
        source=source * -0.9 * abs(ugentools.LFDNoise1.kr(frequency=0.1))
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(tuple(in_) + tuple(source)),
        )

durated_mono_chorus = builder.build()
