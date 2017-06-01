from supriya import synthdeftools
from supriya import ugentools


def signal_block_pre(builder, source, state):
    source = ugentools.Limiter.ar(
        duration=ugentools.Rand.ir(0.005, 0.015),
        source=source,
        )
    return source


def signal_block(builder, source, state):
    frequencies, amplitudes, decay_times = [], [], []
    for _ in range(state.get('iterations') or 4):
        frequency = ugentools.ExpRand.ir(
            minimum=builder['frequency_minimum'],
            maximum=builder['frequency_maximum'],
            )
        frequencies.append(frequency)
        amplitudes.append(ugentools.ExpRand.ir())
        decay_times.append(ugentools.Rand.ir(1, 2))
    specifications = [frequencies, amplitudes, decay_times]
    source = ugentools.Klank.ar(
        source=source,
        decay_scale=builder['decay_scale'],
        frequency_offset=builder['frequency_offset'],
        frequency_scale=builder['frequency_scale'],
        specifications=specifications,
        )
    return source


def signal_block_post(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source *= builder['gain'].db_to_amplitude()
    source = ugentools.Limiter.ar(
        duration=ugentools.Rand.ir(0.005, 0.015),
        source=source,
        )
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    decay_scale=1,
    frequency_offset=0,
    frequency_scale=1,
    gain=0,
    frequency_minimum=20,
    frequency_maximum=1000,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_pre)
factory = factory.with_signal_block(signal_block)
factory = factory.with_signal_block(signal_block_post)

nrt_klank_random_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()
nrt_klank_random = nrt_klank_random_factory.build(name='klank_random')

__all__ = (
    'nrt_klank_random',
    'nrt_klank_random_factory',
    )
