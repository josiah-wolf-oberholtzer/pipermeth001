# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_pre(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
    #source = ugentools.Limiter.ar(
    #    duration=ugentools.Rand.ir(0.005, 0.015),
    #    source=source,
    #    )
    return source


def signal_block(builder, source, state):
    stage_iterations = 3
    inner_iterations = 4
    channel_count = state['channel_count']
    frequency = [builder['frequency']] * channel_count
    assert len(frequency) == channel_count
    lowpassed = ugentools.LPF.ar(
        source=source,
        frequency=1000,
        )
    source -= lowpassed
    for _ in range(stage_iterations):
        all_delays = []
        delay = source
        for i in range(inner_iterations):
            delay_time = ugentools.LFNoise2.kr(frequency=frequency)
            delay_time = delay_time.scale(-1, 1, 0.0001, 0.01)
            delay = ugentools.DelayC.ar(
                delay_time=delay_time,
                maximum_delay_time=0.1,
                source=delay,
                )
            all_delays.extend(delay)
        source = ugentools.Mix.multichannel(all_delays, state['channel_count'])
        source /= inner_iterations
    source += lowpassed
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
    return source * ugentools.DC.kr(-12).db_to_amplitude() * -1


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    frequency=1,
    gain=0,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_pre)
factory = factory.with_signal_block(signal_block)
factory = factory.with_signal_block(signal_block_post)
factory = factory.with_feedback_loop(feedback_loop)

nrt_chorus_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

rt_chorus_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_chorus = nrt_chorus_factory.build(name='chorus')
rt_chorus = rt_chorus_factory.build(name='chorus')

__all__ = (
    'nrt_chorus',
    'nrt_chorus_factory',
    'rt_chorus',
    'rt_chorus_factory',
    )
