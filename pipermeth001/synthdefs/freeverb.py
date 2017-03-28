# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_one(builder, source, state):
    source = ugentools.FreeVerb.ar(
        source=source,
        damping=builder['damping'],
        room_size=builder['room_size'],
        mix=1.0,
        )
    return source


def signal_block_two(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    return source


factory = synthdeftools.SynthDefFactory(channel_count=2)
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_one)
factory = factory.with_signal_block(signal_block_two)

nrt_freeverb_factory = factory.with_output(
    crossfaded=True,
    leveled=True,
    windowed=True,
    )

rt_freeverb_factory = factory \
    .with_silence_detection() \
    .with_output(crossfaded=True)

nrt_freeverb = nrt_freeverb_factory.build()
rt_freeverb = rt_freeverb_factory.build()

__all__ = (
    'nrt_freeverb',
    'nrt_freeverb_factory',
    'rt_freeverb',
    'rt_freeverb_factory',
    )
