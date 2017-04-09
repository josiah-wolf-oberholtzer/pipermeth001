# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_one(builder, source, state):
    channels = []
    for channel in source:
        pv_chain = ugentools.FFT.new(
            source=channel,
            window_size=8192,
            hop=0.125,
            )
        pv_chain = ugentools.PV_MagBelow(
            pv_chain=pv_chain,
            threshold=5,
            )
        channel = ugentools.IFFT.ar(
            pv_chain=pv_chain,
            window_size=8192,
            )
        channel = ugentools.Convolution.ar(
            source=channel,
            kernel=ugentools.PinkNoise.ar() * 0.25,
            framesize=8192,
            )
        channels.append(channel)
    source = synthdeftools.UGenArray(channels)
    return source


def signal_block_two(builder, source, state):
    source = ugentools.LeakDC.ar(source=source)
    source = ugentools.Limiter.ar(source=source)
    return source


factory = synthdeftools.SynthDefFactory(channel_count=2)
factory = factory.with_input()
factory = factory.with_signal_block(signal_block_one)
factory = factory.with_signal_block(signal_block_two)

nrt_greyout_factory = factory.with_output(
    crossfaded=True, leveled=True, windowed=True)

rt_greyout_factory = factory \
    .with_gate() \
    .with_output(crossfaded=True) \
    .with_silence_detection()

nrt_greyout = nrt_greyout_factory.build()
rt_greyout = rt_greyout_factory.build()

__all__ = (
    'nrt_greyout',
    'nrt_greyout_factory',
    'rt_greyout',
    'rt_greyout_factory',
    )
