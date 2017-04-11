# -*- encoding: utf-8 -*-
import math
from supriya import synthdeftools
from supriya import ugentools


def channel_block(source, state):
    maximum_delay_time = state['maximum_delay_time']
    source = ugentools.AllpassC.ar(
        decay_time=ugentools.LFDNoise3.kr(
            frequency=ugentools.ExpRand.ir(0.01, 10),
            ).scale(-1, 1, 0., 0.25),
        delay_time=ugentools.LFDNoise3.kr(
            frequency=ugentools.ExpRand.ir(0.01, 10),
            ).scale(-1, 1, 0., maximum_delay_time),
        maximum_delay_time=maximum_delay_time,
        source=source,
        )
    return source


def signal_block_one(builder, source, state):
    allpasses = []
    iterations = 16
    state['maximum_delay_time'] = 0.01
    for i in range(iterations):
        allpass = channel_block(source, state)
        if i % 2:
            allpass *= -1
        allpasses.extend(allpass)
    source = ugentools.Mix.multichannel(allpasses, state['channel_count'])
    source *= math.sqrt(1 / (iterations / state['channel_count']))
    return source


def signal_block_two(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source = ugentools.Limiter.ar(source=source)
    return source


def feedback_loop(builder, source, state):
    source = (source[-1],) + source[:-1]
    source = synthdeftools.UGenArray(source)
    noise = ugentools.LFDNoise1.kr(frequency=0.1).cubed() * 0.9
    source = source * noise
    return source


factory = synthdeftools.SynthDefFactory(channel_count=2)
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_one)
factory = factory.with_signal_block(signal_block_two)
factory = factory.with_feedback_loop(feedback_loop)

nrt_chorus_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True)

rt_chorus_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_chorus = nrt_chorus_factory.build()
rt_chorus = rt_chorus_factory.build()

__all__ = (
    'nrt_chorus',
    'nrt_chorus_factory',
    'rt_chorus',
    'rt_chorus_factory',
    )
