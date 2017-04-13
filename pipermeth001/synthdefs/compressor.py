# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def signal_block(builder, source, state):
    source *= builder['pregain'].db_to_amplitude()
    bands = []
    frequencies = [150, 300, 600, 1200, 2400, 4800, 9600]
    for frequency in frequencies:
        band = ugentools.LPF.ar(
            source=source,
            frequency=frequency,
            )
        bands.append(band)
        source -= band
    bands.append(source)
    compressors = []
    for i, band in enumerate(bands):
        band_name = 'band_{}_'.format(i + 1)
        band *= builder[band_name + 'pregain']
        band = ugentools.CompanderD.ar(
            clamp_time=builder[band_name + 'clamp_time'],
            relax_time=builder[band_name + 'relax_time'],
            slope_above=builder[band_name + 'slope_above'],
            slope_below=builder[band_name + 'slope_below'],
            source=band,
            threshold=builder[band_name + 'threshold'].db_to_amplitude(),
            )
        band *= builder[band_name + 'postgain']
        compressors.extend(band)
    assert len(compressors) == state['channel_count'] * 8
    source = ugentools.Mix.multichannel(compressors, state['channel_count'])
    assert len(source) == state['channel_count']
    source *= builder[band_name + 'postgain'].db_to_amplitude()
    source = ugentools.Limiter.ar(
        source=source,
        duration=builder['limiter_lookahead'],
        )
    return source


factory = synthdeftools.SynthDefFactory(
    channel_count=2,
    pregain=0,
    postgain=0,
    band_1_pregain=0,
    band_1_clamp_time=0.01,
    band_1_relax_time=0.1,
    band_1_threshold=-12,
    band_1_slope_above=0.5,
    band_1_slope_below=1.0,
    band_1_postgain=0,

    band_2_pregain=0,
    band_2_clamp_time=0.01,
    band_2_relax_time=0.1,
    band_2_threshold=-12,
    band_2_slope_above=0.5,
    band_2_slope_below=1.0,
    band_2_postgain=0,

    band_3_pregain=0,
    band_3_clamp_time=0.01,
    band_3_relax_time=0.1,
    band_3_threshold=-12,
    band_3_slope_above=0.5,
    band_3_slope_below=1.0,
    band_3_postgain=0,

    band_4_pregain=0,
    band_4_clamp_time=0.01,
    band_4_relax_time=0.1,
    band_4_threshold=-12,
    band_4_slope_above=0.5,
    band_4_slope_below=1.0,
    band_4_postgain=0,

    band_5_pregain=0,
    band_5_clamp_time=0.01,
    band_5_relax_time=0.1,
    band_5_threshold=-12,
    band_5_slope_above=0.5,
    band_5_slope_below=1.0,
    band_5_postgain=0,

    band_6_pregain=0,
    band_6_clamp_time=0.01,
    band_6_relax_time=0.1,
    band_6_threshold=-12,
    band_6_slope_above=0.5,
    band_6_slope_below=1.0,
    band_6_postgain=0,

    band_7_pregain=0,
    band_7_clamp_time=0.01,
    band_7_relax_time=0.1,
    band_7_threshold=-12,
    band_7_slope_above=0.5,
    band_7_slope_below=1.0,
    band_7_postgain=0,

    band_8_pregain=0,
    band_8_clamp_time=0.01,
    band_8_relax_time=0.1,
    band_8_threshold=-12,
    band_8_slope_above=0.5,
    band_8_slope_below=1.0,
    band_8_postgain=0,

    limiter_lookahead=0.1,
    )

factory = factory.with_input()
factory = factory.with_signal_block(signal_block)
factory = factory.with_output()

multiband_compressor = factory.build()

__all__ = (
    'multiband_compressor',
    )
