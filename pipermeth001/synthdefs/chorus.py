# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_pre(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
    source = ugentools.Limiter.ar(
        duration=ugentools.Rand.ir(0.005, 0.015),
        source=source,
        )
    return source


def iteration_block(source, state):
    channel_count = state['channel_count']
    maximum_delay_time = 0.01
    for _ in range(2):
        decay_time = ugentools.ExpRand.ir(
            minimum=[0.001] * channel_count,
            maximum=[maximum_delay_time * 2] * channel_count,
            )
        delay_time = ugentools.LFNoise2.kr(
            frequency=ugentools.ExpRand.ir(
                minimum=[0.1] * channel_count,
                maximum=[5.0] * channel_count,
                ),
            ).squared() * maximum_delay_time
        source = ugentools.AllpassC.ar(
            decay_time=decay_time,
            delay_time=delay_time,
            maximum_delay_time=maximum_delay_time,
            source=source,
            )
        assert len(decay_time) == channel_count
        assert len(delay_time) == channel_count
        assert len(source) == channel_count
    return source


def signal_block(builder, source, state):
    allpasses = []
    iterations = 16
    for i in range(iterations):
        allpass = iteration_block(source, state)
        if i % 2:
            allpass *= -1
        allpasses.extend(allpass)
    source = ugentools.Mix.multichannel(allpasses, state['channel_count'])
    source *= 1. / iterations
    return source


def signal_block_post(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source *= builder['gain'].db_to_amplitude()
    source = ugentools.Limiter.ar(
        duration=ugentools.Rand.ir(0.005, 0.015),
        source=source,
        )
    return source


def feedback_loop(builder, source, state):
    source = synthdeftools.UGenArray((source[-1],) + source[:-1])
    source *= ugentools.LFNoise1.kr(frequency=0.05).squared()
    source *= -0.95
    source = ugentools.HPF.ar(
        source=source,
        frequency=500,
        )
    source = ugentools.DelayC.ar(
        source=source,
        delay_time=ugentools.LFNoise1.kr(
            frequency=0.05,
            ).scale(-1, 1, 0.1, 0.2),
        maximum_delay_time=0.2,
        )
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    gain=0,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_pre)
factory = factory.with_signal_block(signal_block)
factory = factory.with_signal_block(signal_block_post)
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
