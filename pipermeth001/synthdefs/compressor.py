# -*- encoding: utf-8 -*-
from supriya import synthdeftools
from supriya import ugentools


def parameter_block(builder, state):
    frequencies = state['frequencies']
    band_count = len(frequencies) + 1
    for i in range(band_count):
        band_name = 'band_{}_'.format(i + 1)
        builder._add_parameter(band_name + 'pregain', 0, 'CONTROL')
        builder._add_parameter(band_name + 'clamp_time', 0.01, 'CONTROL')
        builder._add_parameter(band_name + 'relax_time', 0.1, 'CONTROL')
        builder._add_parameter(band_name + 'threshold', -6, 'CONTROL')
        builder._add_parameter(band_name + 'slope_above', 0.5, 'CONTROL')
        builder._add_parameter(band_name + 'slope_below', 1.0, 'CONTROL')
        builder._add_parameter(band_name + 'postgain', 0, 'CONTROL')


def signal_block(builder, source, state):
    source *= builder['pregain'].db_to_amplitude()
    bands = []
    frequencies = state['frequencies']
    for frequency in frequencies:
        band = ugentools.LPF.ar(
            source=source,
            frequency=frequency,)
        bands.append(band)
        source -= band
    bands.append(source)
    compressors = []
    for i, band in enumerate(bands):
        band_name = 'band_{}_'.format(i + 1)
        band *= builder[band_name + 'pregain'].db_to_amplitude()
        band = ugentools.CompanderD.ar(
            clamp_time=builder[band_name + 'clamp_time'],
            relax_time=builder[band_name + 'relax_time'],
            slope_above=builder[band_name + 'slope_above'],
            slope_below=builder[band_name + 'slope_below'],
            source=band,
            threshold=builder[band_name + 'threshold'].db_to_amplitude(),
            )
        band *= builder[band_name + 'postgain'].db_to_amplitude()
        compressors.extend(band)
    assert len(compressors) == state['channel_count'] * (len(frequencies) + 1)
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
    limiter_lookahead=0.01,
    )
factory = factory.with_initial_state(
    frequencies=(150, 300, 600, 1200, 2400, 4800, 9600),
    )
factory = factory.with_parameter_block(parameter_block)
factory = factory.with_input()
factory = factory.with_signal_block(signal_block)
factory = factory.with_output(replacing=True)

multiband_compressor = factory.build(name='compressor')

__all__ = (
    'multiband_compressor',
    )
