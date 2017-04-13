# -*- encoding: utf-8 -*-
import math
from supriya import synthdeftools
from supriya import ugentools


def parameter_block(iterations, builder, state):
    # Frequency scaling
    transposition_flux = ugentools.LFNoise1.kr(
        frequency=[0.01] * iterations,
        ) * (1. / 16)
    transposition = builder['transpose']
    transposition += transposition_flux
    frequency_scaling = transposition.semitones_to_ratio()
    frequency_scaling *= builder['direction']
    # Buffer pointer
    pointer_scrub = ugentools.LFNoise1.kr(
        frequency=[0.01] * iterations,
        ) * state['window'] * 0.1
    pointer = state['line'] + pointer_scrub
    # Window rand ratio
    window_rand_ratio = ugentools.LFNoise2.kr(
        frequency=[0.01] * iterations)
    window_rand_ratio = window_rand_ratio.scale(-1, 1, 0., 0.1)
    # Window size
    window_size_variance = ugentools.LFNoise1.kr(
        frequency=[0.01] * iterations,
        ) * 0.1
    window_size = ugentools.LFNoise2.kr(
        frequency=0.01,
        ) + window_size_variance
    window_size = window_size.scale(-1.1, 1.1, 0.01, 0.5)
    # All parameters
    parameters = {
        'buffer_id': builder['buffer_id'],
        'frequency_scaling': frequency_scaling,
        'interpolation': 4,
        'overlaps': builder['overlaps'].as_int(),
        'pointer': pointer,
        'window_rand_ratio': window_rand_ratio,
        'window_size': window_size,
        }
    return parameters


def signal_block(builder, source, state):
    duration = ugentools.BufDur.kr(builder['buffer_id']) * builder['rate']
    state['line'] = ugentools.Line.kr(done_action=2, duration=duration)
    state['window'] = state['line'].hanning_window()
    iterations = int(state.get('iterations', 4))
    source = ugentools.Warp1.ar(
        **parameter_block(iterations, builder, state)
        )
    source = list(source)
    for i in range(iterations):
        if i % 2:
            source[i] *= -1
    if state['channel_count'] > 1:
        position = ugentools.LFNoise1.kr(
            frequency=[0.05] * iterations,
            )
        if state['channel_count'] > 2:
            source = ugentools.PanAz.ar(
                channel_count=state['channel_count'],
                position=position,
                source=source,
                )
        else:
            source = ugentools.Pan2.ar(
                position=position,
                source=source,
                )
    source = ugentools.Mix.multichannel(source, state['channel_count'])
    source *= state['window']
    source *= builder['gain'].db_to_amplitude()
    if iterations > 1:
        source *= 1. / math.sqrt(iterations)
    return source


warp_buffer_player_factory = synthdeftools.SynthDefFactory(
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

warp_buffer_player = warp_buffer_player_factory.build()

__all__ = [
    'warp_buffer_player',
    'warp_buffer_player_factory',
    ]
