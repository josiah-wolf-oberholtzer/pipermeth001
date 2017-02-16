# -*- encoding: utf-8 -*-
from supriya import SynthDefBuilder
from supriya import ugentools


channel_count = 2

with SynthDefBuilder(
    out=0,
    ) as builder:
    source = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source = ugentools.LeakDC.ar(source=source)
    source = ugentools.Limiter.ar(source=source)
    ugentools.ReplaceOut.ar(
        bus=builder['out'],
        source=source,
        )

limiter = builder.build()
