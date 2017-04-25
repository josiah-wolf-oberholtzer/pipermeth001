# -*- encoding: utf-8 -*-
from supriya import AddAction, Say, Session, patterntools
from pipermeth001 import project_settings, synthdefs

### SESSION SETUP ###

session = Session.from_project_settings(project_settings)

### BUFFERS ###

says = []
for voice in ['Daniel', 'Fiona', 'Victoria', 'Tessa', 'Karen', 'Thomas']:
    for text in [
        'Be true.', "Don't leave me.", 'Talk to me.',
        'Feed me.', 'Heal me.', 'Dance with me.', 'Teach me.',
        'Hold me.', 'Touch me.', 'Love me.',
        'Let me help you.', "Don't hurt me.",
        'Show me a path.', 'Give me light.', 'Release me.',
        ]:
        says.append(Say(text, voice=voice))

buffers = []
with session.at(0):
    for say in says:
        buffer_ = session.add_buffer(channel_count=1, file_path=say)
        buffers.append(buffer_)

### DUST ###

dust_pattern = patterntools.Pbind(
    add_action=AddAction.ADD_TO_HEAD,
    duration=patterntools.Pwhite(10, 30),
    delta=patterntools.Pwhite(15, 90),
    synthdef=synthdefs.nrt_dust,
    density=patterntools.Pwhite(1, 50),
    gain=-24,
    )

### WARP BUFFER PLAYER ###

warp_buffer_player_pattern = patterntools.Pbind(
    synthdef=patterntools.Prand([
        synthdefs.warp_buffer_player_factory.build(name='warp4', iterations=4),
        synthdefs.warp_buffer_player_factory.build(name='warp2', iterations=2),
        ], repetitions=None),
    add_action=AddAction.ADD_TO_HEAD,
    buffer_id=patterntools.Prand(buffers, repetitions=None),
    delta=patterntools.Pwhite(0, 30),
    duration=0,
    direction=patterntools.Prand([-1, 1], repetitions=None),
    gain=patterntools.Pwhite(-18, -12),
    overlaps=patterntools.Prand(
        [1, 2, 8, 16, 16, 32, 32, 32] * 4,
        repetitions=None),
    rate=patterntools.Pwhite(64, 128),
    transpose=patterntools.Pwhite(-12.0, 12.0),
    )

#### OVERRIDES ###
#
#dust_pattern = patterntools.Pbindf(
#    dust_pattern,
#    duration=40,
#    delta=15,
#    )
#warp_buffer_player_pattern = patterntools.Pbindf(
#    warp_buffer_player_pattern,
#    duration=32,
#    delta=16,
#    )

### FX PATTERN ###

fx_pattern = patterntools.Pbind(
    add_action=AddAction.ADD_TO_TAIL,
    delta=patterntools.Pwhite(15, 60),
    duration=patterntools.Pwhite(30, 90),
    )

### ALLPASS ###

allpass_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_allpass,
    gain=0,
    level=patterntools.Pwhite(0.25, 1.0),
    )

### BPF SWEEP ###

bpf_sweep_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_bpf_sweep,
    delta=patterntools.Pwhite(30, 90),
    duration=patterntools.Pwhite(30, 60),
    gain=-0,
    level=patterntools.Pwhite(0.5, 1.0),
    start_frequency=patterntools.Pwhite(10000, 20000),
    stop_frequency=patterntools.Pwhite(100, 5000),
    )

### CHORUS ###

chorus_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_chorus,
    gain=3,
    level=patterntools.Pwhite(0.25, 1.0),
    )

### FREEVERB ###

freeverb_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freeverb,
    damping=patterntools.Pwhite(),
    gain=6,
    level=patterntools.Pwhite(0.25, 1.0),
    room_size=patterntools.Pwhite(),
    )

### FREQSHIFT ###

freqshift_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freqshift,
    level=patterntools.Pwhite(0., 0.75),
    sign=patterntools.Prand([-1, 1]),
    )

### GREYOUT ###

greyout_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_greyout,
    gain=-6,
    delta=patterntools.Pwhite(45, 90),
    level=patterntools.Pwhite(0.25, 1.0),
    )

### LPF DIP ###

lpf_dip_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_lpf_dip,
    delta=patterntools.Pwhite(30, 90),
    duration=patterntools.Pwhite(30, 60),
    gain=-6,
    level=patterntools.Pwhite(0.5, 1.0),
    frequency=patterntools.Pwhite(7500, 10000),
    )

### PITCHSHIFT ###

pitchshift_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_pitchshift,
    gain=3,
    level=patterntools.Pwhite(0.5, 1.0),
    pitch_dispersion=patterntools.Pwhite(0., 0.02),
    pitch_shift=patterntools.Pwhite(-12.0, 12.0),
    time_dispersion=patterntools.Pwhite(),
    window_size=patterntools.Pwhite(0.1, 2.0),
    )

### PATTERN ###

release_time = 15

compressor_parameters = dict(
    band_1_threshold=-12,
    band_2_threshold=-12,
    band_3_threshold=-12,
    band_4_threshold=-12,
    band_5_threshold=-15,
    band_6_threshold=-18,
    band_7_threshold=-21,
    band_8_threshold=-24,
    limiter_lookahead=5,
    )

source_pattern = patterntools.Ppar([
    #dust_pattern,
    warp_buffer_player_pattern,
    ])
source_pattern = source_pattern.with_group(release_time=release_time)
source_pattern = source_pattern.with_effect(
    synthdefs.multiband_compressor,
    release_time=release_time,
    **compressor_parameters
    )

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
    synthdefs.multiband_compressor,
    release_time=release_time,
    pregain=12,
    band_1_slope_above=3 / 4,
    band_2_slope_above=3 / 4,
    band_3_slope_above=3 / 4,
    band_4_slope_above=3 / 4,
    band_5_slope_above=3 / 4,
    band_6_slope_above=3 / 4,
    band_7_slope_above=3 / 4,
    band_8_slope_above=3 / 4,
    **compressor_parameters
    )

global_pattern = patterntools.Pgpar([
    source_pattern,
    effect_pattern,
    ], release_time=release_time)
global_pattern = global_pattern.with_bus(release_time=release_time)

### RENDER ###

minutes = 6
iterations = 1
for i in range(iterations):
    with session.at(i * 10):
        session.inscribe(global_pattern, duration=60 * minutes, seed=i)

with session.at(0):
    session.add_synth(
        synthdef=synthdefs.multiband_compressor,
        add_action='ADD_TO_TAIL',
        pregain=0,
        band_1_threshold=-12,
        band_2_threshold=-12,
        band_3_threshold=-12,
        band_4_threshold=-12,
        band_5_threshold=-12,
        band_6_threshold=-12,
        band_7_threshold=-12,
        band_8_threshold=-12,
        limiter_lookahead=5,
        )

friends = session

#import pprint
#pprint.pprint(session.to_lists())
print(session.to_strings(include_timespans=True))

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
- Sometimes, usually near the end of an NRT session, I see /g_head commands.
  - It appears that groups are ending early, and their contents are being
    ejected, often out-of-order into the group's parent. This causes fade-outs
    to not happen properly, amongst other problems.
- Pattern-created groups should probably ~split-and-delete~ nodes which extend
  beyond them.
- Additionally, add in support for displaying the non-md5 names of synths in
  NRT Session.to_strings(). This will make debugging a lot simpler.
  - What is that steady-repetition click, approx 0.5 seconds in cycle? Seeing
    the synth names will help ID it.

"""

__all__ = ['friends']
