# -*- encoding: utf-8 -*-
import subprocess
import time
from supriya import DoneAction, Server, SynthDefBuilder, Synth
from supriya import patterntools
from supriya import synthdefs
from supriya import synthdeftools
from supriya import ugentools

channel_count = 2

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    source = ugentools.Dust2.ar(
        density=ugentools.ExpRand.ir(1, 50),
        ) * window
    ugentools.Out.ar(
        bus=builder['out'],
        source=[source, source],
        )
dust_synthdef = builder.build()

with SynthDefBuilder(
    level=synthdeftools.Parameter(value=0.0, lag=15),
    out=0,
    ) as builder:
    source = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        ) * builder['level'].s_curve()
    ugentools.ReplaceOut.ar(
        bus=builder['out'],
        source=source,
        )
volume_synthdef = builder.build()

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    in_ = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source = in_ * window
    source = source[0] + source[1]
    source += ugentools.LocalIn.ar(channel_count=1)
    allpasses = []
    allpass_count = 16
    maximum_delay_time = 0.05
    for _ in range(allpass_count):
        allpass = ugentools.AllpassC.ar(
            decay_time=ugentools.LFDNoise3.kr(
                frequency=ugentools.ExpRand.ir(0.1, 5),
                ).scale(-1, 1, 0., 0.1),
            delay_time=ugentools.LFDNoise3.kr(
                frequency=ugentools.ExpRand.ir(0.1, 5),
                ).scale(-1, 1, 0., maximum_delay_time),
            maximum_delay_time=maximum_delay_time,
            source=source,
            )
        allpasses.append(allpass)
    source = ugentools.Mix.new(allpasses) / allpass_count
    source = ugentools.LeakDC.ar(source=source)
    source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window,
        source=[source, source],
        )
    ugentools.LocalOut.ar(
        source=source * -0.9 * abs(ugentools.LFDNoise1.kr(frequency=0.1))
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(tuple(in_) + tuple(source)),
        )
mono_chorus_synthdef = builder.build()

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    damping=0.5,
    room_size=0.5,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    in_ = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source = in_ * window
    source = ugentools.FreeVerb.ar(
        source=source,
        damping=builder['damping'],
        room_size=builder['room_size'],
        mix=1.0,
        )
    source = ugentools.LeakDC.ar(source=source)
    source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window,
        source=source,
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(tuple(in_) + tuple(source)),
        )
freeverb_synthdef = builder.build()

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    in_ = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source = in_ * window
    source = ugentools.FreqShift.ar(
        source=source,
        frequency=ugentools.LFDNoise3.kr(frequency=0.1) * 2000,
        phase=ugentools.LFNoise2.kr(frequency=0.1),
        )
    source = ugentools.LeakDC.ar(source=source)
    source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window,
        source=source,
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(tuple(in_) + tuple(source)),
        )
freqshift_synthdef = builder.build()

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    pitch_shift=0.,
    pitch_dispersion=0,
    time_dispersion=0,
    window_size=0.5,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    in_ = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source = in_ * window
    source += ugentools.LocalIn.ar(channel_count=channel_count)
    source = ugentools.PitchShift.ar(
        source=source,
        pitch_dispersion=builder['pitch_dispersion'],
        pitch_ratio=builder['pitch_shift'].semitones_to_ratio(),
        time_dispersion=builder['time_dispersion'] * builder['window_size'],
        window_size=builder['window_size'],
        )
    source = ugentools.LeakDC.ar(source=source)
    source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window,
        source=source,
        )
    ugentools.LocalOut.ar(
        source=[
            source[1] * -0.9 * ugentools.LFDNoise1.kr(frequency=0.1),
            source[0] * -0.9 * ugentools.LFDNoise1.kr(frequency=0.1),
            ],
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(tuple(in_) + tuple(source)),
        )
pitchshift_synthdef = builder.build()

with SynthDefBuilder(
    duration=1.0,
    level=1.0,
    out=0,
    ) as builder:
    window = ugentools.Line.kr(
        done_action=2,
        duration=builder['duration'],
        ).hanning_window()
    in_ = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
    source = in_ * window
    source += ugentools.LocalIn.ar(channel_count=channel_count)
    allpasses = []
    maximum_delay = ugentools.Rand.ir(0.1, 1)
    for output in source:
        for _ in range(3):
            output = ugentools.AllpassC.ar(
                decay_time=ugentools.LFDNoise3.kr(
                    frequency=ugentools.ExpRand.ir(0.01, 1),
                    ).scale(-1, 1, 0.001, 1),
                delay_time=ugentools.LFDNoise3.kr(
                    frequency=ugentools.ExpRand.ir(0.01, 1),
                    ).scale(-1, 1, 0.001, 1) * maximum_delay,
                maximum_delay_time=maximum_delay,
                source=output,
                )
        allpasses.append(output)
    source = synthdeftools.UGenArray(allpasses)
    source = ugentools.LeakDC.ar(source=source)
    source = (source * 1.5).tanh()
    source = ugentools.Limiter.ar(source=source)
    ugentools.XOut.ar(
        bus=builder['out'],
        crossfade=window,
        source=source,
        )
    ugentools.LocalOut.ar(
        source=source * -0.9 * ugentools.LFDNoise1.kr(frequency=0.1)
        )
    ugentools.DetectSilence.kr(
        done_action=DoneAction.FREE_SYNTH,
        source=ugentools.Mix.new(tuple(in_) + tuple(source)),
        )
allpass_synthdef = builder.build()

default_pattern = patterntools.Pbind(
    synthdef=synthdefs.default,
    amplitude=patterntools.Pwhite(),
    delta=patterntools.Pwhite(0., 10.),
    duration=patterntools.Pwhite(0.1, 0.5),
    frequency=patterntools.Pwhite(minimum=55, maximum=1760),
    pan=patterntools.Pwhite(),
    )

dust_pattern = patterntools.Pbind(
    synthdef=dust_synthdef,
    delta=patterntools.Pwhite(0.0, 15),
    duration=patterntools.Pwhite(0.05, 5),
    level=patterntools.Pwhite(),
    )

pitchshift_pattern = patterntools.Pbind(
    synthdef=pitchshift_synthdef,
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 10),
    level=patterntools.Pwhite(),
    pitch_dispersion=patterntools.Pwhite(0., 0.1),
    pitch_shift=patterntools.Pwhite(-12.0, 12.0),
    time_dispersion=patterntools.Pwhite(),
    window_size=patterntools.Pwhite(0.1, 2.0),
    )

freeverb_pattern = patterntools.Pbind(
    synthdef=freeverb_synthdef,
    damping=patterntools.Pwhite(),
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 20),
    level=patterntools.Pwhite(),
    room_size=patterntools.Pwhite(),
    )

allpass_pattern = patterntools.Pbind(
    synthdef=allpass_synthdef,
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 10),
    level=patterntools.Pwhite(),
    )

mono_chorus_pattern = patterntools.Pbind(
    synthdef=mono_chorus_synthdef,
    delta=patterntools.Pwhite(0.5, 10),
    duration=patterntools.Pwhite(0.5, 20),
    level=patterntools.Pwhite(),
    )

freqshift_pattern = patterntools.Pbind(
    synthdef=freqshift_synthdef,
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
    allpass_synthdef,
    freeverb_synthdef,
    freqshift_synthdef,
    mono_chorus_synthdef,
    pitchshift_synthdef,
    synthdefs.default,
    synthdefs.multiband_compressor,
    volume_synthdef,
    dust_synthdef,
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
    #band_1_slope_below=0.5,
    #band_2_slope_below=0.5,
    #band_3_slope_below=0.5,
    #band_4_slope_below=0.5,
    )
volume_synth = Synth(volume_synthdef)
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
