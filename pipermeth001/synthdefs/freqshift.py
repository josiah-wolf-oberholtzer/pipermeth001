# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_one(builder, source, state):
    source = ugentools.FreqShift.ar(
        source=source,
        frequency=ugentools.LFDNoise3.kr(frequency=0.01) * 2000,
        phase=ugentools.LFNoise2.kr(frequency=0.01),
        )
    return source


def signal_block_two(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source = ugentools.Limiter.ar(source=source)
    return source


factory = synthdeftools.SynthDefFactory(channel_count=2)
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_one)
factory = factory.with_signal_block(signal_block_two)

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
