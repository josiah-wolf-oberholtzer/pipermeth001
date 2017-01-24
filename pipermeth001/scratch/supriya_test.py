# -*- encoding: utf-8 -*-
import subprocess
import time

from supriya import Server, Synth
from supriya import patterntools
from supriya import synthdefs

from pipermeth001 import synthdefs as project_synthdefs

channel_count = 2


default_pattern = patterntools.Pbind(
    synthdef=synthdefs.default,
    amplitude=patterntools.Pwhite(),
    delta=patterntools.Pwhite(0., 10.),
    duration=patterntools.Pwhite(0.1, 0.5),
    frequency=patterntools.Pwhite(minimum=55, maximum=1760),
    pan=patterntools.Pwhite(),
    )

dust_pattern = patterntools.Pbind(
    synthdef=project_synthdefs.durated_dust,
    delta=patterntools.Pwhite(0.0, 15),
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

server = Server().boot(memory_size=8192 * 16)
for synthdef in (
    project_synthdefs.durated_pitchshift,
    project_synthdefs.durated_allpass,
    project_synthdefs.durated_dust,
    project_synthdefs.durated_freeverb,
    project_synthdefs.durated_freqshift,
    project_synthdefs.durated_mono_chorus,
    project_synthdefs.volume,
    synthdefs.default,
    synthdefs.multiband_compressor,
    ):
    print('Allocating!', synthdef.anonymous_name)
    synthdef.allocate()

multiband_compressor_synth = Synth(
    synthdefs.multiband_compressor,
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
    band_1_pregain=6,
    band_2_pregain=3,
    band_3_pregain=-3,
    band_4_pregain=-3,
    )
volume_synth = Synth(project_synthdefs.volume)
server.root_node.extend([multiband_compressor_synth, volume_synth])

server.recorder.start('~/Desktop/output.aiff', channel_count=channel_count)

volume_synth.controls['level'] = 1.0
for _ in range(6):
    pattern.play()

time.sleep(180)

volume_synth.controls['level'] = 0.0
time.sleep(15 + server.latency)
server.quit()

command = 'lame -b 192 ~/Desktop/output.aiff'
subprocess.call(command, shell=True)
