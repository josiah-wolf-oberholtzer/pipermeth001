#! /usr/bin/env python
import supriya
from supriya import SynthDefBuilder, bind, ugentools
from supriya.tools.miditools import NanoKontrol2
from supriya.tools.synthdeftools import Parameter
from pipermeth001 import synthdefs


def build_freeverb_synthdef():
    builder = SynthDefBuilder(
        in_=Parameter(value=0, parameter_rate='SCALAR'),
        out=Parameter(value=0, parameter_rate='SCALAR'),
        mix=Parameter(value=0.75, lag=0.25),
        damping=Parameter(value=0.9, lag=0.25),
        room_size=Parameter(value=0.9, lag=0.25),
        feedback_gain=Parameter(value=-24, lag=0.25),
        frequency_shift=Parameter(value=-200, lag=0.25),
        )
    with builder:
        source = ugentools.In.ar(bus=builder['in_'], channel_count=2)
        source += ugentools.LocalIn.ar(channel_count=2)
        source = ugentools.FreeVerb.ar(
            source=source,
            mix=1.0,
            room_size=builder['room_size'],
            damping=builder['damping'],
            )
        source = ugentools.FreqShift.ar(
            source=source,
            frequency=builder['frequency_shift'],
            )
        source = ugentools.LeakDC.ar(source=source)
        ugentools.XOut.ar(
            bus=builder['out'],
            crossfade=builder['mix'],
            source=source,
            )
        feedback_source = source * builder['feedback_gain'].db_to_amplitude()
        feedback_source = ugentools.Limiter.ar(
            source=feedback_source,
            duration=0.01,
            )
        feedback_source = ugentools.HPF.ar(
            frequency=150,
            source=feedback_source,
            )
        feedback_source = ugentools.LPF.ar(
            frequency=5000,
            source=feedback_source,
            )
        ugentools.LocalOut.ar(source=-feedback_source)
    synthdef = builder.build(name='jams-freeverb')
    return synthdef


def setup_server():
    server = supriya.Server()
    server.debug_osc = True
    server.boot(
        block_size=64,
        memory_size=8192 * 16,
        )
    return server


def setup_nodes(server):
    microphone_synth = supriya.Synth(
        synthdef=supriya.synthdefs.system_link_audio_2,
        in_=int(server.audio_input_bus_group),
        out=int(server.audio_output_bus_group),
        name='mic-input',
        )
    source_group = supriya.Group(name='source-group')
    source_compressor = supriya.Synth(
        synthdef=synthdefs.multiband_compressor,
        name='source-compressor',)
    effect_group = supriya.Group(name='effect-group')
#    grain_synth = supriya.Synth(
#        synthdef=synthdefs.jam_grain_synth,
#        )
#    delay_synth = supriya.Synth(
#        synthdef=synthdefs.jam_delay_synth,
#        )
#    harmonizer_chorus_synth = supriya.Synth(
#        synthdef=synthdefs.jam_harmonizer_chorus,
#        )
    freeverb_synthdef = build_freeverb_synthdef()
    freeverb_synth = supriya.Synth(
        synthdef=freeverb_synthdef,
        name='freeverb-synth',
        )
    effect_group.extend([
        #grain_synth,
        #delay_synth,
        #harmonizer_synth,
        freeverb_synth,
        ])
    effect_compressor = supriya.Synth(
        synthdef=synthdefs.multiband_compressor,
        name='effect-compressor',
        )
    server.default_group.extend([
        microphone_synth,
        source_group,
        source_compressor,
        effect_group,
        effect_compressor,
        ])


def setup_bindings(server):
    nano = NanoKontrol2()

    # freeverb
    synth = server['freeverb-synth']
    bind(nano['knob_1'], synth['mix'], target_range=[0., 1.])
    bind(nano['knob_2'], synth['feedback_gain'], target_range=[-64, 12])
    bind(nano['fader_1'], synth['frequency_shift'],
        source_range=[0, 128], target_range=[-200, 200])
    bind(nano['fader_2'], synth['damping'], target_range=[0, 1])
    bind(nano['fader_2'], synth['room_size'], target_range=[0, 1])

    return nano


if __name__ == '__main__':
    server = setup_server()
    setup_nodes(server)
    nano = setup_bindings(server)
