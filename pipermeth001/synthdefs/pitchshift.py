# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_one(builder, source, state):
    source = ugentools.PitchShift.ar(
        source=source,
        pitch_dispersion=builder['pitch_dispersion'],
        pitch_ratio=builder['pitch_shift'].semitones_to_ratio(),
        time_dispersion=builder['time_dispersion'] * builder['window_size'],
        window_size=builder['window_size'],
        )
    return source


def signal_block_two(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source = source * 2
    source = ugentools.Limiter.ar(source=source)
    return source


def feedback_loop(builder, source, state):
    source = synthdeftools.UGenArray((source[-1],) + source[:-1])
    source = source * 0.95 * ugentools.LFDNoise1.kr(frequency=0.1).cubed()
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    pitch_shift=0.,
    pitch_dispersion=0,
    time_dispersion=0,
    window_size=0.5,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_one)
factory = factory.with_signal_block(signal_block_two)
factory = factory.with_feedback_loop(feedback_loop)

nrt_pitchshift_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True)

rt_pitchshift_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_pitchshift = nrt_pitchshift_factory.build()
rt_pitchshift = rt_pitchshift_factory.build()

__all__ = (
    'nrt_pitchshift',
    'nrt_pitchshift_factory',
    'rt_pitchshift',
    'rt_pitchshift_factory',
    )
