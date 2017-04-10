# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_one(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)
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


def signal_block_two(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source = ugentools.Limiter.ar(source=source)
    return source


def feedback_loop(builder, source, state):
    source = (source[-1],) + source[:-1]
    source = synthdeftools.UGenArray(source)
    source = source * -0.95 * ugentools.LFDNoise1.kr(frequency=0.1)
    return source


factory = synthdeftools.SynthDefFactory(channel_count=2)
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_one)
factory = factory.with_signal_block(signal_block_two)
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
