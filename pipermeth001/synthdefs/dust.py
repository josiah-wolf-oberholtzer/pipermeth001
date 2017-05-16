# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    iterations = int(state.get('iterations', 4))
    source = ugentools.Dust2.ar(
        density=[builder['density']] * iterations,
        )
    source /= builder['density'].square_root()
    if state['channel_count'] > 1:
        position = ugentools.LFNoise1.kr(
            frequency=[0.5] * iterations,
            ) * 0.5
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
    source *= builder['gain'].db_to_amplitude()
    source /= iterations
    return source


factory = synthdeftools.SynthDefFactory(density=10, gain=0)
factory = factory.with_signal_block(signal_block)
factory = factory.with_output(windowed=True)

nrt_dust = factory.with_rand_id().build(name='dust')

__all__ = ['nrt_dust']
