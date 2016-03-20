from supriya.tools import synthdeftools
from supriya.tools import ugentools


with synthdeftools.SynthDefBuilder(
    bus=0,
    frequencies=[250, 1000, 5000],
    clamp_times=[0.01, 0.01, 0.01, 0.01],
    gains=[1., 1., 1., 1.],
    relax_times=[0.1, 0.1, 0.1, 0.1],
    ratios_above=[1., 1., 1., 1.],
    ratios_below=[1., 1., 1., 1.],
    thresholds=[0.5, 0.5, 0.5, 0.5],
    ) as builder:
    source = ugentools.In.ar(bus=builder['bus'])
    band_1 = ugentools.LPF.ar(
        frequency=builder['frequencies'][0],
        source=source,
        )
    band_4 = ugentools.HPF.ar(
        frequency=builder['frequencies'][2],
        source=source,
        )
    center = source - band_1 - band_4
    band_2 = ugentools.LPF.ar(
        frequency=builder['frequencies'][1],
        source=center,
        )
    band_3 = ugentools.HPF.ar(
        frequency=builder['frequencies'][1],
        source=center,
        )
    band_1 = ugentools.CompanderD.ar(
        clamp_time=builder['clamp_times'][0],
        relax_time=builder['relax_times'][0],
        slope_above=synthdeftools.Op.reciprocal(builder['ratios_above'][0]),
        slope_below=synthdeftools.Op.reciprocal(builder['ratios_below'][0]),
        source=band_1,
        threshold=builder['thresholds'][0],
        ) * builder['gains'][0]
    band_2 = ugentools.CompanderD.ar(
        clamp_time=builder['clamp_times'][1],
        relax_time=builder['relax_times'][1],
        slope_above=synthdeftools.Op.reciprocal(builder['ratios_above'][1]),
        slope_below=synthdeftools.Op.reciprocal(builder['ratios_below'][1]),
        source=band_2,
        threshold=builder['thresholds'][1],
        ) * builder['gains'][1]
    band_3 = ugentools.CompanderD.ar(
        clamp_time=builder['clamp_times'][2],
        relax_time=builder['relax_times'][2],
        slope_above=synthdeftools.Op.reciprocal(builder['ratios_above'][2]),
        slope_below=synthdeftools.Op.reciprocal(builder['ratios_below'][2]),
        source=band_3,
        threshold=builder['thresholds'][2],
        ) * builder['gains'][2]
    band_4 = ugentools.CompanderD.ar(
        clamp_time=builder['clamp_times'][3],
        relax_time=builder['relax_times'][3],
        slope_above=synthdeftools.Op.reciprocal(builder['ratios_above'][3]),
        slope_below=synthdeftools.Op.reciprocal(builder['ratios_below'][3]),
        source=band_4,
        threshold=builder['thresholds'][3],
        ) * builder['gains'][3]
    source = ugentools.Sum4.new(
        input_one=band_1,
        input_two=band_2,
        input_three=band_3,
        input_four=band_4,
        )
    out = ugentools.ReplaceOut.ar(bus=builder['bus'], source=source)

multiband_compressor = builder.build()

__all__ = ['multiband_compressor']
