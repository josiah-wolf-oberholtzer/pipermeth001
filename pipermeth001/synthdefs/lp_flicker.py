from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    line = state['line']
    lfo_frequency = line.scale(
        0, 1,
        ugentools.ExpRand.ir(1, 10),
        ugentools.ExpRand.ir(1, 10),
        exponential=True,
        )
    lfo = ugentools.LFPar.kr(frequency=lfo_frequency)
    frequency = lfo.scale(
        -1, 1,
        ugentools.Rand.ir(5000, ugentools.SampleRate.ir() * 0.5),
        ugentools.SampleRate.ir() * 0.5,
        )
    source = ugentools.LPF.ar(
        source=source,
        frequency=frequency,
        )
    return source


factory = synthdeftools.SynthDefFactory(channel_count=2) \
    .with_input() \
    .with_signal_block(signal_block) \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

lp_flicker = factory.build(name='lp_flicker')

__all__ = (
    'lp_flicker',
    )
