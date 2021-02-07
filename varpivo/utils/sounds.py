from collections import namedtuple

from rtttl import parse_rtttl


def get_tone(note='C', octave=5):
    TONES = {
        'C': 261.63,
        'C#': 277.18,
        'D': 293.66,
        'D#': 311.13,
        'E': 329.63,
        'F': 349.23,
        'F#': 369.99,
        'G': 392,
        'G#': 415.3,
        'A': 440,
        'A#': 466.16,
        'B': 493.88
    }
    freq = TONES[note]
    freq = freq * (2 ** (octave - 5))
    return freq


def from_rtttl(rtttl_string):
    notes = parse_rtttl(rtttl_string)
    return [Note(**note) for note in notes['notes']]


Note = namedtuple('Note', 'frequency duration')


class Songs:
    PIVO = [
        Note(get_tone('E'), 200),
        Note(get_tone(), 500),
        Note(get_tone('E'), 200),
        Note(get_tone(), 500),
        Note(get_tone('E'), 200),
        Note(get_tone(), 500),
        Note(get_tone('E'), 200),
        Note(get_tone(), 500),
        Note(get_tone('E'), 200),
        Note(get_tone(), 500),
        Note(get_tone('G'), 400),
        Note(get_tone('G'), 200),
        Note(get_tone('G'), 600),
        Note(get_tone('G'), 200),
        Note(get_tone('G'), 200),
        Note(get_tone('A'), 400),
        Note(get_tone('G'), 200),
        Note(get_tone('E'), 600),
        Note(get_tone('D'), 400),
    ]

    WALK_OF_LIFE = from_rtttl(
        "WalkOfLi:d=4,o=5,b=140:g#6,16p,8g#6,2p,16f#.6,16g#.6,8b.6,16g#.6,16f#.6,8p,e6,16p,8e6,1p,16f#.6,16g#.6,b6,16p,8b6,2p,16f#.6,16g#.6,8b.6,16g#6,8f#6,8p,e6,16p,8e6,2p,16f#.6,16g#.6,8b.6,16g#.6,16f#.6,16e.6,b6,16p,8b6,2p,16f#.6,16g#.6,8b.6,16g#.6,16f#.6,8p,e6,16p,8e6,1p,16f#.6,16g#.6,b6,16p,8b6,2p,16f#.6,16g#.6,8b.6,16g#.6,16f#.6,8p,e6,16p,8e6,2p,16f#.6,16g#.6,8b.6,16g#.6,16f#.6,16e.6,32p,8b6,16p,b6")
    FRIENDS = from_rtttl(
        """Friends:d=8,o=5,b=100:16d,g,a,c6,b,a,g.,16g,d,g,a,2a,p,16p,16d,g,a,c.6,16b,16a,g.,16c6,b,a,g,2d6,p,16p,16c6,c6,c6,c6,c6,c6,c.6,16c6,b,2b,p,16a,16a,16b,16c6,c6,c6,c6,c.6,16b,a.,16g,g.,16d,16g,16a,b,4a,4g,p""")
    SEVEN_NATION_ARMY = from_rtttl(
        "7NationA:d=4,o=6,b=125:e.,8e,8g,16p,8e,32p,8d,c.,16d,16c,b5,p,32p,e.,8e,8g,16p,8e,32p,8d,c.,16d,16c,b5,p,32p,e.,8e,8g,16p,8e,32p,8d,c.,16d,16c,b5,p,32p,e.,8e,8g,16p,8e,32p,8d,c,16d,b5")
    FINAL_COUNTDOWN = from_rtttl(
        "The Final Countdown:d=4,o=5,b=125:p,8p,16b,16a,b,e,p,8p,16c6,16b,8c6,8b,a,p,8p,16c6,16b,c6,e,p,8p,16a,16g,8a,8g,8f#,8a,g.,16f#,16g,a.,16g,16a,8b,8a,8g,8f#,e,c6,2b.,16b,16c6,16b,16a,1b")
    TAKE_ON_ME = from_rtttl(
        "TakeOnMe:d=16,o=5,b=100:8p,a#,a#,a#,8f#,8d#,8g#,8g#,g#,c6,c6,c#6,d#6,c#6,c#6,c#6,8g#,8f#,8a#,8a#,a#,g#,g#,a#,g#,a#,a#,a#,8f#,8d#,8g#,8g#,g#,c6,c6,c#6,d#6,c#6,c#6,c#6,8g#,8f#,8a#,8a#")
    LIVIN_LA_VIDA_LOCA = from_rtttl(
        "LivinLaV:d=16,o=5,b=400:8a,4p,8p,2a,8p,p,4f,4g,8a#,4p,8p,8a#,4p,8p,2a,2p,4p,8a,4p,8p,2a,8p,p,4f,4e,4g,4p,4g,4p,2f,2p,4p,8a,4p,8p,2a,4p,4f,4g,8a#,4p,8p,8a#,4p,8p,2a,2p,4p,8a,4p,8p,2a,4p,4f,4e,8g,4p,8p,4g,4p,2f,4p")
    LUFTBALLONS = from_rtttl(
        "99LuftBa:d=4,o=6,b=160:32p,d,8e,c.,e,d,8c,a5.,8p,8a5,8f,f,f,f.,8f,e,d,c.,d,8e,c,e.,d,8c,a5.,8p,8a5,f,f,f,f,8f,e,d.,8c,8d,e,c,e.,d,8c,a5.,8p,8a5,c,8a5,c,f,f,e,d.,8c,d,e,c,e.,d,8c,a5.,8p,8f,f,8f,f,f,f,e,2d")
