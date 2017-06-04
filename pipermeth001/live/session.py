#! /usr/bin/env python
import supriya
import time
from supriya import SynthDefBuilder, bind, ugentools
from supriya.tools.miditools import NanoKontrol2
from supriya.tools.synthdeftools import Parameter
from pipermeth001 import synthdefs


def build_grain_synthdef():
    channel_count = 2
    builder = SynthDefBuilder(
        in_=Parameter(value=0, parameter_rate='SCALAR'),
        out=Parameter(value=0, parameter_rate='SCALAR'),
        mix=Parameter(value=0.0, lag=0.25),
        feedback_gain=Parameter(value=-24, lag=0.25),
        density=Parameter(value=1.0),
        duration=Parameter(value=0.01),
        )
    with builder:
        source = ugentools.In.ar(
            bus=builder['in_'],
            channel_count=channel_count,
            )
        source += ugentools.LocalIn.ar(channel_count=channel_count)
        # core algorithm
        buffer_duration = 10
        local_buf = ugentools.LocalBuf(
            channel_count=1,
            frame_count=ugentools.SampleRate.ir() * buffer_duration,
            )
        ugentools.RecordBuf.ar(
            buffer_id=local_buf,
            source=ugentools.Mix.new(source) / 2,
            )
        trigger = ugentools.Dust.kr(density=builder['density'])
        source = ugentools.GrainBuf.ar(
            buffer_id=local_buf,
            channel_count=2,
            trigger=trigger,
            duration=builder['duration'],
            rate=1,
            position=ugentools.WhiteNoise.kr(),
            pan=ugentools.WhiteNoise.kr(),
            )
        source = ugentools.LeakDC.ar(source=source)
        source = source.tanh()
        # bus output
        ugentools.XOut.ar(
            bus=builder['out'],
            crossfade=builder['mix'],
            source=source,
            )
        # feedback algorithm
        feedback = source
        feedback *= -builder['feedback_gain'].db_to_amplitude()
        feedback = ugentools.Limiter.ar(source=feedback, duration=0.01)
        feedback = ugentools.HPF.ar(frequency=150, source=feedback)
        feedback = ugentools.LPF.ar(frequency=5000, source=feedback)
        feedback = ugentools.Rotate2.ar(
            x=feedback[0],
            y=feedback[1],
            position=ugentools.LFNoise2.kr(frequency=0.1)
            )
        ugentools.LocalOut.ar(source=-feedback)
    synthdef = builder.build(name='jams_grain')
    return synthdef


def build_pitch_shift_synthdef():
    channel_count = 2
    builder = SynthDefBuilder(
        in_=Parameter(value=0, parameter_rate='SCALAR'),
        out=Parameter(value=0, parameter_rate='SCALAR'),
        mix=Parameter(value=0.0, lag=0.25),
        feedback_gain=Parameter(value=-24, lag=0.25),
        transposition=Parameter(value=0.0, lag=0.25),
        fuzz=Parameter(value=0.0, lag=0.25),
        )
    with builder:
        source = ugentools.In.ar(
            bus=builder['in_'],
            channel_count=channel_count,
            )
        source += ugentools.LocalIn.ar(channel_count=channel_count)
        # core algorithm
        window_size = 0.5
        source = ugentools.PitchShift.ar(
            source=source,
            window_size=window_size,
            pitch_ratio=builder['transposition'].semitones_to_ratio(),
            time_dispersion=builder['fuzz'].squared() * (window_size / 2),
            pitch_dispersion=builder['fuzz'].squared(),
            )
        source = ugentools.LeakDC.ar(source=source)
        # bus output
        ugentools.XOut.ar(
            bus=builder['out'],
            crossfade=builder['mix'],
            source=source,
            )
        # feedback algorithm
        source += ugentools.LocalIn.ar(channel_count=channel_count)
        feedback = source
        feedback *= -builder['feedback_gain'].db_to_amplitude()
        feedback = ugentools.Limiter.ar(source=feedback, duration=0.01)
        feedback = ugentools.HPF.ar(frequency=150, source=feedback)
        feedback = ugentools.LPF.ar(frequency=10000, source=feedback)
        feedback = ugentools.Rotate2.ar(
            x=feedback[0],
            y=feedback[1],
            position=ugentools.LFNoise2.kr(frequency=0.1)
            )
        ugentools.LocalOut.ar(source=-feedback)
    synthdef = builder.build(name='jams_pitch_shift')
    return synthdef


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
        frequency_shift=Parameter(value=0.0, lag=0.1),
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
        feedback = ugentools.HPF.ar(frequency=100, source=feedback)
        feedback = ugentools.LPF.ar(frequency=15000, source=feedback)
        feedback = ugentools.Rotate2.ar(
            x=feedback[0],
            y=feedback[1],
            position=ugentools.LFNoise2.kr(frequency=0.1)
            )
        ugentools.LocalOut.ar(source=-feedback)
    synthdef = builder.build(name='jams_freeverb')
    return synthdef


def setup_server():
    server = supriya.Server()
    server.debug_osc = True
    server.boot(
        block_size=128,
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
    grain_synthdef = build_grain_synthdef()
    grain_synth = supriya.Synth(
        synthdef=grain_synthdef,
        name='grain_synth',
        )
    pitch_shift_synthdef = build_pitch_shift_synthdef()
    pitch_shift_synth = supriya.Synth(
        synthdef=pitch_shift_synthdef,
        name='pitch_shift_synth',
        )
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
        grain_synth,
        pitch_shift_synth,
        delay_synth,
        freeverb_synth,
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

    # grain
    synth = server['grain_synth']
    bind(nano['knob_1'], synth['mix'], target_range=[0.0, 1.0])
    bind(nano['knob_2'], synth['feedback_gain'], target_range=[-96.0, 24.0])
    bind(nano['fader_1'], synth['density'],
        target_range=[0.1, 100.0], exponent=3.0)
    bind(nano['fader_2'], synth['duration'],
        target_range=[0.001, 1.0], exponent=3.0)

    # pitchshift
    synth = server['pitch_shift_synth']
    bind(nano['knob_3'], synth['mix'], target_range=[0.0, 1.0])
    bind(nano['knob_4'], synth['feedback_gain'], target_range=[-96.0, 24.0])
    bind(nano['fader_3'], synth['fuzz'], target_range=[0.0, 1.0])
    bind(nano['fader_4'], synth['transposition'], target_range=[-12.0, 12.0])

    # delay
    synth = server['delay_synth']
    bind(nano['knob_5'], synth['mix'], target_range=[0.0, 1.0])
    bind(nano['knob_6'], synth['feedback_gain'], target_range=[-96.0, 24.0])
    bind(nano['fader_5'], synth['depth'],
        target_range=[0.001, 1.0], exponent=2.0)
    bind(nano['fader_6'], synth['frequency'],
        target_range=[0.001, 10.0], exponent=3.0)

    # freeverb
    synth = server['freeverb_synth']
    bind(nano['knob_7'], synth['mix'], target_range=[0.0, 1.0])
    bind(nano['knob_8'], synth['feedback_gain'], target_range=[-96.0, 24.0])
    bind(nano['fader_7'], synth['frequency_shift'],
        source_range=[0, 128], target_range=[-200, 0], exponent=0.1)
    bind(nano['fader_8'], synth['damping'], target_range=[0.0, 1.0])
    bind(nano['fader_8'], synth['room_size'], target_range=[0.0, 1.0])

    return nano


if __name__ == '__main__':
    server = setup_server()
    setup_nodes(server)
    nano = setup_bindings(server)
    time.sleep(2)
    nano.open_port()
