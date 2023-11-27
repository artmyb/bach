# Note class:
# key is MIDI note number.
# name is the note name followed by octave placement on the piano.
# (the first A note on the piano is A0, the first C note on the piano is A1.)
# length is the length of the note in beats.
# dynamic is the loudness. between 0 and 1
# timbre is a list of relative amplitudes of harmonics. The default timbre [1,0,0,0,0,0,...] represents a sine wave.

you can start by creating a Note object:
note1 = Note("A4")
note2 = Note("E5")

>print(note1.name)
>A4
>print(note1.frequency())
>440
>print(note1.add(1).name)
>Bb
>print(note1.dominant())
>E4
>print(note1.harmonic(3))
>E6
>print(note1.major_scale(0))
>A4
>print(note1.major_scale(6))
>F#5
>print(note1.minor_scale(5),mode="harmonic")
>F#5
>print(note1.major(1))
>C#5
>print(note2-note1)
>7
>print(note1.add_in_scale(3,tonal_center = "F#",scale = "melodic minor"))
>Eb
