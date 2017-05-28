# -*- encoding: utf-8 -*-
import supriya
from pipermeth001 import project_settings, synthdefs


### SESSION SETUP ###

session = supriya.Session.from_project_settings(project_settings)

release_time = 15

compressor_parameters = dict(
    band_1_threshold=-12,
    band_2_threshold=-12,
    band_3_threshold=-12,
    band_4_threshold=-15,
    band_5_threshold=-18,
    band_6_threshold=-24,
    band_7_threshold=-30,
    band_8_threshold=-36,
    band_1_slope_above=0.75,
    band_2_slope_above=0.75,
    band_3_slope_above=0.75,
    band_4_slope_above=0.75,
    band_5_slope_above=0.75,
    band_6_slope_above=0.75,
    band_7_slope_above=0.75,
    band_8_slope_above=0.75,
    )

### NOISE WASH PATTERN ###

noise_wash_pattern = supriya.patterntools.Pbind(
    synthdef=synthdefs.nrt_noise_wash,
    delta=supriya.patterntools.Pwhite(15, 30),
    duration=supriya.patterntools.Pwhite(15, 60),
    gain=supriya.patterntools.Pwhite(-24, -12),
    )

### FX PATTERN BASE ###

fx_pattern = supriya.patterntools.Pbind(
    add_action=supriya.AddAction.ADD_TO_TAIL,
    delta=supriya.patterntools.Pwhite(15, 30),
    duration=supriya.patterntools.Pwhite(30, 90),
    level=supriya.patterntools.Pwhite(0.25, 1.0),
    )

### ALLPASS ###

allpass_pattern = supriya.patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_allpass,
    gain=3,
    )

### CHORUS ###

chorus_pattern = supriya.patterntools.Pbindf(
    fx_pattern,
    level=1.0,
    synthdef=supriya.patterntools.Pseq([
        synthdefs.nrt_chorus_factory.build(name='chorus2', iterations=2),
        synthdefs.nrt_chorus_factory.build(name='chorus4', iterations=4),
        synthdefs.nrt_chorus_factory.build(name='chorus8', iterations=8),
        ], None),
    gain=3,
    )

### FREEVERB ###

freeverb_pattern = supriya.patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freeverb,
    damping=supriya.patterntools.Pwhite(),
    gain=3,
    room_size=supriya.patterntools.Pwhite(),
    )

### FREQSHIFT ###

freqshift_pattern = supriya.patterntools.Pbindf(
    fx_pattern,
    gain=6,
    level=supriya.patterntools.Pwhite(0.5, 1.0),
    sign=supriya.patterntools.Prand([-1, 1]),
    synthdef=synthdefs.nrt_freqshift,
    )

### PITCHSHIFT ###

pitchshift_pattern = supriya.patterntools.Pbindf(
    fx_pattern,
    gain=6,
    pitch_dispersion=supriya.patterntools.Pwhite(0., 0.02),
    pitch_shift=supriya.patterntools.Pwhite(-12.0, 12.0),
    synthdef=synthdefs.nrt_pitchshift,
    time_dispersion=supriya.patterntools.Pwhite(),
    window_size=supriya.patterntools.Pwhite(0.1, 2.0),
    )

### SOURCE PATTERN ###

source_pattern = supriya.patterntools.Ppar([noise_wash_pattern])
source_pattern = source_pattern.with_group(release_time=release_time)
source_pattern = source_pattern.with_effect(
    synthdef=synthdefs.multiband_compressor,
    release_time=release_time,
    pregain=12,
    **compressor_parameters
    )

### EFFECT PATTERN ###

effect_pattern = supriya.patterntools.Pgpar(
    [
        [
            allpass_pattern,
            chorus_pattern,
            freeverb_pattern,
            freqshift_pattern,
            pitchshift_pattern,
            allpass_pattern,
            ],
        ],
    release_time=release_time,
    )
effect_pattern = effect_pattern.with_group(release_time=release_time)
effect_pattern = effect_pattern.with_effect(
    synthdef=synthdefs.multiband_compressor,
    release_time=release_time,
    pregain=0,
    **compressor_parameters
    )

### GLOBAL PATTERN ###

global_pattern = supriya.patterntools.Pgpar(
    [source_pattern, effect_pattern],
    release_time=release_time,
    )
global_pattern = global_pattern.with_bus(release_time=release_time)

### RENDER ###

minutes = 5
iterations = 4
for i in range(iterations):
    with session.at(i * 10):
        session.inscribe(global_pattern, duration=60 * minutes, seed=i)

with session.at(0):
    session.add_synth(
        synthdef=synthdefs.multiband_compressor,
        add_action='ADD_TO_TAIL',
        duration=session.duration + release_time,
        pregain=0,
        **compressor_parameters
        )
    session.set_rand_seed()

noise_wash = session
__all__ = ['noise_wash']
