# -*- encoding: utf-8 -*-
from supriya import Session
from supriya import patterntools
from supriya import synthdefs

from pipermeth001 import synthdefs as project_synthdefs


spoopy_v0 = Session(0, 2)

default_pattern = patterntools.Pbind(
    synthdef=synthdefs.default,
    amplitude=patterntools.Pwhite(),
    delta=patterntools.Pwhite(0., 2.),
    duration=patterntools.Pwhite(0.1, 0.5),
    frequency=patterntools.Pwhite(minimum=55, maximum=1760),
    pan=patterntools.Pwhite(-1.0, 1.0),
    )

dust_pattern = patterntools.Pbind(
    synthdef=project_synthdefs.durated_dust,
    delta=patterntools.Pwhite(1.0, 15),
    duration=patterntools.Pwhite(0.05, 5),
    level=patterntools.Pwhite(),
    )

pitchshift_pattern = patterntools.Pbind(
    synthdef=project_synthdefs.durated_pitchshift,
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 10),
    level=patterntools.Pwhite(),
    pitch_dispersion=patterntools.Pwhite(0., 0.1),
    pitch_shift=patterntools.Pwhite(-12.0, 12.0),
    time_dispersion=patterntools.Pwhite(),
    window_size=patterntools.Pwhite(0.1, 2.0),
    )

freeverb_pattern = patterntools.Pbind(
    synthdef=project_synthdefs.durated_freeverb,
    damping=patterntools.Pwhite(),
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 20),
    level=patterntools.Pwhite(),
    room_size=patterntools.Pwhite(),
    )

allpass_pattern = patterntools.Pbind(
    synthdef=project_synthdefs.durated_allpass,
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 10),
    level=patterntools.Pwhite(),
    )

mono_chorus_pattern = patterntools.Pbind(
    synthdef=project_synthdefs.durated_mono_chorus,
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 20),
    level=patterntools.Pwhite(),
    )

freqshift_pattern = patterntools.Pbind(
    synthdef=project_synthdefs.durated_freqshift,
    delta=patterntools.Pwhite(0.5, 20),
    duration=patterntools.Pwhite(0.5, 10),
    level=patterntools.Pwhite(),
    )

pattern = patterntools.Pbus(
    patterntools.Ppar([
        allpass_pattern,
        mono_chorus_pattern,
        pitchshift_pattern,
        freeverb_pattern,
        freqshift_pattern,
        allpass_pattern,
        default_pattern,
        dust_pattern,
        ]),
    )

durations = []
with spoopy_v0.at(0):
    group = spoopy_v0.add_group()
    for i in range(6):
        duration = group.inscribe(pattern, duration=180, seed=i)
        durations.append(duration)
    compressor_synth = spoopy_v0.add_synth(
        add_action='ADD_TO_TAIL',
        synthdef=synthdefs.multiband_compressor,
        frequency_1=200,
        frequency_2=2000,
        frequency_3=5000,
        band_1_threshold=0,
        band_2_threshold=-6,
        band_3_threshold=-12,
        band_4_threshold=-18,
        band_1_slope_above=1,
        band_2_slope_above=0.5,
        band_3_slope_above=0.25,
        band_4_slope_above=0.125,
        band_1_pregain=0,
        band_2_pregain=0,
        band_3_pregain=-3,
        band_4_pregain=-3,
        )
    limiter_synth = spoopy_v0.add_synth(
        add_action='ADD_TO_TAIL',
        synthdef=project_synthdefs.limiter,
        )


max_duration = max(durations) + 10
for node in (group, compressor_synth, limiter_synth):
    node.set_duration(max_duration)
