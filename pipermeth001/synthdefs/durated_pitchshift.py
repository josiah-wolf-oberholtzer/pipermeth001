# -*- encoding: utf-8 -*-
from supriya import DoneAction, SynthDefBuilder
from supriya import ugentools


channel_count = 2

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
    source = ugentools.In.ar(
        bus=builder['out'],
        channel_count=channel_count,
        )
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
        crossfade=window * builder['level'],
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
        source=ugentools.Mix.new(source),
        )

durated_pitchshift = builder.build()
