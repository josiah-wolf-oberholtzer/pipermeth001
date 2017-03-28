# -*- encoding: utf-8 -*-
from supriya import SynthDefBuilder
from supriya import ugentools


with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    source = ugentools.Dust2.ar(
        density=ugentools.ExpRand.ir(1, 50),
        ) * window
    ugentools.Out.ar(
        bus=builder['out'],
        source=[source, source],
        )

durated_dust = builder.build()
