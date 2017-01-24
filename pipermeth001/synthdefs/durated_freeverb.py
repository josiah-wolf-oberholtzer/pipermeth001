# -*- encoding: utf-8 -*-
from supriya import DoneAction, SynthDefBuilder
from supriya import ugentools


channel_count = 2

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    damping=0.5,
    room_size=0.5,
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
    source = ugentools.FreeVerb.ar(
        source=source,
        damping=builder['damping'],
        room_size=builder['room_size'],
        mix=1.0,
        )
    source = ugentools.LeakDC.ar(source=source)
    source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window,
        source=source,
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(tuple(in_) + tuple(source)),
        )

durated_freeverb = builder.build()
