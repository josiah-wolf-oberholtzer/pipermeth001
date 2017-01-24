# -*- encoding: utf-8 -*-
from supriya import SynthDefBuilder
from supriya import synthdeftools
from supriya import ugentools


channel_count = 2

with SynthDefBuilder(
    level=synthdeftools.Parameter(value=0.0, lag=15),
    out=0,
    ) as builder:
    source = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        ) * builder['level'].s_curve()
    ugentools.ReplaceOut.ar(
        bus=builder['out'],
        source=source,
        )
volume = builder.build()
