# -*- encoding: utf-8 -*-
"""
Something funny is happening in NRT compilation.

- Zero-duration events aren't being handled properly.
  - They don't appear in NRT Session.to_strings(). The states just aren't
    there.
  - Investigate adding a second pair of node:children and node:parent mappings
    in nonrealtimetools.State.
  - The extra mappings hold the node hierarchy before culling stop nodes (which
    includes zero-duration nodes).
  - When cloning, use the post-cull hierarchy mappings.
- Is the last non-infinite state properly desparsified?
  - Maybe an artifact from the split&delete changes in Node.set_duration().
- Looks like node settings don't count against sparseness.
"""
from supriya import AddAction, Session, patterntools
from pipermeth001 import project_settings, synthdefs
from pipermeth001.materials import (
    libretto_x,
    compressor_settings,
    )

### SESSION SETUP ###

session = Session.from_project_settings(project_settings)

release_time = 15

minutes = 3

layer_count = 2

### BUFFERS ###

buffers = []
with session.at(0):
    for say in libretto_x:
        buffer_ = session.add_buffer(channel_count=1, file_path=say)
        buffers.append(buffer_)

### WARP BUFFER PLAYER ###

warp_buffer_player_pattern = patterntools.Pbind(
    synthdef=patterntools.Prand([
        synthdefs.warp_buffer_player_factory.build(name='warp2', iterations=2),
        synthdefs.warp_buffer_player_factory.build(name='warp4', iterations=4),
        synthdefs.warp_buffer_player_factory.build(name='warp8', iterations=8),
        ], repetitions=None),
    add_action=AddAction.ADD_TO_HEAD,
    buffer_id=patterntools.Prand(buffers, repetitions=None),
    delta=patterntools.Pwhite(0, 30),
    duration=0,
    direction=patterntools.Prand([-1, 1], repetitions=None),
    gain=patterntools.Pwhite(-12, 0),
    overlaps=patterntools.Prand([16, 32] * 100, None),
    #overlaps=patterntools.Prand(
    #    [1, 2, 4, 8, 8, 16, 16, 16, 32, 32, 32] * 4, None,
    #    )
    rate=patterntools.Pwhite(4, 128),
    transpose=patterntools.Pwhite(-12.0, 12.0),
    )

### FX PATTERN BASE ###

fx_pattern = patterntools.Pbind(
    add_action=AddAction.ADD_TO_TAIL,
    delta=patterntools.Pwhite(15, 60),
    duration=patterntools.Pwhite(30, 90),
    level=patterntools.Pwhite(0.25, 1.0),
    )

### ALLPASS ###

allpass_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_allpass,
    gain=0,
    )

### BPF SWEEP ###

bpf_sweep_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_bpf_sweep,
    delta=patterntools.Pwhite(30, 90),
    duration=patterntools.Pwhite(30, 60),
    gain=3,
    level=patterntools.Pwhite(0., 0.5),
    start_frequency=patterntools.Pwhite(10000, 20000),
    stop_frequency=patterntools.Pwhite(100, 5000),
    )

### CHORUS ###

chorus_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_chorus_factory.build(
        name='chorus8', iterations=8),
    frequency=patterntools.Pwhite() * 2,
    gain=3,
    )

### FREEVERB ###

freeverb_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freeverb,
    damping=patterntools.Pwhite() ** 0.25,
    gain=3,
    room_size=patterntools.Pwhite() ** 0.25,
    )

### FREQSHIFT ###

freqshift_pattern = patterntools.Pbindf(
    fx_pattern,
    level=patterntools.Pwhite(0.5, 1.0),
    synthdef=synthdefs.nrt_freqshift,
    sign=patterntools.Prand([-1, 1]),
    )

### GREYOUT ###

greyout_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_greyout,
    gain=0,
    delta=patterntools.Pwhite(45, 90),
    )

### LPF DIP ###

lpf_dip_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_lpf_dip,
    delta=patterntools.Pwhite(30, 90),
    duration=patterntools.Pwhite(30, 60),
    gain=3,
    level=patterntools.Pwhite(0., 0.5),
    frequency=patterntools.Pwhite(1000, 10000),
    )

### PITCHSHIFT ###

pitchshift_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_pitchshift,
    gain=3,
    pitch_dispersion=patterntools.Pwhite(0., 0.02),
    pitch_shift=patterntools.Pwhite(-12.0, 12.0),
    time_dispersion=patterntools.Pwhite(),
    window_size=patterntools.Pwhite(0.1, 2.0),
    )

### MAIN PATTERN ###

source_pattern = patterntools.Ppar([warp_buffer_player_pattern])
source_pattern = source_pattern.with_group(release_time=release_time)
source_pattern = source_pattern.with_effect(
    synthdef=synthdefs.multiband_compressor,
    release_time=release_time,
    pregain=12,
    **compressor_settings
    )

### EFFECT PATTERN ###

effect_pattern = patterntools.Ppar([
    allpass_pattern,
    chorus_pattern,
    freeverb_pattern,
    freqshift_pattern,
    greyout_pattern,
    pitchshift_pattern,
    bpf_sweep_pattern,
    lpf_dip_pattern,
    ])
effect_pattern = effect_pattern.with_group(release_time=release_time)
effect_pattern = effect_pattern.with_effect(
    synthdef=synthdefs.multiband_compressor,
    release_time=release_time,
    pregain=6,
    **compressor_settings
    )

### GLOBAL PATTERN ###

global_pattern = patterntools.Pgpar(
    [
        source_pattern,
        effect_pattern,
        ],
    release_time=release_time,
    )
global_pattern = global_pattern.with_bus(release_time=release_time)

### RENDER ###

for i in range(layer_count):
    with session.at(i * 10):
        session.inscribe(global_pattern, duration=60 * minutes, seed=i)

with session.at(0):
    session.add_synth(
        synthdef=synthdefs.multiband_compressor,
        add_action='ADD_TO_TAIL',
        duration=session.duration + release_time,
        pregain=-6,
        **compressor_settings
        )

session.set_rand_seed(offset=0)
