from supriya import (
    Session,
    patterntools,
    synthdefs,
)


pseed = Session(0, 2)

pattern = patterntools.Pbind(
    synthdef=synthdefs.default,
    amplitude=1.0,
    delta=1.0,
    duration=0.5,
    frequency=patterntools.Pwhite(minimum=55, maximum=1760),
    pan=patterntools.Pwhite(-1.0, 1.0),
    )
pattern = patterntools.Pseed(pattern, seed=0)

with pseed.at(0):
    pseed.inscribe(pattern, duration=10)
