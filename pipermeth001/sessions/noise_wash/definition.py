# -*- encoding: utf-8 -*-
import supriya
from pipermeth001 import project_settings, synthdefs
from pipermeth001.materials import compressor_settings


class SessionFactory(supriya.nonrealtimetools.SessionFactory):

    ### GLOBALS ###

    layer_count = 4
    minutes = 5
    release_time = 15

    ### SESSION ###

    def __session__(self):
        session = supriya.Session(
            input_bus_channel_count=self.input_bus_channel_count,
            output_bus_channel_count=self.output_bus_channel_count,
            )
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
                pregain=0,
                **compressor_settings
                )
            session.set_rand_seed()
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
    def noise_wash_pattern(self):
        return supriya.patterntools.Pbind(
            synthdef=synthdefs.nrt_noise_wash,
            delta=supriya.patterntools.Pwhite(15, 30),
            duration=supriya.patterntools.Pwhite(15, 60),
            gain=supriya.patterntools.Pwhite(-24, -12),
            )

    @property
    def pitchshift_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            gain=6,
            pitch_dispersion=supriya.patterntools.Pwhite(0., 0.02),
            pitch_shift=supriya.patterntools.Pwhite(-12.0, 12.0),
            synthdef=synthdefs.nrt_pitchshift,
            time_dispersion=supriya.patterntools.Pwhite(),
            window_size=supriya.patterntools.Pwhite(0.1, 2.0),
            )

    @property
    def source_pattern(self):
        source_pattern = supriya.patterntools.Ppar([self.noise_wash_pattern])
        source_pattern = source_pattern.with_group(
            release_time=self.release_time)
        source_pattern = source_pattern.with_effect(
            synthdef=synthdefs.multiband_compressor,
            release_time=self.release_time,
            pregain=12,
            **compressor_settings
            )
        return source_pattern

    ### EFFECT PATTERNS ###

    @property
    def allpass_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_allpass,
            gain=3,
            )

    @property
    def chorus_pattern(self):
        choruses = [
            synthdefs.nrt_chorus_factory.build(name='chorus2', iterations=2),
            synthdefs.nrt_chorus_factory.build(name='chorus4', iterations=4),
            synthdefs.nrt_chorus_factory.build(name='chorus8', iterations=8),
            ]
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            level=1.0,
            synthdef=supriya.patterntools.Pseq(choruses, None),
            gain=3,
            )

    @property
    def effect_pattern(self):
        effect_pattern = supriya.patterntools.Pgpar(
            [
                [
                    self.allpass_pattern,
                    self.chorus_pattern,
                    self.freeverb_pattern,
                    self.freqshift_pattern,
                    self.pitchshift_pattern,
                    self.allpass_pattern,
                    ],
                ],
            release_time=self.release_time,
            )
        effect_pattern = effect_pattern.with_group(
            release_time=self.release_time)
        effect_pattern = effect_pattern.with_effect(
            synthdef=synthdefs.multiband_compressor,
            release_time=self.release_time,
            pregain=0,
            **compressor_settings
            )
        return effect_pattern

    @property
    def freeverb_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_freeverb,
            damping=supriya.patterntools.Pwhite(),
            gain=3,
            room_size=supriya.patterntools.Pwhite(),
            )

    @property
    def freqshift_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            gain=6,
            level=supriya.patterntools.Pwhite(0.5, 1.0),
            sign=supriya.patterntools.Prand([-1, 1]),
            synthdef=synthdefs.nrt_freqshift,
            )

    @property
    def fx_pattern(self):
        return supriya.patterntools.Pbind(
            add_action=supriya.AddAction.ADD_TO_TAIL,
            delta=supriya.patterntools.Pwhite(15, 30),
            duration=supriya.patterntools.Pwhite(30, 90),
            level=supriya.patterntools.Pwhite(0.25, 1.0),
            )


session = SessionFactory.from_project_settings(project_settings)
