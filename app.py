from typing import Optional, List
import re
import streamlit as st
from fractions import Fraction
import pandas as pd


st.set_page_config(
    page_title="Music Intervals and Tuning",
    page_icon="🎼",
    layout="wide",
    menu_items={
        "Get help": "https://github.com/entilzha/music-theory",
        "Report a Bug": "https://github.com/entilzha/music-theory",
        "About": "Code at https://github.com/entilzha/music-theory, by Pedro Rodriguez https://www.pedro.ai",
    },
)
DOWN = "down"
UP = "up"


class Interval:
    def __init__(self, *, name: str, ratio: Fraction, n_semitones: int) -> None:
        self.name = name
        self.ratio = ratio
        self.n_semitones = n_semitones

    def up(self):
        return DirectedInterval(
            name=self.name, ratio=self.ratio, n_semitones=self.n_semitones, direction=UP
        )

    def down(self):
        return DirectedInterval(
            name=self.name,
            ratio=self.ratio,
            n_semitones=self.n_semitones,
            direction=DOWN,
        )

    def __str__(self) -> str:
        return f"{self.name} ({self.n_semitones} Semitones, {self.ratio})"


class DirectedInterval(Interval):
    def __init__(
        self, *, name: str, ratio: Fraction, direction: str, n_semitones: int
    ) -> None:
        super().__init__(name=name, ratio=ratio, n_semitones=n_semitones)
        self.direction = direction


UNISON_RATIO = Fraction(1, 1)
MINOR_SECOND_RATIO = Fraction(16, 15)
MAJOR_SECOND_RATIO = Fraction(9, 8)
MINOR_THIRD_RATIO = Fraction(6, 5)
MAJOR_THIRD_RATIO = Fraction(5, 4)
PERFECT_FOURTH_RATIO = Fraction(4, 3)
PERFECT_FIFTH_RATIO = Fraction(3, 2)
MAJOR_SIXTH_RATIO = Fraction(5, 3)
MINOR_SIXTH_RATIO = Fraction(8, 5)
MAJOR_SEVENTH_RATIO = Fraction(15, 8)
MINOR_SEVENTH_RATIO = Fraction(9, 5)
OCTAVE_RATIO = Fraction(2, 1)

UNISON = Interval(name="Unison", ratio=UNISON_RATIO, n_semitones=0)
MINOR_SECOND = Interval(name="Minor Second", ratio=MINOR_SECOND_RATIO, n_semitones=1)
MAJOR_SECOND = Interval(name="Major Second", ratio=MAJOR_SECOND_RATIO, n_semitones=2)
MINOR_THIRD = Interval(name="Minor Third", ratio=MINOR_THIRD_RATIO, n_semitones=3)
MAJOR_THIRD = Interval(name="Major Third", ratio=MAJOR_THIRD_RATIO, n_semitones=4)
PERFECT_FOURTH = Interval(
    name="Perfect Fourth", ratio=PERFECT_FOURTH_RATIO, n_semitones=5
)
# Interval(name="Diminished Fifth", ratio=0, n_semitones=6),
PERFECT_FIFTH = Interval(name="Perfect Fifth", ratio=PERFECT_FIFTH_RATIO, n_semitones=7)
MINOR_SIXTH = Interval(name="Minor Sixth", ratio=MINOR_SIXTH_RATIO, n_semitones=8)
MAJOR_SIXTH = Interval(name="Major Sixth", ratio=MAJOR_SIXTH_RATIO, n_semitones=9)
MINOR_SEVENTH = Interval(
    name="Minor Seventh", ratio=MINOR_SEVENTH_RATIO, n_semitones=10
)
MAJOR_SEVENTH = Interval(
    name="Major Seventh", ratio=MAJOR_SEVENTH_RATIO, n_semitones=11
)
OCTAVE = Interval(name="Octave", ratio=OCTAVE_RATIO, n_semitones=12)

INTERVALS = [
    MINOR_SECOND,
    MAJOR_SECOND,
    MINOR_THIRD,
    MAJOR_THIRD,
    PERFECT_FOURTH,
    PERFECT_FIFTH,
    MINOR_SIXTH,
    MAJOR_SIXTH,
    MINOR_SEVENTH,
    MAJOR_SEVENTH,
    OCTAVE,
]
N_SEMITONES_TO_INTERVAL = {i.n_semitones: i for i in INTERVALS}
NAME_TO_INTERVAL = {str(i): i for i in INTERVALS}


class Note:
    def __init__(
        self, name: str, root_hz: int, shifts: Optional[List[DirectedInterval]] = None
    ) -> None:
        self.name = name
        self.root_hz = root_hz
        if shifts is None:
            self.shifts = []
        else:
            self.shifts = shifts

    def up(self, interval: Interval):
        return Note(self.name, self.root_hz, shifts=self.shifts + [interval.up()])

    def down(self, interval: Interval) -> "Note":
        return Note(self.name, self.root_hz, shifts=self.shifts + [interval.down()])

    @property
    def hz(self):
        freq = self.root_hz
        for s in self.shifts:
            if s.direction == UP:
                freq = freq * s.ratio
            elif s.direction == DOWN:
                freq = freq / s.ratio
            else:
                raise ValueError()
        return float(freq)

    @property
    def ratio(self):
        fraction = Fraction(1, 1)
        for s in self.shifts:
            if s.direction == UP:
                fraction = fraction * s.ratio
            elif s.direction == DOWN:
                fraction = fraction / s.ratio
            else:
                raise ValueError()
        return fraction

    @property
    def derivation(self):
        out = f"{self.name} ({self.root_hz})"
        names = []
        fracs = []
        if len(self.shifts) > 0:
            for s in self.shifts:
                if s.direction == UP:
                    names.append(f"⬆️ {s.name}")
                    fracs.append(f"{s.ratio}")
                elif s.direction == DOWN:
                    names.append(f"⬇️ {s.name}")
                    fracs.append(f"{1 / s.ratio}")
                else:
                    ValueError()
            names = " ".join(names)
            fracs = " * ".join(fracs)
            return out + " " + names + " = " + fracs
        else:
            return out


A4 = Note("A4", 440)


JUST_TONES = {
    "G3": A4.down(PERFECT_FIFTH).down(PERFECT_FIFTH),
    "G♯3/A♭3": A4.down(PERFECT_FIFTH).down(PERFECT_FIFTH).up(MINOR_SECOND),
    "A3": A4.down(OCTAVE),
    "A♯3/B♭3": A4.down(OCTAVE).up(MINOR_SECOND),
    "B3": A4.down(PERFECT_FIFTH).down(PERFECT_FIFTH).up(MAJOR_THIRD),
    "C3": A4.down(PERFECT_FIFTH).down(PERFECT_FIFTH).up(PERFECT_FOURTH),
    "C♯3/D♭4": A4.down(PERFECT_FIFTH).down(MINOR_SECOND),
    "D4": A4.down(PERFECT_FIFTH),
    "E4": A4.up(PERFECT_FIFTH).down(OCTAVE),
    "F4": A4.down(PERFECT_FIFTH).up(MINOR_THIRD),
    "F♯4/G♭4": A4.down(PERFECT_FIFTH).up(MAJOR_THIRD),
    "G4": A4.up(PERFECT_FOURTH),
    "G♯4/A♭4": A4.down(MINOR_SECOND),
    "A4": A4,
    "A♯4/B♭4": A4.up(MINOR_SECOND),
    "B4": A4.up(MAJOR_SECOND),
    "C4": A4.up(MINOR_THIRD),
    "C♯4/D♭5": A4.up(MAJOR_THIRD),
    "D5": A4.up(PERFECT_FOURTH),
    "D♯5/E♭5": A4.down(PERFECT_FIFTH).up(OCTAVE).up(MINOR_SECOND),
    "E5": A4.up(PERFECT_FIFTH),
    "F5": A4.up(MINOR_SIXTH),
    "F♯5/G♭5": A4.up(PERFECT_FIFTH).up(MAJOR_SECOND),
    "G5": A4.down(PERFECT_FIFTH).down(PERFECT_FIFTH).up(OCTAVE).up(OCTAVE),
    "G♯5/A♭5": A4.up(OCTAVE).down(MINOR_SECOND),
    "A5": A4.up(OCTAVE),
    "A♯5/B♭5": A4.up(OCTAVE).up(MINOR_SECOND),
    "B5": A4.up(OCTAVE).up(MAJOR_SECOND),
}

STEPS = {
    ("A", "B"): 2,
    ("B", "C"): 1,
    ("C", "D"): 2,
    ("D", "E"): 2,
    ("E", "F"): 1,
    ("F", "G"): 2,
    ("G", "A"): 2,
}


def calculate_equal_tone(steps: int):
    return 440 * (2 ** (1 / 12)) ** steps


EQUAL_TONES = {
    "G3": calculate_equal_tone(-14),
    "G♯3/A♭3": calculate_equal_tone(-13),
    "A3": calculate_equal_tone(-12),
    "A♯3/B♭3": calculate_equal_tone(-11),
    "B3": calculate_equal_tone(-10),
    "C3": calculate_equal_tone(-9),
    "C♯3/D♭4": calculate_equal_tone(-8),
    "D4": calculate_equal_tone(-7),
    "D♯4/E♭4": calculate_equal_tone(-6),
    "E4": calculate_equal_tone(-5),
    "F4": calculate_equal_tone(-4),
    "F♯4/G♭4": calculate_equal_tone(-3),
    "G4": calculate_equal_tone(-2),
    "G♯4/A♭4": calculate_equal_tone(-1),
    "A4": calculate_equal_tone(0),
    "A♯4/B♭4": calculate_equal_tone(1),
    "B4": calculate_equal_tone(2),
    "C4": calculate_equal_tone(3),
    "C♯4/D♭5": calculate_equal_tone(4),
    "D5": calculate_equal_tone(5),
    "D♯5/E♭5": calculate_equal_tone(6),
    "E5": calculate_equal_tone(7),
    "F5": calculate_equal_tone(8),
    "F♯5/G♭5": calculate_equal_tone(9),
    "G5": calculate_equal_tone(10),
    "G♯5/A♭5": calculate_equal_tone(11),
    "A5": calculate_equal_tone(12),
    "A♯5/B♭5": calculate_equal_tone(13),
    "B5": calculate_equal_tone(14),
}


def hz_to_nearest_tone(hz: float):
    min_name = None
    min_note = None
    min_delta = None
    for name, note in JUST_TONES.items():
        if min_delta is None or abs(note.hz - hz) < min_delta:
            min_delta = abs(note.hz - hz)
            min_note = note
            min_name = name
    return min_name, min_note


NOTES = [
    "C",
    "C♯/D♭",
    "D",
    "D♯/E♭",
    "E",
    "F",
    "F♯/G♭",
    "G",
    "G♯/A♭",
    "A",
    "A♯/B♭",
    "B",
]
NOTE_TO_NUM = {n: i for i, n in enumerate(NOTES)}
N_NOTES = len(NOTES)


def compute_interval(note: str, interval: Interval, direction: str):
    idx = NOTE_TO_NUM[note]
    if direction == "up":
        next_idx = (idx + interval.n_semitones) % N_NOTES
    elif direction == "down":
        next_idx = (idx - interval.n_semitones) % N_NOTES
    else:
        raise ValueError()
    return NOTES[next_idx]


st.header("Music Intervals, Equal Temperament, and Just Temperament")

col0, col1, col2 = st.columns(3)
with col0:
    selected_note = st.radio("Note", NOTES)

with col1:
    selected_interval_name = st.radio("Interval", NAME_TO_INTERVAL)

with col2:
    selected_direction = st.radio("Direction", ["up", "down"])

paired_note = compute_interval(
    selected_note, NAME_TO_INTERVAL[selected_interval_name], selected_direction
)


def compute_new_tones(note: str, result_note: str, interval: Interval, direction: str):
    matching = []
    for numbered_note, value in JUST_TONES.items():
        if re.sub(r"[0-9]", "", numbered_note) == note:
            if direction == UP:
                root_hz = value.hz
                result_hz = float(root_hz * interval.ratio)
            elif direction == DOWN:
                root_hz = value.hz
                result_hz = float(root_hz / interval.ratio)
            else:
                raise ValueError()
            nearest_name, nearest_note = hz_to_nearest_tone(result_hz)
            matching.append(
                f"  * **Root**: {numbered_note} {root_hz:.4f} **Result**: {result_note} {result_hz:.4f} **Nearest**: {nearest_name} {nearest_note.hz}"
            )
    return "\n".join(matching) + "\n"


matching_tones = compute_new_tones(
    selected_note,
    paired_note,
    NAME_TO_INTERVAL[selected_interval_name],
    selected_direction,
)

left, right = st.columns(2)
with left:
    st.markdown(
        f"""
    * **First Note**: {selected_note}
    * **Interval**: {selected_interval_name} **Direction**: {selected_direction}
    * **Second Note**: {paired_note}
    * **Nearest Just Tones**:
    {matching_tones}
    """
    )


def combined_format(name):
    interval = NAME_TO_INTERVAL[name]
    return f"{interval.name} ({interval.n_semitones})"


with right:
    selected_combined_intervals = st.multiselect(
        "Select Intervals to Combine",
        2 * list(NAME_TO_INTERVAL),
        format_func=combined_format,
    )
    semitones = (
        sum(NAME_TO_INTERVAL[name].n_semitones for name in selected_combined_intervals)
        % 12
    )
    if semitones == 6:
        combined_interval = "Tritone"
    else:
        combined_interval = N_SEMITONES_TO_INTERVAL[semitones]
    st.markdown(
        f"""
    * Semitones: {semitones}
    * Interval: {combined_interval}
    """
    )


rows = []
for name, tone in JUST_TONES.items():
    rows.append(
        {
            "tone": name,
            "hz_frac": f"A440 * {tone.ratio}",
            "just hz": tone.hz,
            "equal hz": EQUAL_TONES[name],
            "derivation": tone.derivation,
        }
    )
df = pd.DataFrame(rows)
st.table(df)
