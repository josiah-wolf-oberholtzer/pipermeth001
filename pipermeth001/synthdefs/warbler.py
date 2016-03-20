from supriya.tools import synthdeftools
from supriya.tools import ugentools


with synthdeftools.SynthDefBuilder(
    bus=0,
    ) as builder:
    trigger = ugentools.Dust.kr(0.5)
    amplitude = ugentools.LFNoise2.kr(0.5)
    frequency = ugentools.TExpRand.kr(
        trigger=trigger,
        minimum=150,
        maximum=1000,
        ).hz_to_midi()
    frequency += ugentools.LFNoise2.kr(0.5) * 2
    frequency = frequency.midi_to_hz()
    source = ugentools.LFSaw.ar(
        frequency=frequency,
        ) * amplitude
    out = ugentools.Out.ar(bus=builder['bus'], source=[source, source])

warbler = builder.build()

if __name__ == '__main__':
    synth = warbler.play()
