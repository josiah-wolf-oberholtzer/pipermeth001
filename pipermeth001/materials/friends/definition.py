# -*- encoding: utf-8 -*-
from supriya import (
    AddAction, Say, Session, patterntools
    )
from supriya import synthdefs as system_synthdefs
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

### WARP BUFFER PLAYER ###

warp_buffer_player_pattern = patterntools.Pbind(
    add_action=AddAction.ADD_TO_HEAD,
    buffer_id=patterntools.Prand(buffers, repetitions=None),
    delta=patterntools.Pwhite(0.0, 30.0),
    direction=patterntools.Prand([-1, 1], repetitions=None),
    duration=0,
    gain=patterntools.Pwhite(-18, -12),
    overlaps=patterntools.Prand([
        1,
        2,
        8,
        16,
        16,
        32,
        32,
        32,
        ], repetitions=None),
    rate=patterntools.Pwhite(64, 128),
    synthdef=patterntools.Prand([
        synthdefs.warp_buffer_player_factory.build(iterations=4),
        synthdefs.warp_buffer_player_factory.build(iterations=2),
        ], repetitions=None),
    transpose=patterntools.Pwhite(-12.0, 12.0),
    )

### FX PATTERN ###

fx_pattern = patterntools.Pbind(
    add_action=AddAction.ADD_TO_TAIL,
    delta=patterntools.Pwhite(15, 45),
    duration=patterntools.Pwhite(30, 90),
    level=patterntools.Pwhite(0., 0.5),
    )

### ALLPASS ###

allpass_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_allpass,
    gain=6,
    )

### BPF SWEEP ###

bpf_sweep_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_bpf_sweep,
    delta=patterntools.Pwhite(30, 90),
    duration=patterntools.Pwhite(30, 60),
    level=patterntools.Pwhite(0.0, 1.0),
    )

### CHORUS ###

chorus_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_chorus,
    gain=6,
    level=patterntools.Pwhite(0.5, 1.0),
    )

### FREEVERB ###

freeverb_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freeverb,
    damping=patterntools.Pwhite(),
    gain=6,
    room_size=patterntools.Pwhite(),
    )

### FREQSHIFT ###

freqshift_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freqshift,
    sign=patterntools.Prand([-1, 1]),
    )

### GREYOUT ###

greyout_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_greyout,
    gain=-3,
    )

### PITCHSHIFT ###

pitchshift_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_pitchshift,
    gain=6,
    level=patterntools.Pwhite(0.5, 1.0),
    pitch_dispersion=patterntools.Pwhite(0., 0.02),
    pitch_shift=patterntools.Pwhite(-12.0, 12.0),
    time_dispersion=patterntools.Pwhite(),
    window_size=patterntools.Pwhite(0.1, 2.0),
    )

### PATTERN ###

release_time = 30
pattern = patterntools.Ppar([
    warp_buffer_player_pattern,
    allpass_pattern,
    chorus_pattern,
    freeverb_pattern,
    freqshift_pattern,
    greyout_pattern,
    pitchshift_pattern,
    bpf_sweep_pattern,
    ])
pattern = pattern.with_group(release_time=release_time)
pattern = pattern.with_effect(
    system_synthdefs.multiband_compressor,
    release_time=release_time,
    pregain=6,
    frequency_1=250,
    frequency_2=1000,
    frequency_3=2500,
    postgain=0,
    )
pattern = pattern.with_bus(release_time=release_time)

### RENDER ###

minutes = 10  # 10
iterations = 5  # 3
for i in range(iterations):
    with session.at(i * 10):
        session.inscribe(pattern, duration=60 * minutes, seed=i)

with session.at(0):
    session.add_synth(
        synthdef=system_synthdefs.multiband_compressor,
        add_action='ADD_TO_TAIL',
        frequency_1=500,
        frequency_2=2000,
        frequency_3=5000,
        )

friends = session

__all__ = ['friends']
