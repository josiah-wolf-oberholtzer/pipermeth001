# -*- encoding: utf-8 -*-
from supriya import (
    AddAction, Say, Session, patterntools
    )
from supriya import synthdefs as system_synthdefs
from pipermeth001 import project_settings, synthdefs

### SESSION SETUP ###

minutes = 2
iterations = 3
session = Session.from_project_settings(project_settings)

### BUFFERS ###

says = []
for voice in ['Daniel', 'Fiona', 'Victoria', 'Tessa', 'Karen', 'Thomas']:
    for text in [
        'Feed me.', 'Heal me.', 'Dance with me.', 'Teach me.',
        'Hold me.', 'Touch me.', 'Love me.',
        'Show me a path.', 'Give me light.', 'Release me.',
        'Let me help you.', "Don't hurt me.",
        'Be true.', "Don't leave me.", 'Talk to me.',
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
    delta=patterntools.Pwhite(0.0, 16.0),
    direction=patterntools.Prand([-1, 1], repetitions=None),
    duration=0,
    gain=patterntools.Pwhite(-9, -6),
    overlaps=patterntools.Prand([2, 16, 1, 16, 8, 32, 32], repetitions=None),
    pan=patterntools.Pwhite(-1.0, 1.0),
    rate=patterntools.Pwhite(64, 128),
    synthdef=patterntools.Prand([
        synthdefs.warp_buffer_player_factory.build(iterations=4),
        synthdefs.warp_buffer_player_factory.build(iterations=1),
        ], repetitions=None),
    transpose=patterntools.Pwhite(-12.0, 12.0),
    )

### FX PATTERN ###

fx_pattern = patterntools.Pbind(
    add_action=AddAction.ADD_TO_TAIL,
    delta=patterntools.Pwhite(15, 30),
    duration=patterntools.Pwhite(30, 60),
    level=patterntools.Pwhite(0., 0.5),
    )

### ALLPASS ###

allpass_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_allpass,
    )

### CHORUS ###

chorus_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_chorus,
    )

### FREEVERB ###

freeverb_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freeverb,
    damping=patterntools.Pwhite(),
    room_size=patterntools.Pwhite(),
    )

### FREQSHIFT ###

freqshift_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_freqshift,
    )

### GREYOUT ###

greyout_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_greyout,
    )

### PITCHSHIFT ###

pitchshift_pattern = patterntools.Pbindf(
    fx_pattern,
    synthdef=synthdefs.nrt_pitchshift,
    pitch_dispersion=patterntools.Pwhite(0., 0.02),
    pitch_shift=patterntools.Pwhite(-12.0, 12.0),
    time_dispersion=patterntools.Pwhite(),
    window_size=patterntools.Pwhite(0.1, 2.0),
    )

### RENDER ###

pattern = patterntools.Pbus(
    patterntools.Ppar([
        warp_buffer_player_pattern,
        #allpass_pattern,
        #chorus_pattern,
        #freeverb_pattern,
        #freqshift_pattern,
        #greyout_pattern,
        #pitchshift_pattern,
        ]),
    release_time=30.0,
    )

for i in range(iterations):
    with session.at(i * 15):
        session.inscribe(pattern, duration=60 * minutes, seed=i)

with session.at(0):
    pregain = -6 + ((iterations - 1) * -3)
    session.add_synth(
        add_action=AddAction.ADD_TO_TAIL,
        synthdef=system_synthdefs.multiband_compressor,
        band_1_pregain=pregain,
        band_2_pregain=pregain,
        band_3_pregain=pregain,
        band_4_pregain=pregain,
        )

friends = session

__all__ = ['friends']
