# Note class:
# key is MIDI note number.
# name is the note name followed by octave placement on the piano.
# (the first A note on the piano is A0, the first C note on the piano is A1.)
# length is the length of the note in beats.
# dynamic is the loudness. between 0 and 1
# timbre is a list of relative amplitudes of harmonics. The default timbre [1,0,0,0,0,0,...] represents a sine wave.

import numpy as np
import sounddevice as sd


class Note:
    class CircularList(list):
        def __getitem__(self, index):
            if isinstance(index, slice):
                return super().__getitem__(index)
            elif isinstance(index, int):
                return super().__getitem__(index % len(self))

    note_names = CircularList(("C","C#","D","Eb","E","F","F#","G","G#","A","Bb","B"))

    def __init__(self,name,duration=1,dynamic=0.25,timbre=[1]+50*[0]):
        self.name = name
        self.duration = duration
        self.dynamic = dynamic
        self.timbre = timbre

    def note_set(self):
        set = ""
        for i in self.name:
            if i.isalpha() or i == "#" or i == "b":
                set = set + i
        return set

    def octave(self):
        octave = self.name.replace(self.note_set(),"")
        if "#" in octave:
            octave = octave.replace("#","")
        if "b" in octave:
            octave = octave.replace("b","")
        return int(octave)

    def note_index(self):
        return Note.note_names.index(self.note_set())

    def key(self):
        key = self.note_index() + 12*(int(self.octave())+1)
        return key

    def frequency(self):
        return 440*2**((self.key()-69)/12)

    def add1(self,semitone=1):
        new_note_key = self.key() + semitone
        new_note_octave = new_note_key//12 - 1
        new_note_set = Note.note_names[self.note_index()+semitone]
        return Note(new_note_set+str(new_note_octave),duration=self.duration,dynamic=self.dynamic,timbre=self.timbre)

    def __add__(self,semitone):
        return self.add1(semitone)

    def __radd__(self,semitone):
        return self.add1(semitone)

    def change_duration(self,new_duration):
        return Note(self.name, duration=new_duration, dynamic=self.dynamic,
                    timbre=self.timbre)

    def __sub__(self, other):
        if type(other) == Note:
            return self.key() - other.key()
        elif type(other) == int:
            return self.add1(-other)

    def __mul__(self, relative_duration):
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
        key_difference = 12*np.log(n)/np.log(2)
        return self.add1(round(key_difference))

    def subharmonic(self,n):
        return self.harmonic(1/n)

    def major(self,degree = 0):
        steps_up = (0,2,4,5,7,9,11,12)
        steps_down = (0,1,3,5,7,8,10,12)
        if degree < 0:
            return self.add1(-steps_down[-degree//12+(-degree)%12])
        return self.add1(steps_up[degree//12+degree%12])

    def minor(self,degree = 0,mode="harmonic"):
        if mode == "harmonic":
            steps_up = (0, 2, 3, 5, 7, 8, 11, 12)
            steps_down = (0, 1, 4, 5, 7, 9, 10, 12)
        elif mode == "natural":
            steps_up = (0, 2, 3, 5, 7, 9, 10, 12)
            steps_down = (0, 2, 4, 5, 7, 9, 10, 12)
        elif mode == "melodic":
            steps_up = (0, 2, 3, 5, 7, 9, 11, 12)
            steps_down = (0, 1, 3, 5, 7, 9, 10, 12)
        if degree < 0:
            return self.add1(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add1(steps_up[degree // 12 + degree % 12])

    def ionian(self,degree = 0,mode="natural"):
        if mode == "harmonic":
            steps_up = (0, 2, 4, 5, 8, 9, 11, 12)
            steps_down = (0, 1, 3, 4, 7, 8, 10, 12)
        elif mode == "natural":
            steps_up = (0, 2, 4, 5, 7, 9, 11, 12)
            steps_down = (0, 1, 3, 5, 7, 8, 10, 12)
        elif mode == "melodic":
            steps_up = (0, 2, 4, 6, 8, 9, 11, 12)
            steps_down = (0, 1, 3, 4, 6, 8, 10, 12)
        if degree < 0:
            return self.add1(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add1(steps_up[degree // 12 + degree % 12])

    def dorian(self,degree = 0,mode="natural"):
        if mode == "harmonic":
            steps_up = (0, 2, 3, 6, 7, 9, 10, 12)
            steps_down = (0, 2, 3, 5, 6, 9, 10, 12)
        elif mode == "natural":
            steps_up = (0, 2, 3, 5, 7, 9, 10, 12)
            steps_down = (0, 2, 3, 5, 7, 9, 10, 12)
        elif mode == "melodic":
            steps_up = (0, 2, 4, 6, 7, 9, 11, 12)
            steps_down = (0, 2, 3, 5, 6, 8, 10, 12)
        if degree < 0:
            return self.add1(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add1(steps_up[degree // 12 + degree % 12])

    def phrygian(self,degree = 0,mode="natural"):
        if mode == "harmonic":
            steps_up = (0, 1, 4, 5, 7, 8, 10, 12)
            steps_down = (0, 2, 4, 5, 7, 8, 11, 12)
        elif mode == "natural":
            steps_up = (0, 1, 3, 5, 7, 8, 10, 12)
            steps_down = (0, 2, 4, 5, 7, 9, 11, 12)
        elif mode == "melodic":
            steps_up = (0, 3, 4, 5, 7, 8, 10, 12)
            steps_down = (0, 2, 4, 5, 7, 8, 10, 12)
        if degree < 0:
            return self.add1(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add1(steps_up[degree // 12 + degree % 12])

    def lydian(self,degree = 0,mode="natural"):
        if mode == "harmonic":
            steps_up = (0, 3, 4, 6, 7, 9, 11, 12)
            steps_down = (0, 1, 3, 5, 6, 8, 9, 12)
        elif mode == "natural":
            steps_up = (0, 2, 4, 6, 7, 9, 11, 12)
            steps_down = (0, 1, 3, 5, 6, 8, 10, 12)
        elif mode == "melodic":
            steps_up = (0, 2, 3, 5, 6, 8, 10, 12)
            steps_down = (0, 2, 4, 6, 7, 9, 10, 12)
        if degree < 0:
            return self.add1(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add1(steps_up[degree // 12 + degree % 12])

    def mixolydian(self,degree = 0,mode="natural"):
        if mode == "harmonic":
            steps_up = (0, 1, 3, 4, 6, 8, 9, 12)
            steps_down = (0, 3, 4, 6, 8, 9, 11, 12)
        elif mode == "natural":
            steps_up = (0, 2, 4, 5, 7, 9, 10, 12)
            steps_down = (0, 2, 3, 5, 7, 8, 10, 12)
        elif mode == "melodic":
            steps_up = (0, 1, 3, 4, 6, 8, 10, 12)
            steps_down = (0, 2, 4, 6, 8, 9, 11, 12)
        if degree < 0:
            return self.add1(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add1(steps_up[degree // 12 + degree % 12])

    def locrian(self,degree = 0,mode="natural"):
        if mode == "harmonic":
            steps_up = (0, 1, 3, 5, 6, 9, 10, 12)
            steps_down = (0, 2, 3, 6, 7, 9, 11, 12)
        elif mode == "natural":
            steps_up = (0, 1, 3, 5, 6, 8, 10, 12)
            steps_down = (0, 2, 4, 6, 7, 9, 11, 12)
        elif mode == "melodic":
            steps_up = (0, 1, 3, 5, 7, 9, 10, 12)
            steps_down = (0, 2, 3, 5, 7, 9, 11, 12)
        if degree < 0:
            return self.add1(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add1(steps_up[degree // 12 + degree % 12])

    def chord(self,degree=0,root=0,intervals = (0,4,7)):
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
                notes = [0]+[self-(12-i) for i in reversed(intervals)]
                notes_add = [0]+[self-(12-i) for i in reversed(intervals)]
                for i in range(1, int(-degree)):
                    for j in notes_add:
                        notes.append(j - i * 12)
                return notes[-degree]
        else:
            difference = ((self+120)-Note(root+"0") )%12
            print((self+120).name,Note(root+"0").name)
            print(difference)
            root_note= self-difference
            print(root_note.name,difference,degree)
            is_there = 0
            for i in range(5):
                if root_note.M(i).name == self.name:
                    is_there += 1
                    difference = i
                    break
            if is_there == 0:
                raise Exception("Note object is not in root note's chord.")
                return
            return root_note.M(degree+difference)

    def M(self, degree=0, root=0):
        return self.chord(degree, root, (0, 4, 7))

    def M7(self,degree=0,root=0):
        return self.chord(degree,root,(0,4,7,10))

    def M7M(self,degree=0,root=0):
        return self.chord(degree, root, (0, 4, 7, 11))

    def m(self,degree = 0,root=0):
        return self.chord(degree, root, (0, 3, 7))

    def m7(self,degree = 0,root=0):
        return self.chord(degree, root, (0, 3, 7, 10))

    def m7dim(self,degree = 0,root=0):
        return self.chord(degree, root, (0, 3, 7, 9))

    def dim7(self,degree = 0,root=0):
        return self.chord(degree, root, (0, 3, 6, 10))

    def add(self,add=1,tonal_center = None, scale = "major"):
        mainnote_octave = self.name[-1]
        mainnote_set = self.name.replace(str(mainnote_octave), "")
        if tonal_center is None:
            tonal_center = mainnote_set

        if scale == "major":
            difference = (self.add1(120)-Note(tonal_center+"0"))%12
            if difference == 0:
                return self.major(degree = add)
            elif difference == 2:
                return self.dorian(degree=add)
            elif difference == 4:
                return self.phrygian(degree = add)
            elif difference == 5:
                return self.lydian(degree = add)
            elif difference == 7:
                return self.mixolydian(degree = add)
            elif difference == 9:
                return self.minor(degree = add, mode="natural")
            elif difference == 11:
                return self.locrian(degree =add)
        elif scale == "natural minor":
            difference = (self.add1(120) - Note(tonal_center+"0")) % 12
            if difference == 0:
                return self.minor(degree=add,mode=scale.split()[0])
            elif difference == 2:
                return self.locrian(degree=add,mode = scale.split()[0])
            elif difference == 3:
                return self.ionian(degree=add,mode = scale.split()[0])
            elif difference == 5:
                return self.dorian(degree=add,mode = scale.split()[0])
            elif difference == 7:
                return self.phrygian(degree=add,mode = scale.split()[0])
            elif difference == 8:
                return self.lydian(degree=add,mode = scale.split()[0])
            elif difference == 10:
                return self.mixolydian(degree=add,mode = scale.split()[0])

        elif scale == "harmonic minor":
            difference = (self.add1(120) - Note(tonal_center+"0")) % 12
            if difference == 0:
                return self.minor(degree=add,mode=scale.split()[0])
            elif difference == 2:
                return self.locrian(degree=add,mode = scale.split()[0])
            elif difference == 3:
                return self.ionian(degree=add,mode = scale.split()[0])
            elif difference == 5:
                return self.dorian(degree=add,mode = scale.split()[0])
            elif difference == 7:
                return self.phrygian(degree=add,mode = scale.split()[0])
            elif difference == 8:
                return self.lydian(degree=add,mode = scale.split()[0])
            elif difference == 11:
                return self.mixolydian(degree=add,mode = scale.split()[0])

        elif scale == "melodic minor":
            difference = (self.add1(120) - Note(tonal_center+"0")) % 12
            if difference == 0:
                return self.minor(degree=add, mode=scale.split()[0])
            elif difference == 2:
                return self.locrian(degree=add, mode=scale.split()[0])
            elif difference == 3:
                return self.ionian(degree=add, mode=scale.split()[0])
            elif difference == 5:
                return self.dorian(degree=add, mode=scale.split()[0])
            elif difference == 7:
                return self.phrygian(degree=add, mode=scale.split()[0])
            elif difference == 9:
                return self.lydian(degree=add, mode=scale.split()[0])
            elif difference == 11:
                return self.mixolydian(degree=add, mode=scale.split()[0])

    def play(self,tempo = 120, sample_rate=44100):
        time = np.arange(0,(self.duration*60/tempo),1/sample_rate)
        audio = np.array(time.size*[0], dtype=np.int16)
        for i in range(len(self.timbre)):
            audio = audio + self.timbre[i]*np.sin((i+1)*self.frequency()*2*np.pi*time)
        audio = self.dynamic*audio

        sd.play(audio, samplerate=44100)
        sd.wait()



my_timbre = [1,1,2,0.1,0.5,0.1,0.3,0.05]
note1 = Note("Bb3",dynamic = 1,duration=1,timbre=my_timbre)

tune_of_tuba_mirum = [3*note1,
                      3*note1.dominant(),
                      note1+4,note1,
                      note1.M(-1),
                      note1.M(-2),
                      3*note1-12,
                      3*note1.change_dynamic(0),
                      note1,
                      note1.M(1),
                      note1.M(2),
                      note1.M7(3),
                      note1.M7(2),
                      note1.M(1),
                      note1.M7(3)-12,
                      note1.subdominant(which=1).M(-2),
                      note1,
                      note1.subdominant(which=1),
                      note1.dominant(which=1)+1,
                      note1.dominant(which=1),
                      note1.supertonic(),
                      note1.dominant(which=1),
                      note1.subdominant(which=1),
                      3*note1.M(1)]

for i in tune_of_tuba_mirum:
    print(i.name)
    i.play()
