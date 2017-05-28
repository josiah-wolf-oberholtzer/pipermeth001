# -*- encoding: utf-8 -*-
import supriya


material = []

voices = [
    'Daniel',
    'Fiona',
    'Victoria',
    'Tessa',
    'Karen',
    'Thomas',
    ]

texts = [
    'Be true.',
    "Don't leave me.",
    'Talk to me.',
    'Feed me.',
    'Heal me.',
    'Dance with me.',
    'Teach me.',
    'Hold me.',
    'Touch me.',
    'Love me.',
    'Let me help you.',
    "Don't hurt me.",
    'Show me a path.',
    'Give me light.',
    'Release me.',
    ]

for voice in voices:
    for text in texts:
        material.append(supriya.Say(text, voice=voice))

material = tuple(material)
