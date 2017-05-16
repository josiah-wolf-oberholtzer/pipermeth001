# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
    just_under_nyquist = (ugentools.SampleRate.ir() / 2) - 1000
    frequency = builder['frequency'].clip(20, just_under_nyquist)
    source = ugentools.LPF.ar(
        source=source,
        frequency=frequency,
        )
    source *= builder['gain'].db_to_amplitude()
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    frequency=10000,
    gain=0,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block)

nrt_lpf_dip_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

nrt_lpf_dip = nrt_lpf_dip_factory.build(name='lpf_dip')

__all__ = (
    'nrt_lpf_dip',
    'nrt_lpf_dip_factory',
    )
