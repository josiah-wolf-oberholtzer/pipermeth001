# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def parameter_block(iterations, builder, state):
    transposition = builder['transpose'] + ugentools.LFNoise2.kr(
        frequency=[0.01] * iterations,
        ) * 0.125
    frequency_scaling = transposition.semitones_to_ratio()
    frequency_scaling *= builder['direction']
    pointer_scrub = ugentools.LFNoise2.kr(
        frequency=[0.01] * iterations,
        ) * state['window'] * 0.2
    pointer = state['line'] + pointer_scrub
    window_size = ugentools.LFNoise2.kr(
        frequency=[0.05] * iterations,
        ).scale(-1, 1, 0.125, 0.375)
    parameters = {
        'buffer_id': builder['buffer_id'],
        'channel_count': 1,
        'frequency_scaling': frequency_scaling,
        'interpolation': 4,
        'overlaps': builder['overlaps'].as_int(),
        'pointer': pointer,
        'window_rand_ratio': 0.01,
        'window_size': window_size,
        }
    return parameters


def signal_block(builder, source, state):
    duration = ugentools.BufDur.kr(builder['buffer_id']) * builder['rate']
    state['line'] = ugentools.Line.kr(done_action=2, duration=duration)
    state['window'] = state['line'].hanning_window()
    iterations = 4
    source = ugentools.Warp1.ar(
        **parameter_block(iterations, builder, state)
        )
    if state['channel_count'] > 1:
        position = ugentools.LFNoise2.kr(
            frequency=[0.01] * iterations,
            )
        source = ugentools.PanAz.ar(
            channel_count=state['channel_count'],
            source=source,
            position=position,
            width=1,
            )
    source = ugentools.Mix.multichannel(source, state['channel_count'])
    source = source * state['window'] * builder['gain'].db_to_amplitude()
    return source


factory = synthdeftools.SynthDefFactory(
    buffer_id=0,
    channel_count=2,
    direction=1,
    gain=0,
    overlaps=32,
    rate=1,
    transpose=0,
    ) \
    .with_output() \
    .with_signal_block(signal_block)

warp_buffer_player = factory.build()

__all__ = ['warp_buffer_player']
