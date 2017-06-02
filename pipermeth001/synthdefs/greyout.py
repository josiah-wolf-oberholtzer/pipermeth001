# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_pre(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
    #source = ugentools.Limiter.ar(
    #    duration=ugentools.Rand.ir(0.005, 0.015),
    #    source=source,
    #    )
    return source


def signal_block(builder, source, state):
    channels = []
    fft_size = 1024 * 16
    hop_size = 1. / 64
    for channel in source:
        pv_chain = ugentools.FFT.new(
            source=channel,
            window_size=fft_size,
            hop=hop_size,
            )
        pv_chain = ugentools.PV_MagBelow(
            pv_chain=pv_chain,
            threshold=0.5,
            )
        channel = ugentools.IFFT.ar(
            pv_chain=pv_chain,
            window_size=fft_size,
            )
        channels.append(channel)
    source = synthdeftools.UGenArray(channels)
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
    gain=0,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_pre)
factory = factory.with_signal_block(signal_block)
factory = factory.with_signal_block(signal_block_post)

nrt_greyout_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

rt_greyout_factory = factory \
    .with_output(crossfaded=True)

nrt_greyout = nrt_greyout_factory.build(name='greyout')
rt_greyout = rt_greyout_factory.build(name='greyout')

__all__ = (
    'nrt_greyout',
    'nrt_greyout_factory',
    'rt_greyout',
    'rt_greyout_factory',
    )
