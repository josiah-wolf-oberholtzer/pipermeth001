# -*- encoding: utf-8 -*-
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
- Is the last non-infinite state properly desparsified?
  - Maybe an artifact from the split&delete changes in Node.set_duration().
- Looks like node settings don't count against sparseness.
"""
import supriya
from pipermeth001 import project_settings, synthdefs
from pipermeth001.materials import (
    libretto_x,
    compressor_settings,
    )


class SessionFactory(supriya.nonrealtimetools.SessionFactory):

    ### GLOBALS ###

    layer_count = 2
    minutes = 3
    release_time = 15

    ### SESSION ###

    def __session__(self):
        self.buffers = []
        session = supriya.Session(
            input_bus_channel_count=self.input_bus_channel_count,
            output_bus_channel_count=self.output_bus_channel_count,
            )
        with session.at(0):
            for say in libretto_x:
                buffer_ = session.add_buffer(channel_count=1, file_path=say)
                self.buffers.append(buffer_)
        for i in range(self.layer_count):
            with session.at(i * 10):
                session.inscribe(
                    self.global_pattern,
                    duration=60 * self.minutes,
                    seed=i,
                    )
        with session.at(0):
            session.add_synth(
                synthdef=synthdefs.multiband_compressor,
                add_action='ADD_TO_TAIL',
                duration=session.duration + self.release_time,
                pregain=-6,
                **compressor_settings
                )
        session.set_rand_seed(offset=0)
        return session

    ### GLOBAL PATTERN ###

    @property
    def global_pattern(self):
        global_pattern = supriya.patterntools.Pgpar(
            [
                self.source_pattern,
                self.effect_pattern,
                ],
            release_time=self.release_time,
            )
        global_pattern = global_pattern.with_bus(
            release_time=self.release_time)
        return global_pattern

    ### SOURCE PATTERNS ###

    @property
    def source_pattern(self):
        source_pattern = supriya.patterntools.Ppar([
            self.warp_buffer_player_pattern,
            ])
        source_pattern = source_pattern.with_group(
            release_time=self.release_time)
        source_pattern = source_pattern.with_effect(
            synthdef=synthdefs.multiband_compressor,
            release_time=self.release_time,
            pregain=12,
            **compressor_settings
            )
        return source_pattern

    @property
    def warp_buffer_player_pattern(self):
        return supriya.patterntools.Pbind(
            synthdef=supriya.patterntools.Prand([
                synthdefs.warp_buffer_player_factory.build(name='warp2', iterations=2),
                synthdefs.warp_buffer_player_factory.build(name='warp4', iterations=4),
                synthdefs.warp_buffer_player_factory.build(name='warp8', iterations=8),
                ], repetitions=None),
            add_action=supriya.AddAction.ADD_TO_HEAD,
            buffer_id=supriya.patterntools.Prand(self.buffers, repetitions=None),
            delta=supriya.patterntools.Pwhite(0, 30),
            duration=0,
            direction=supriya.patterntools.Prand([-1, 1], repetitions=None),
            gain=supriya.patterntools.Pwhite(-12, 0),
            overlaps=supriya.patterntools.Prand([16, 32] * 100, None),
            #overlaps=supriya.patterntools.Prand(
            #    [1, 2, 4, 8, 8, 16, 16, 16, 32, 32, 32] * 4, None,
            #    )
            rate=supriya.patterntools.Pwhite(4, 128),
            transpose=supriya.patterntools.Pwhite(-12.0, 12.0),
            )

    ### EFFECT PATTERNS ###

    @property
    def allpass_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_allpass,
            gain=0,
            )

    @property
    def bpf_sweep_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_bpf_sweep,
            delta=supriya.patterntools.Pwhite(30, 90),
            duration=supriya.patterntools.Pwhite(30, 60),
            gain=3,
            level=supriya.patterntools.Pwhite(0., 0.5),
            start_frequency=supriya.patterntools.Pwhite(10000, 20000),
            stop_frequency=supriya.patterntools.Pwhite(100, 5000),
            )

    @property
    def chorus_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_chorus_factory.build(
                name='chorus8', iterations=8),
            frequency=supriya.patterntools.Pwhite() * 2,
            gain=3,
            )

    @property
    def effect_pattern(self):
        effect_pattern = supriya.patterntools.Ppar([
            self.allpass_pattern,
            self.chorus_pattern,
            self.freeverb_pattern,
            self.freqshift_pattern,
            self.greyout_pattern,
            self.pitchshift_pattern,
            self.bpf_sweep_pattern,
            self.lpf_dip_pattern,
            ])
        effect_pattern = effect_pattern.with_group(
            release_time=self.release_time)
        effect_pattern = effect_pattern.with_effect(
            synthdef=synthdefs.multiband_compressor,
            release_time=self.release_time,
            pregain=6,
            **compressor_settings
            )
        return effect_pattern

    @property
    def freeverb_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_freeverb,
            damping=supriya.patterntools.Pwhite() ** 0.25,
            gain=3,
            room_size=supriya.patterntools.Pwhite() ** 0.25,
            )

    @property
    def freqshift_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            level=supriya.patterntools.Pwhite(0.5, 1.0),
            synthdef=synthdefs.nrt_freqshift,
            sign=supriya.patterntools.Prand([-1, 1]),
            )

    @property
    def fx_pattern(self):
        return supriya.patterntools.Pbind(
            add_action=supriya.AddAction.ADD_TO_TAIL,
            delta=supriya.patterntools.Pwhite(15, 60),
            duration=supriya.patterntools.Pwhite(30, 90),
            level=supriya.patterntools.Pwhite(0.25, 1.0),
            )

    @property
    def greyout_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_greyout,
            gain=0,
            delta=supriya.patterntools.Pwhite(45, 90),
            )

    @property
    def lpf_dip_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_lpf_dip,
            delta=supriya.patterntools.Pwhite(30, 90),
            duration=supriya.patterntools.Pwhite(30, 60),
            gain=3,
            level=supriya.patterntools.Pwhite(0., 0.5),
            frequency=supriya.patterntools.Pwhite(1000, 10000),
            )

    @property
    def pitchshift_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_pitchshift,
            gain=3,
            pitch_dispersion=supriya.patterntools.Pwhite(0., 0.02),
            pitch_shift=supriya.patterntools.Pwhite(-12.0, 12.0),
            time_dispersion=supriya.patterntools.Pwhite(),
            window_size=supriya.patterntools.Pwhite(0.1, 2.0),
            )


session = SessionFactory.from_project_settings(project_settings)
