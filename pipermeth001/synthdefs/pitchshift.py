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
    source = ugentools.PitchShift.ar(
        source=source,
        pitch_dispersion=builder['pitch_dispersion'],
        pitch_ratio=builder['pitch_shift'].semitones_to_ratio(),
        time_dispersion=builder['time_dispersion'] * builder['window_size'],
        window_size=builder['window_size'],
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
    gain=0,
    pitch_dispersion=0,
    pitch_shift=0.,
    time_dispersion=0,
    window_size=0.5,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_pre)
factory = factory.with_signal_block(signal_block)
factory = factory.with_signal_block(signal_block_post)
factory = factory.with_feedback_loop(feedback_loop)

nrt_pitchshift_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

rt_pitchshift_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_pitchshift = nrt_pitchshift_factory.build(name='pitchshift')
rt_pitchshift = rt_pitchshift_factory.build(name='pitchshift')

__all__ = (
    'nrt_pitchshift',
    'nrt_pitchshift_factory',
    'rt_pitchshift',
    'rt_pitchshift_factory',
    )
