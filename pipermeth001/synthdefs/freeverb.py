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


def signal_block(builder, source, state):
    source = ugentools.FreeVerb.ar(
        source=source,
        damping=builder['damping'],
        room_size=builder['room_size'],
        mix=1.0,
        )
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
    source *= ugentools.LFNoise1.kr(frequency=0.05).squared().s_curve()
    source *= -1
    source = ugentools.Limiter.ar(
        source=source,
        level=ugentools.DC.kr(-3).db_to_amplitude(),
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
    damping=0.9,
    gain=0,
    room_size=0.5,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_pre)
factory = factory.with_signal_block(signal_block)
factory = factory.with_signal_block(signal_block_post)
factory = factory.with_feedback_loop(feedback_loop)

nrt_freeverb_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

rt_freeverb_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_freeverb = nrt_freeverb_factory.build(name='freeverb')
rt_freeverb = rt_freeverb_factory.build(name='freeverb')

__all__ = (
    'nrt_freeverb',
    'nrt_freeverb_factory',
    'rt_freeverb',
    'rt_freeverb_factory',
    )
