from music21 import *
import random
from enum import Enum
from pathlib import Path

### CONSTANTS ###
# Instrument ranges from this website: 
# https://soundprogramming.net/file-formats/midi-note-ranges-of-orchestral-instruments/

MAX_MIDI = 84
MIN_MIDI = 60

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


def measure_generator(time_sig, inst_range):
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
            to_add = note.Note(random.randint(max(MIN_MIDI, inst_range[0]), min(inst_range[1], MAX_MIDI)))
            to_add.duration = durations[random.randint(0, len(durations) - 1)]
            if (current_duration + to_add.duration._getQuarterLength() <= bar.timeSignature.barDuration._getQuarterLength()):
                current_duration += to_add.duration._getQuarterLength()
                bar.append(to_add)
    return bar
        
# make the parts
parts = [stream.Part() for i in range(0, len(instruments))]
for i,part in enumerate(parts):
    part.instrument = instruments[i]
    for b in range(0, BARS):
        part.append(measure_generator(time_signatures[b % len(time_signatures)], ranges[i].value))

if __name__ == '__main__':
    out = input("Enter output path (default is current directory): ")

# make the score
sc = stream.Score(parts)
if (out == ""):
    p = Path('./ChanceComposition')
else:
    p = Path(out + "/ChanceComposition")
sc.write('lily.pdf', p)