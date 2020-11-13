from music21 import *
import random
from enum import Enum
from pathlib import Path

### CONSTANTS ###

MAX_MIDI = 84
MIN_MIDI = 36
MAX_CHORD_SIZE = 4

instruments = [instrument.Flute, instrument.Clarinet, instrument.Violin, instrument.Violoncello, instrument.Piano]
class range_enum(Enum):
    FLUTE_RANGE = (60, 96)
    CLARINET_RANGE = (50, 94)
    VIOLIN_RANGE = (55, 103)
    CELLO_RANGE = (36, 56)
    PIANO_RANGE = [[21, 60], [60, 109]]
ranges = list(range_enum)

BARS = 8

# probabilities:
REST_DISTRIBUTION = 0.2
durations = [duration.Duration(d, dots=o) for o in range(0, 3) for d in {1/4, 1/2, 1, 2}]
time_signatures = ['4/4', '4/4', '4/4', '4/4', '4/4', '4/4', '5/4', '9/8', '12/8', '3/8', '3/4', '6/8']
last_ts = ''
random.shuffle(time_signatures)

### END CONSTANTS ###

# generate a random measure
def measure_generator(time_sig, inst_range, chords=False):
    bar = stream.Measure()
    ts = meter.TimeSignature(time_sig)
    global last_ts
    if (time_sig is last_ts):
        ts.symbol = ' '
    last_ts = time_sig
    bar.timeSignature = ts
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
                chord_size = random.randint(1, MAX_CHORD_SIZE)
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
def part_generator(part, r, chords=False):
    for b in range(0, BARS):
        part.append(measure_generator(time_signatures[b % len(time_signatures)], r, chords))
        
# make the score
def score_generator():
    to_score = stream.Score()
    layouts = []
    for i in range(0, len(instruments)):
        if ('KeyboardInstrument' in instruments[i]().classes):
            upper = stream.Part()
            lower = stream.Part()
            upper.insert(0, instruments[i]())
            upper.insert(0, clef.GClef())
            part_generator(upper, ranges[i].value[1], True)
            lower.insert(0, instruments[i]())
            lower.insert(0, clef.BassClef())
            part_generator(lower, ranges[i].value[0], False)
            to_score.insert(0, upper)
            to_score.insert(0, lower)
            staff_group = layout.StaffGroup([upper, lower], name=instruments[i]().bestName(), abbreviation=instruments[i]().instrumentAbbreviation, symbol='brace')
            layouts.append(staff_group)
        else:
            p = stream.Part()
            p.insert(0, instruments[i]())
            part_generator(p, ranges[i].value)
            if (instruments[i] is instrument.Violoncello):
                p.insert(0, clef.BassClef())
            to_score.insert(0, p)
            staff_group = layout.StaffGroup([p], name=instruments[i]().bestName(), abbreviation=instruments[i]().instrumentAbbreviation, symbol='bracket')
            layouts.append(staff_group)
    for lay in layouts:
        to_score.insert(0, lay)
    return to_score

if __name__ == '__main__':
    BARS = int(input("How many bars? ") or '8')
    print(BARS)
    REST_DISTRIBUTION = float(input("Enter the distribution of rests as a decimal between 0 and 1 (default 0.2): ") or '0.2')
    print(REST_DISTRIBUTION)
    MAX_CHORD_SIZE = int(input("Enter the maximum chord size in notes (default 4): ") or '4')
    print(MAX_CHORD_SIZE)
    out = input("Enter output path (default is current directory): ")


# drive the code
sc = stream.Score(score_generator())
if (out == ""):
    fp = Path('./ChanceComposition')
else:
    fp = Path(out + "/ChanceComposition")
sc.write('midi', fp)
sc.write('musicxml.pdf', fp)