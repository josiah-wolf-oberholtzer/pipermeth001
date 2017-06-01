from supriya import synthdeftools
from supriya import ugentools


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
        pv_chain = ugentools.PV_LocalMax(
            pv_chain=pv_chain,
            threshold=0,
            )
        channel = ugentools.IFFT.ar(
            pv_chain=pv_chain,
            window_size=fft_size,
            )
        channels.append(channel)
    source = synthdeftools.UGenArray(channels)
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    )
factory = factory.with_input()
factory = factory.with_signal_block(signal_block)
nrt_pv_factory = factory \
    .with_output(crossfaded=True, leveled=True, windowed=True) \
    .with_rand_id()

nrt_pv = nrt_pv_factory.build('pv')

__all__ = (
    'nrt_pv_factory',
    'nrt_pv',
    )
