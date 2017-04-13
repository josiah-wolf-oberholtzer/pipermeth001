# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_pre(builder, source, state):
    source = ugentools.Limiter.ar(
        duration=ugentools.Rand.ir(0.005, 0.015),
        source=source,
        )
    return source


def signal_block(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
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
    source *= ugentools.LFNoise1.kr(frequency=0.05).squared().squared()
    source *= -0.9
    source = ugentools.HPF.ar(
        source=source,
        frequency=250,
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

nrt_allpass_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True)

rt_allpass_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_allpass = nrt_allpass_factory.build()
rt_allpass = rt_allpass_factory.build()

__all__ = (
    'nrt_allpass',
    'nrt_allpass_factory',
    'rt_allpass',
    'rt_allpass_factory',
    )
