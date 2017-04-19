# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
    sign = builder['sign']
    frequency = ugentools.LFNoise2.kr(frequency=0.01).scale(
        -1, 1, 100, 1000) * sign
    source = ugentools.FreqShift.ar(
        source=source,
        frequency=frequency,
        phase=ugentools.LFNoise2.kr(frequency=0.01),
        )
    return source


factory = synthdeftools.SynthDefFactory(channel_count=2, sign=1)
factory = factory.with_input()
factory = factory.with_signal_block(signal_block)

nrt_freqshift_factory = factory.with_output(
    crossfaded=True, leveled=True, windowed=True)

rt_freqshift_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_freqshift = nrt_freqshift_factory.build()
rt_freqshift = rt_freqshift_factory.build()

__all__ = (
    'nrt_freqshift',
    'nrt_freqshift_factory',
    'rt_freqshift',
    'rt_freqshift_factory',
    )
