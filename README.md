
Note class for python:

move bach.py to your main directory, import the class by -> from bach import Note

key is MIDI note number.

name is the note name followed by octave placement on the piano.

(the first A note on the piano is A0, the first C note on the piano is A1.)

length is the length of the note in beats.

dynamic is the loudness. between 0 and 1

timbre is a list of relative amplitudes of harmonics. The default timbre [1,0,0,0,0,0,...] represents a sine wave.

you can start by creating a Note object:


    note = Note("A0")
    
    note.display()
    
    Name: A0 ,Duration: 1 ,MIDI number: 21 ,Note set: A
    
    note = Note.byfreq(440)
    note.display()
    
    Name: A4 ,Duration: 1 ,MIDI number: 69 ,Note set: A
    
    (note+1).display()
    
    Name: Bb4 ,Duration: 1 ,MIDI number: 70 ,Note set: Bb
    
    (note-1).display()
    
    Name: G#4 ,Duration: 1 ,MIDI number: 68 ,Note set: G#
    
    note2 = Note.byfreq(256)
    print(note-note2)
    
    9
    
    note.dominant().display()
    
    Name: E4 ,Duration: 1 ,MIDI number: 64 ,Note set: E
    
    note.dominant(which=1).display()
    
    Name: E5 ,Duration: 1 ,MIDI number: 76 ,Note set: E
    
    note.harmonic(5).display()
    
    Name: C#7 ,Duration: 1 ,MIDI number: 97 ,Note set: C#
    
    note.M(0).display()
    
    Name: A4 ,Duration: 1 ,MIDI number: 69 ,Note set: A
    
    note.M(1).display()
    
    Name: C#5 ,Duration: 1 ,MIDI number: 73 ,Note set: C#
    
    note.add(5,tone="C",scale="major").display()
    
    Name: F5 ,Duration: 1 ,MIDI number: 100 ,Note set: E
    
    melody = Note.array([note,note2,note+5,note-2])
    melody.display()
    
    Name: A4 ,Duration: 1 ,MIDI number: 69 ,Note set: A
    Name: C4 ,Duration: 1 ,MIDI number: 60 ,Note set: C
    Name: D5 ,Duration: 1 ,MIDI number: 74 ,Note set: D
    Name: G4 ,Duration: 1 ,MIDI number: 67 ,Note set: G
    
    melody = 2*melody
    melody.display()
    
    Name: A4 ,Duration: 1 ,MIDI number: 69 ,Note set: A
    Name: C4 ,Duration: 1 ,MIDI number: 60 ,Note set: C
    Name: D5 ,Duration: 1 ,MIDI number: 74 ,Note set: D
    Name: G4 ,Duration: 1 ,MIDI number: 67 ,Note set: G
    Name: A4 ,Duration: 1 ,MIDI number: 69 ,Note set: A
    Name: C4 ,Duration: 1 ,MIDI number: 60 ,Note set: C
    Name: D5 ,Duration: 1 ,MIDI number: 74 ,Note set: D
    Name: G4 ,Duration: 1 ,MIDI number: 67 ,Note set: G
    
    print(melody.tone())
    
    [('C', 'major'), ('F', 'major'), ('G', 'major'), ('Bb', 'major'), ('G', 'harmonic minor'), ('C', 'melodic minor'), ('G', 'melodic minor')]
    
    note1 = Note("A5")
    note2 = Note("C5")
    notes = Note.array([note1,note2])
    print(notes.root())
    
    ['FMaj', 'Am', 'DMaj7', 'FMaj7', 'Dm7', 'Am7', 'AmMaj7', 'D7', 'F7', 'F#dim', 'Adim', 'Amaug7', 'F#dim7', 'Adim7', 'CmM7', 'AmM7']
    
    intervals = ("unison","minor second","major second","minor third","major third", "perfect fourth","tritone","perfect fifth","minor sixth","major sixth","minor seventh", "major seventh", "octave")
    
    consonances_in_octave = [Note.array(note1,note1-i).consonance() for i in range(12)]
    
    sorted_indices = sorted(range(len(consonances_in_octave)), key=lambda k:consonances_in_octave[k])
    
    for i in range(len(sorted_indices)):
        print(intervals[sorted_indices[len(sorted_indices)-i-1]])
    
    unison
    octave
    perfect fifth
    perfect fourth
    major sixth
    major third
    minor third
    minor seventh
    tritone
    minor sixth
    major second
    major seventh
    minor second

    A = Note("A5")
    C_sharp,D_sharp = A+4,A+6
    notes = Note.array([A,C_sharp,D_sharp])
    print(notes.tone())
    
    [('E', 'major'), ('C#', 'natural minor'), ('C#', 'harmonic minor'), ('Bb', 'harmonic minor'), ('E', 'melodic minor'), ('F#', 'melodic minor'), ('Bb', 'melodic minor')]
    
    print(notes.root())
    
    [('B', 'Maj9'), ('Eb', 'dim7'), ('F#', 'mM7')]
    
    print(notes.root(aslist=False))
    
    ['BMaj9', 'Ebdim7', 'F#mM7']
    
    print(notes.tone(probabilistic = True))
    
    [('E', 'major', 0.10558547143913011), ('C#', 'natural minor', 0.10558547143913011), ('C#', 'harmonic minor', 0.10558547143913011), ('Bb', 'harmonic minor', 0.10558547143913011), ('E', 'melodic minor', 0.10558547143913011), ('F#', 'melodic minor', 0.10558547143913011),.....]
    
    print(notes.root(probabilistic = True))
    
    [('B', 'Maj9', 0.025), ('Eb', 'dim7', 0.025), ('F#', 'mM7', 0.025), ('A', 'Maj', 0.0125), ('F#', 'm', 0.0125), ('Eb', 'Maj7', 0.0125), ('F', 'Maj7', 0.0125), ('A', 'Maj7', 0.0125), ('B', 'Maj7', 0.0125), ('Eb', 'm7', 0.0125), ('F#', 'm7', 0.0125), ('D', 'mMaj7', 0.0125),.....]
