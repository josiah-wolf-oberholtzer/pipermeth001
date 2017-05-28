# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    source = ugentools.PinkNoise.ar()
    source = ugentools.PanB2.ar(
        source=source,
        azimuth=ugentools.LFNoise2.kr(frequency=0.05),
        gain=1,
        )
    source = ugentools.DecodeB2.ar(
        channel_count=state['channel_count'],
        w=source[0],
        x=source[1],
        y=source[2],
        )
    hp_frequency = state['line'].clip(0, 0.5) * 2
    hp_frequency = hp_frequency.scale(
        0, 1,
        ugentools.SampleRate.ir() * 0.45, 20,
        exponential=True,
        )
    lp_frequency = state['line'].clip(0.5, 1).scale(0.5, 1., 0, 1)
    lp_frequency = lp_frequency.scale(
        0, 1,
        ugentools.SampleRate.ir() * 0.45, 20,
        )
    source = ugentools.BHiPass.ar(
        source=source,
        frequency=hp_frequency,
        reciprocal_of_q=10,
        )
    source = ugentools.BLowPass.ar(
        source=source,
        frequency=lp_frequency,
        reciprocal_of_q=10,
        )
    source *= builder['gain'].db_to_amplitude()
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    gain=0,
    )
factory = factory.with_signal_block(signal_block)

nrt_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

nrt_noise_wash = nrt_factory.build(name='noise_wash')


__all__ = (
    'nrt_noise_wash',
    )
