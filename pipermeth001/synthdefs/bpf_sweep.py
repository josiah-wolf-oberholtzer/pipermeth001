# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    just_under_nyquist = (ugentools.SampleRate.ir() / 2) - 1000
    start_frequency = builder['start_frequency'].clip(
        100, just_under_nyquist)
    stop_frequency = builder['stop_frequency'].clip(
        100, just_under_nyquist)
    frequency = state['line'].scale(
        input_minimum=0,
        input_maximum=1,
        output_minimum=start_frequency,
        output_maximum=stop_frequency,
        exponential=True,
        )
    source = ugentools.BPF.ar(
        source=source,
        frequency=frequency,
        reciprocal_of_q=0.25,
        )
    source *= builder['gain'].db_to_amplitude()
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    gain=0,
    start_frequency=15000,
    stop_frequency=100,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block)

nrt_bpf_sweep_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

nrt_bpf_sweep = nrt_bpf_sweep_factory.build(name='bpf_sweep')

__all__ = (
    'nrt_bpf_sweep',
    'nrt_bpf_sweep_factory',
    )
