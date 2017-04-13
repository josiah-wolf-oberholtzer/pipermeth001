# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    line = state['line'].scale(
        0,
        1,
        (ugentools.SampleRate.ir() / 2) - 1000,
        100,
        )
    source = ugentools.BPF.ar(
        source=source,
        frequency=line,
        reciprocal_of_q=1,
        )
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block)

nrt_bpf_sweep_factory = factory.with_output(
    crossfaded=True, leveled=True, windowed=True)

nrt_bpf_sweep = nrt_bpf_sweep_factory.build()

__all__ = (
    'nrt_bpf_sweep',
    'nrt_bpf_sweep_factory',
    )
