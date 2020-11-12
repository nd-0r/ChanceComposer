from music21 import *
import random
from enum import Enum
from pathlib import Path

### CONSTANTS ###
# Instrument ranges from this website: 
# https://soundprogramming.net/file-formats/midi-note-ranges-of-orchestral-instruments/

MAX_MIDI = 84
MIN_MIDI = 60
MAX_CHORD_SIZE = 4

instruments = [instrument.Flute, instrument.Clarinet, instrument.Violin, instrument.Violoncello, instrument.Piano]
class range_enum(Enum):
    FLUTE_RANGE = (60, 96)
    CLARINET_RANGE = (50, 94)
    VIOLIN_RANGE = (55, 103)
    CELLO_RANGE = (36, 76)
    PIANO_RANGE = (21, 109)
ranges = list(range_enum)

BARS = 8

# probabilities:
REST_DISTRIBUTION = 0.2
durations = [duration.Duration(d, dots=o) for o in range(0, 3) for d in {1/4, 1/2, 1, 2}]
time_signatures = ['4/4', '2/2', '2/4', '3/4', '3/8', '6/8', '9/8', '12/8']
random.shuffle(time_signatures)

### END CONSTANTS ###

# generate a random measure
def measure_generator(time_sig, inst_range, chords=False):
    bar = stream.Measure()
    bar.timeSignature = meter.TimeSignature(time_sig)
    current_duration = 0
    while (current_duration < bar.timeSignature.barDuration._getQuarterLength()):
        if (random.random() < REST_DISTRIBUTION):
            to_add = note.Rest()
            to_add.duration = durations[random.randint(0, len(durations) - 1)]
            if (current_duration + to_add.duration._getQuarterLength() <= bar.timeSignature.barDuration._getQuarterLength()):
                current_duration += to_add.duration._getQuarterLength()
                bar.append(to_add)
        else:
            if (chords == True):
                chord_size = random.randint(0, MAX_CHORD_SIZE)
                pitches = [pitch.Pitch(random.randint(max(MIN_MIDI, inst_range[0]), min(inst_range[1], MAX_MIDI))) for i in range(0, chord_size)]
                to_add = chord.Chord(pitches)
                to_add.duration = durations[random.randint(0, len(durations) - 1)]
                if (current_duration + to_add.duration._getQuarterLength() <= bar.timeSignature.barDuration._getQuarterLength()):
                    current_duration += to_add.duration._getQuarterLength()
                    bar.append(to_add)
            else:
                to_add = note.Note(random.randint(max(MIN_MIDI, inst_range[0]), min(inst_range[1], MAX_MIDI)))
                to_add.duration = durations[random.randint(0, len(durations) - 1)]
                if (current_duration + to_add.duration._getQuarterLength() <= bar.timeSignature.barDuration._getQuarterLength()):
                    current_duration += to_add.duration._getQuarterLength()
                    bar.append(to_add)
    return bar

# make the parts
def part_generator(part, chords=False):
    for b in range(0, BARS):
        part.append(measure_generator(time_signatures[b % len(time_signatures)], ranges[instruments.index(part.instrument)].value, chords))
        
# make the score
def score_generator():
    parts = []
    for i in range(0, len(instruments)):
        if ('KeyboardInstrument' in instruments[i]().classes):
            upper = stream.Part()
            lower = stream.Part()
            upper.instrument = instruments[i]
            part_generator(upper, True)
            lower.instrument = instruments[i]
            part_generator(lower, False)
            parts.append(layout.StaffGroup([upper, lower], name=instruments[i]().bestName(), abbreviation=instruments[i]().instrumentAbbreviation, symbol='brace'))
        else:
            p = stream.Part()
            p.instrument = instruments[i]
            part_generator(p)
            parts.append(layout.StaffGroup([p], name=instruments[i]().bestName(), abbreviation=instruments[i]().instrumentAbbreviation, symbol='bracket'))
    return parts

if __name__ == '__main__':
    BARS = int(input("How many bars? ") or '8')
    REST_DISTRIBUTION = float(input("Enter the distribution of rests as a decimal between 0 and 1 (default 0.2): ") or '0.2')
    MAX_CHORD_SIZE = int(input("Enter the maximum chord size in notes (default 4): ") or '4')
    out = input("Enter output path (default is current directory): ")


# drive the code
sc = stream.Score(score_generator())
if (out == ""):
    p = Path('./ChanceComposition')
else:
    p = Path(out + "/ChanceComposition")
sc.write('lily.pdf', p)