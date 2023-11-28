"""
title: bach
author: murat yaşar baskın @artmyb
goal: a Note class that enables performing various operations on Note objects
initialize a Note objcet by:
my_note = Note("A4")
"""
import numpy as np
import sounddevice as sd


class Note:
    class CircularList(list):
        def __getitem__(self, index):
            if isinstance(index, slice):
                return super().__getitem__(index)
            elif isinstance(index, int):
                return super().__getitem__(index % len(self))

    sets = CircularList(("C","C#","D","Eb","E","F","F#","G","G#","A","Bb","B"))
    fifths = CircularList(("C","G","D","A","E","B","F#","C#","Ab","Eb","Bb","F"))
    scales = {"major":(0,2,4,5,7,9,11,12),
              "harmonic minor":(0, 2, 3, 5, 7, 8, 11, 12),
              "melodic minor":(0, 2, 3, 5, 7, 9, 11, 12)}


    @staticmethod
    def bykey(key):
        #creates a note object by MIDI number
        octave = key//12 -1
        index = key % 12
        name_set = Note.sets[index]
        name = name_set+str(octave)
        return Note(name)

    @staticmethod
    def byfreq(frequency):
        #created a Note object by a frequency
        key = 69+12*np.log(frequency/440)/np.log(2)
        return Note.bykey(round(key))

    def __init__(self,name,duration=1,dynamic=0.25,timbre=[1]+50*[0]):
        #timbre is the relative amplitudes of the harmonics. default timbre [1,0,0,0,...] representts a sinusoidal.
        self.name = name
        self.duration = duration
        self.dynamic = dynamic
        self.timbre = timbre

    def set(self):
        #returns the name of the note without octave indicator (  A4 = Note("A4), A4.set() = "A" )
        set = ""
        for i in self.name:
            if i.isalpha() or i == "#" or i == "b":
                set = set + i
        return set

    def octave(self):
        octave = self.name.replace(self.set(),"")
        if "#" in octave:
            octave = octave.replace("#","")
        if "b" in octave:
            octave = octave.replace("b","")
        return int(octave)

    def note_index(self):
        #returns the index of the note set in the Note.sets list
        return Note.sets.index(self.set())

    def key(self):
        #returns the MIDI number of the note
        key = self.note_index() + 12*(int(self.octave())+1)
        return key

    def frequency(self):
        #obviously...
        return 440*2**((self.key()-69)/12)

    def add1(self,semitone=1):
        return Note.bykey(self.key()+semitone)

    def __add__(self,semitone):
        #adding an integer and a note returns a note that is that integerx(semi-tone) above the original note.
        return self.add1(semitone)

    def __radd__(self,semitone):
        return self.add1(semitone)

    def change_duration(self,new_duration):
        return Note(self.name, duration=new_duration, dynamic=self.dynamic,
                    timbre=self.timbre)

    def __sub__(self, other):
        #subtracting two notes returns the semi-tone difference
        #subtracting an integer from a returns a note that is that integerx(semi-tone) below the original note.
        if type(other) == Note:
            return self.key() - other.key()
        elif type(other) == int:
            return self.add1(-other)

    def __mul__(self, relative_duration):
        #multiplying the note by a number multiplies the duration of it
        new_duration = self.duration * relative_duration
        return self.change_duration(new_duration)

    def __rmul__(self, relative_duration):
        new_duration = self.duration * relative_duration
        return self.change_duration(new_duration)

    def change_dynamic(self,new_dynamic):
        return Note(self.name, duration=self.duration, dynamic=new_dynamic,
                    timbre=self.timbre)

    def dominant(self,which = 0):
        return self.add1(-5+which*12)

    def subdominant(self,which = 0):
        return self.add1(-7 + which * 12)

    def supertonic(self,which = 0):
        return self.add1(+2 + which * 12)

    def leading_tone(self):
        return self.add1(-1)

    def harmonic(self,n):
        #returns harmonics of the note (as a note)
        key_difference = 12*np.log(n)/np.log(2)
        return self.add1(round(key_difference))

    def subharmonic(self,n):
        return self.harmonic(1/n)

    def chord(self,degree=0,root=0,intervals = (0,4,7)):
        #returns notes of a chord starting from the input note (inversions are included as well)
        #degree is an integer, number uf steps. 0 returns self.
        #root is the root of the note. the input note (self) is the root as default
        #intervals is a list of semi-tone increments onto the base note. default value is for major chord.
        if degree == 0:
            return self
        if root == 0:
            if degree > 0:
                notes = [self+i for i in intervals]
                notes_add = [self+i for i in intervals]
                for i in range(1,int(degree)):
                    for j in notes_add:
                        notes.append(j+i*12)
                return notes[degree]
            if degree < 0:
                notes = [self]+[self+(i-12) for i in reversed(intervals)]
                notes_add = [self]+[self+(i-12) for i in reversed(intervals)]
                for i in range(1, int(-degree)):
                    for j in notes_add:
                        notes.append(j - i * 12)
                return notes[-degree]
        else:
            difference = ((self+120)-Note(root+"0") )%12
            root_note= self-difference
            is_there = 0
            for i in range(12):
                if root_note.chord(i,intervals = intervals).name == self.name:
                    is_there += 1
                    difference = i
                    break
            if is_there == 0:
                raise Exception("Note object is not in root note's chord.")
                return
            return root_note.chord(degree = degree+difference,intervals = intervals)

    def M(self, degree=0, root=0): #major chord
        return self.chord(degree, root, (0, 4, 7))

    def M7(self,degree=0,root=0): # dominant major seventh chord
        return self.chord(degree,root,(0,4,7,10))

    def M7M(self,degree=0,root=0): #major seventh chord
        return self.chord(degree, root, (0, 4, 7, 11))

    def m(self,degree = 0,root=0): #minor chord
        return self.chord(degree, root, (0, 3, 7))

    def m7(self,degree = 0,root=0): #minor seventh chord
        return self.chord(degree, root, (0, 3, 7, 10))

    def m7dim(self,degree = 0,root=0): #diminished minor seventh chord
        return self.chord(degree, root, (0, 3, 7, 9))

    def m7aug(self, degree=0, root=0): #augmented minor seventh chord
        return self.chord(degree, root, (0, 3, 7, 11))

    def dim7(self,degree = 0,root=0): #diminished seventh chord
        return self.chord(degree, root, (0, 3, 6, 10))

    def add(self,add=1,tone = None, scale = "major"):
        # returns a shift of the input note within a scale.
        # default scale is the major scale of the input note.
        # tone parameter must be a note name without octave indicator. ("C", "Ab",...)
        mainnote_octave = self.octave()
        mainset = self.name.replace(str(mainnote_octave), "")
        if tone is None:
            tone = mainset
            root = 0
        else:
            root = tone
        if scale == "major" or scale == "ionian":
            return self.chord(degree = add,root = root, intervals = Note.scales["major"])
        elif scale == "natural minor" or scale == "aeolian":
            return self.chord(degree = add,root = root, intervals = (0,2,3,5,6,8,10,12))
        elif scale == "harmonic minor":
            return self.chord(degree=add, root=root, intervals=Note.scales["harmonic minor"])
        elif scale == "melodic minor":
            return self.chord(degree=add, root=root, intervals=Note.scales["melodic minor"])
        elif scale == "dorian":
            return self.chord(degree=add, root=root, intervals=(0, 2, 3, 5, 6, 9, 10, 12))
        elif scale == "phyrigian":
            return self.chord(degree=add, root=root, intervals=(0, 1, 3, 5, 7, 8, 10, 12))
        elif scale == "lydian":
            return self.chord(degree=add, root=root, intervals=(0,2,4,6,7,9,11,12))
        elif scale == "mixolydian":
            return self.chord(degree=add, root=root, intervals=(0,2,4,5,7,9,10,12))
        elif scale == "locrian":
            return self.chord(degree=add, root=root, intervals=(0,1,3,5,6,8,10,12))
        else:
            return self.chord(degree=add, root=root, intervals=scale)

    def display(self):
        print("Name:",self.name,",Duration:",self.duration,",MIDI number:",self.key(),",Note set:",self.set())

    def play(self,tempo = 120, sample_rate=44100):
        #obvious...
        time = np.arange(0,(self.duration*60/tempo),1/sample_rate)
        audio = np.array(time.size*[0], dtype=np.int16)
        for i in range(len(self.timbre)):
            audio = audio + self.timbre[i]*np.sin((i+1)*self.frequency()*2*np.pi*time)
        audio = self.dynamic*audio

        sd.play(audio, samplerate=44100)
        sd.wait()

    class array:
        #a class to contain note(s)
        # initialize by my_notes = Notes.array([my_note,my_note2])
        def __init__(self,note_list):
            self.size = len(note_list)
            self.list = note_list

        def __getitem__(self,index):
            return self.list[index]

        def __setitem__(self, index, value):
            self.list[index] = value

        def __len__(self):
            return len(self.list)

        #below methods return the methods of every note, as a list

        def set(self):
            return [i.set() for i in self]

        def key(self):
            return [i.key() for i in self]

        def frequency(self):
            return [i.frequency() for i in self]

        def transpose(self, semitone = 1):
            #transposes all the notes by semitone input.
            return [i.add1(semitone) for i in self]

        def change_duration(self,new_duration):
            return [i.change_duration(new_duration) for i in self]

        def change_dynamic(self,new_dynamic):
            return [i.change_dynamic(new_dynamic) for i in self]

        def display(self):
            for i in self:
                i.display()
            return

        def __add__(self,other):
            #adding an integer will transpose all the notes.
            #adding another array object will unify them
            #adding a note to the array will append the note
            if type(other) == int:
                return self.transpose(other)
            elif type(other) == Note.array:
                return Note.array(self.list + other.list)
            elif type(other) == Note:
                return Note.array(self.list + [other])

        def __radd__(self,other):
            if type(other) == int:
                return self.transpose(other)
            elif type(other) == Note.array:
                return Note.array(self.list + other.list)
            elif type(other) == Note:
                return Note.array([other]+self.list)

        def __sub__(self,other):
            if type(other) == int:
                return self.transpose(-other)
            return

        def __mul__(self,other):
            #multiplying by integer will create that much copies and unify them.
            #if the integer is negative, the same operation happens with the reversed list.
            if type(other) == int and other > 0:
                result = self.list
                for i in range(other-1):
                    result = result + self.list
                return Note.array(result)
            elif type(other) == int and other < 0:
                result = [self[-i] for i in range(1,self.size+1)]
                for i in range(-other-1):
                    result = [self[-i] for i in range(1,self.size+1)] + result
                return Note.array(result)
            return

        def __rmul__(self,other):
            return self.__mul__(other)

        def __neg__(self):
            return self.__mul__(-1)

        def tone(self): #returns a list of pairs that contain the possible tone of a given note array
            result = []
            for scale in list(Note.scales.keys()):
                tone_values = 12 * [1]
                for i in self:
                    belongs = [(i-j).note_index() for j in Note.scales[scale]]
                    for k in range(len(tone_values)):
                        if k not in belongs:
                            tone_values[k] = 0
                if 1 in tone_values:
                    indexes = [item for item, x in enumerate(tone_values) if x == 1]
                    result = result+[(Note.sets[note],scale) for note in indexes]
            return result
