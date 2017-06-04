#! /usr/bin/env python
import supriya
import time
from supriya import SynthDefBuilder, bind, ugentools
from supriya.tools.miditools import NanoKontrol2
from supriya.tools.synthdeftools import Parameter
from pipermeth001 import synthdefs


def build_delay_synthdef():
    channel_count = 2
    builder = SynthDefBuilder(
        in_=Parameter(value=0, parameter_rate='SCALAR'),
        out=Parameter(value=0, parameter_rate='SCALAR'),
        mix=Parameter(value=0.0, lag=0.25),
        feedback_gain=Parameter(value=-24, lag=0.25),
        depth=Parameter(value=1.0, lag=0.1),
        frequency=Parameter(value=1.0, lag=0.1),
        )
    with builder:
        source = ugentools.In.ar(
            bus=builder['in_'],
            channel_count=channel_count,
            )
        source += ugentools.LocalIn.ar(channel_count=channel_count)
        # core algorithm
        for _ in range(3):
            frequency = [builder['frequency']] * channel_count
            decay_time = ugentools.LFDNoise3.kr(
                frequency=frequency,
                ).squared() * builder['depth']
            delay_time = ugentools.LFDNoise3.kr(
                frequency=frequency,
                ).squared() * builder['depth']
            source = ugentools.AllpassC.ar(
                source=source,
                decay_time=decay_time,
                delay_time=delay_time,
                maximum_delay_time=1.0,
                )
        source = ugentools.LeakDC.ar(source=source)
        # bus output
        ugentools.XOut.ar(
            bus=builder['out'],
            crossfade=builder['mix'],
            source=source,
            )
        # feedback algorithm
        feedback = source
        feedback *= builder['feedback_gain'].db_to_amplitude()
        feedback = ugentools.Limiter.ar(source=feedback, duration=0.01)
        feedback = ugentools.HPF.ar(frequency=150, source=feedback)
        feedback = ugentools.LPF.ar(frequency=5000, source=feedback)
        feedback = ugentools.Rotate2.ar(
            x=feedback[0],
            y=feedback[1],
            position=ugentools.LFNoise2.kr(frequency=0.1)
            )
        ugentools.LocalOut.ar(source=-feedback)
    synthdef = builder.build(name='jams_delay')
    return synthdef


def build_freeverb_synthdef():
    channel_count = 2
    builder = SynthDefBuilder(
        in_=Parameter(value=0, parameter_rate='SCALAR'),
        out=Parameter(value=0, parameter_rate='SCALAR'),
        mix=Parameter(value=0.0, lag=0.25),
        feedback_gain=Parameter(value=-96, lag=0.25),
        damping=Parameter(value=1.0, lag=0.25),
        room_size=Parameter(value=1.0, lag=0.25),
        frequency_shift=Parameter(value=0.0, lag=0.25),
        )
    with builder:
        source = ugentools.In.ar(
            bus=builder['in_'],
            channel_count=channel_count,
            )
        source += ugentools.LocalIn.ar(channel_count=channel_count)
        # core algorithm
        source = ugentools.FreeVerb.ar(
            source=source,
            mix=1.0,
            room_size=builder['room_size'],
            damping=builder['damping'],
            )
        source = ugentools.LeakDC.ar(source=source)
        # bus output
        ugentools.XOut.ar(
            bus=builder['out'],
            crossfade=builder['mix'],
            source=source,
            )
        # feedback algorithm
        feedback = ugentools.FreqShift.ar(
            source=source,
            frequency=builder['frequency_shift'],
            )
        feedback *= builder['feedback_gain'].db_to_amplitude()
        feedback = ugentools.Limiter.ar(source=feedback, duration=0.01)
        feedback = ugentools.HPF.ar(frequency=150, source=feedback)
        feedback = ugentools.LPF.ar(frequency=5000, source=feedback)
        ugentools.LocalOut.ar(source=-feedback)
    synthdef = builder.build(name='jams_freeverb')
    return synthdef


def setup_server():
    server = supriya.Server()
    server.debug_osc = True
    server.boot(
        block_size=64,
        memory_size=8192 * 32,
        )
    return server


def setup_nodes(server):
    microphone_synth = supriya.Synth(
        synthdef=supriya.synthdefs.system_link_audio_2,
        in_=int(server.audio_input_bus_group),
        out=int(server.audio_output_bus_group),
        name='mic_input',
        )
    source_group = supriya.Group(name='source_group')
    source_compressor = supriya.Synth(
        synthdef=synthdefs.multiband_compressor,
        name='source_compressor',)
    effect_group = supriya.Group(name='effect_group')
    delay_synthdef = build_delay_synthdef()
    delay_synth = supriya.Synth(
        synthdef=delay_synthdef,
        name='delay_synth',
        )
    freeverb_synthdef = build_freeverb_synthdef()
    freeverb_synth = supriya.Synth(
        synthdef=freeverb_synthdef,
        name='freeverb_synth',
        )
    effect_group.extend([
        delay_synth,
        freeverb_synth,
        #grain_synth,
        #harmonizer_synth,
        ])
    effect_compressor = supriya.Synth(
        synthdef=synthdefs.multiband_compressor,
        name='effect_compressor',
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
    synth = server['freeverb_synth']
    bind(nano['knob_1'], synth['mix'], target_range=[0.0, 1.0])
    bind(nano['knob_2'], synth['feedback_gain'], target_range=[-96.0, 24.0])
    bind(nano['fader_1'], synth['frequency_shift'],
        source_range=[0, 128], target_range=[-200, 200])
    bind(nano['fader_2'], synth['damping'], target_range=[0.0, 1.0])
    bind(nano['fader_2'], synth['room_size'], target_range=[0.0, 1.0])

    # delay
    synth = server['delay_synth']
    bind(nano['knob_3'], synth['mix'], target_range=[0.0, 1.0])
    bind(nano['knob_4'], synth['feedback_gain'], target_range=[-96.0, 24.0])
    bind(nano['fader_3'], synth['depth'],
        target_range=[0.001, 1.0], exponent=2.0)
    bind(nano['fader_4'], synth['frequency'],
        target_range=[0.001, 10.0], exponent=3.0)

    return nano


if __name__ == '__main__':
    server = setup_server()
    setup_nodes(server)
    nano = setup_bindings(server)
    time.sleep(5)
    nano.open_port()
