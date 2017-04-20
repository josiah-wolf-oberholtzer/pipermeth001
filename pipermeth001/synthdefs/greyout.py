# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block_pre(builder, source, state):
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
    source = ugentools.Limiter.ar(
        duration=ugentools.Rand.ir(0.005, 0.015),
        source=source,
        )
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


def feedback_loop(builder, source, state):
    source = synthdeftools.UGenArray((source[-1],) + source[:-1])
    source *= ugentools.LFNoise1.kr(frequency=0.05).squared().s_curve()
    source *= -0.75
    source *= ugentools.Line.kr(duration=0.1)  # protect against clicks
    source = ugentools.DelayC.ar(
        source=source,
        delay_time=ugentools.LFNoise1.kr(
            frequency=0.05,
            ).scale(-1, 1, 0.1, 0.2),
        maximum_delay_time=0.2,
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
#factory = factory.with_feedback_loop(feedback_loop)

nrt_greyout_factory = factory.with_output(
    crossfaded=True, leveled=True, windowed=True)

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
