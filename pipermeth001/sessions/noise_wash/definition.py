# -*- encoding: utf-8 -*-
import supriya
from pipermeth001 import project_settings, synthdefs
from pipermeth001.materials import compressor_settings as cs


class SessionFactory(supriya.nonrealtimetools.SessionFactory):

    ### GLOBALS ###

    layer_count = 4
    minutes = 3
    release_time = 15
    multiband_compressor = synthdefs.multiband_compressor_factory.build(
        name='multiband_compressor',
        frequencies=(
            40,     # 02
            161,    # 03
            200,    # 04
            404,    # 05
            693,    # 06
            867,    # 07
            1000,   # 08
            2022,   # 09
            3000,   # 10
            3393,   # 11
            4109,   # 12
            5526,   # 13
            6500,   # 14
            7743,   # 15
            12000,  # 16
            ),
        default_slope_above=0.5,
        )
    compressor_settings = dict(
        band_1_threshold=-12,
        band_2_threshold=-12,
        band_3_threshold=-12,
        band_4_threshold=-12,
        band_5_threshold=-12,
        band_6_threshold=-12,
        band_7_threshold=-15,
        band_8_threshold=-18,
        band_9_threshold=-21,
        band_10_threshold=-24,
        band_11_threshold=-27,
        band_12_threshold=-30,
        band_13_threshold=-33,
        band_14_threshold=-36,
        band_15_threshold=-39,
        band_16_threshold=-42,
        band_1_slope_above=0.5,
        band_2_slope_above=0.5,
        band_3_slope_above=0.5,
        band_4_slope_above=0.5,
        band_5_slope_above=0.5,
        band_6_slope_above=0.5,
        band_7_slope_above=0.5,
        band_8_slope_above=0.5,
        band_9_slope_above=0.5,
        band_10_slope_above=0.4,
        band_11_slope_above=0.3,
        band_12_slope_above=0.2,
        band_13_slope_above=0.1,
        band_14_slope_above=0.1,
        band_15_slope_above=0.1,
        band_16_slope_above=0.1,
        )

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
                synthdef=self.multiband_compressor,
                add_action='ADD_TO_TAIL',
                duration=session.duration + self.release_time,
                pregain=-6,
                **self.compressor_settings
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
    def source_pattern(self):
        source_pattern = supriya.patterntools.Ppar([
            self.noise_wash_pattern,
            #self.dust_pattern,
            ])
        source_pattern = source_pattern.with_group(
            release_time=self.release_time)
        source_pattern = source_pattern.with_effect(
            synthdef=self.multiband_compressor,
            release_time=self.release_time,
            pregain=12,
            **self.compressor_settings
            )
        return source_pattern

    @property
    def noise_wash_pattern(self):
        return supriya.patterntools.Pbind(
            synthdef=synthdefs.nrt_noise_wash,
            delta=supriya.patterntools.Pwhite(15, 30),
            duration=supriya.patterntools.Pwhite(15, 60),
            gain=supriya.patterntools.Pwhite(-24, -12),
            )

    ### EFFECT PATTERNS ###

    @property
    def effect_pattern(self):
        effect_pattern = supriya.patterntools.Pgpar(
            [
                [
                    self.lp_flicker_pattern,
                    self.klank_random_pattern,
                    self.allpass_pattern,
                    self.chorus_pattern,
                    self.freeverb_pattern,
                    self.freqshift_pattern,
                    self.pitchshift_pattern,
                    self.lpf_dip_pattern,
                    ],
                ],
            release_time=self.release_time,
            )
        effect_pattern = effect_pattern.with_group(
            release_time=self.release_time)
        effect_pattern = effect_pattern.with_effect(
            synthdef=self.multiband_compressor,
            release_time=self.release_time,
            pregain=3,
            **self.compressor_settings
            )
        return effect_pattern

    @property
    def fx_pattern(self):
        return supriya.patterntools.Pbind(
            add_action=supriya.AddAction.ADD_TO_TAIL,
            delta=supriya.patterntools.Pwhite(15, 30),
            duration=supriya.patterntools.Pwhite(30, 90),
            gain=0,
            level=supriya.patterntools.Pwhite(0.25, 0.75),
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
            gain=3,
            pitch_dispersion=supriya.patterntools.Pwhite(0., 0.02),
            pitch_shift=supriya.patterntools.Pwhite(-12.0, 12.0),
            synthdef=synthdefs.nrt_pitchshift,
            time_dispersion=supriya.patterntools.Pwhite(),
            window_size=supriya.patterntools.Pwhite(0.1, 2.0),
            level=supriya.patterntools.Pwhite(0.75, 1.0),
            )

    @property
    def allpass_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            gain=3,
            synthdef=synthdefs.nrt_allpass,
            level=supriya.patterntools.Pwhite(0.75, 1.0),
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
            gain=3,
            synthdef=supriya.patterntools.Pseq(choruses, None),
            level=supriya.patterntools.Pwhite(0.75, 1.0),
            )

    @property
    def freeverb_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            synthdef=synthdefs.nrt_freeverb,
            damping=supriya.patterntools.Pwhite(0.5, 1),
            gain=0,
            room_size=supriya.patterntools.Pwhite(0.5, 1),
            )

    @property
    def freqshift_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            gain=3,
            level=supriya.patterntools.Pwhite(0.75, 1.0),
            sign=supriya.patterntools.Prand([-1, 1]),
            synthdef=synthdefs.nrt_freqshift,
            )

    @property
    def klank_random_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            decay_scale=supriya.patterntools.Pwhite(1, 20),
            frequency_minimum=20,
            frequency_maximum=supriya.patterntools.Pwhite(5000, 15000),
            frequency_offset=0,
            frequency_scale=1,
            gain=0,
            level=supriya.patterntools.Pwhite(0.125, 0.25),
            synthdef=synthdefs.nrt_klank_random_factory.build(iterations=64),
            )

    @property
    def lp_flicker_pattern(self):
        return supriya.patterntools.Pbindf(
            self.fx_pattern,
            duration=supriya.patterntools.Pwhite(15, 30),
            synthdef=synthdefs.lp_flicker,
            level=1.0,
            )


session = SessionFactory.from_project_settings(project_settings)
