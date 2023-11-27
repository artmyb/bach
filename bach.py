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
        self.octave_digits = 0
        for i in self.name:
            try:
                a = int(i)
                self.octave_digits+=1
            except:
                pass
        self.octave = self.name[-self.octave_digits:]
        if len(self.timbre) < 50:
            while len(self.timbre) < 50:
                self.timbre.append(0)

    def note_set(self):
        unique_note = self.name.replace(self.octave, "")
        return unique_note

    def note_index(self):
        return Note.note_names.index(self.note_set())

    def key(self):
        key = self.note_index() + 12*(int(self.octave)+1)
        return key

    def frequency(self):
        return 440*2**((self.key()-69)/12)

    def add(self,semitone=1):
        new_note_key = self.key() + semitone
        new_note_octave = new_note_key//12 - 1
        new_note_set = Note.note_names[self.note_index()+semitone-12]
        return Note(new_note_set+str(new_note_octave),duration=self.duration,dynamic=self.dynamic,timbre=self.timbre)

    def change_duration(self,new_duration):
        return Note(self.name, duration=new_duration, dynamic=self.dynamic,
                    timbre=self.timbre)

    def dominant(self,which = 0):
        return self.add(-5+which*12)

    def subdominant(self,which = 0):
        return self.add(-7 + which * 12)

    def supertonic(self,which = 0):
        return self.add(+2 + which * 12)

    def leading_tone(self):
        return self.add(-1)

    def harmonic(self,n):
        key_difference = 12*np.log(n)/np.log(2)
        return self.add(round(key_difference))

    def subharmonic(self,n):
        return self.harmonic(1/n)

    def major_scale(self,degree = 0):
        steps_up = (0,2,4,5,7,9,11,12)
        steps_down = (0,1,3,5,7,8,10,12)
        if degree < 0:
            return self.add(-steps_down[-degree//12+(-degree)%12])
        return self.add(steps_up[degree//12+degree%12])

    def minor_scale(self,degree = 0,mode="harmonic"):
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
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def ionian_scale(self,degree = 0,mode="natural"):
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
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def dorian_scale(self,degree = 0,mode="natural"):
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
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def phrygian_scale(self,degree = 0,mode="natural"):
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
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def lydian_scale(self,degree = 0,mode="natural"):
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
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def mixolydian_scale(self,degree = 0,mode="natural"):
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
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def locrian_scale(self,degree = 0,mode="natural"):
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
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def major(self,degree=0):
        steps_up = (0, 4, 7, 12)
        steps_down = (0, 5, 8,12)
        if degree < 0:
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def minor(self,degree = 0):
        steps_up = (0, 3, 7, 12)
        steps_down = (0, 5, 9, 12)
        if degree < 0:
            return self.add(-steps_down[-degree // 12 + (-degree) % 12])
        return self.add(steps_up[degree // 12 + degree % 12])

    def __sub__(self,another_note):
        return self.key() - another_note.key()

    def add_in_scale(self,add=1,tonal_center = None, scale = "major"):
        mainnote_octave = self.name[-1]
        mainnote_set = self.name.replace(str(mainnote_octave), "")
        if tonal_center is None:
            tonal_center = mainnote_set

        if scale == "major":
            difference = (self.add(120)-Note(tonal_center+"0"))%12
            if difference == 0:
                return self.major_scale(degree = add)
            elif difference == 2:
                return self.dorian_scale(degree=add)
            elif difference == 4:
                return self.phrygian_scale(degree = add)
            elif difference == 5:
                return self.lydian_scale(degree = add)
            elif difference == 7:
                return self.mixolydian_scale(degree = add)
            elif difference == 9:
                return self.minor_scale(degree = add, mode="natural")
            elif difference == 11:
                return self.locrian_scale(degree =add)
        elif scale == "natural minor":
            difference = (self.add(120) - Note(tonal_center+"0")) % 12
            if difference == 0:
                return self.minor_scale(degree=add,mode=scale.split()[0])
            elif difference == 2:
                return self.locrian_scale(degree=add,mode = scale.split()[0])
            elif difference == 3:
                return self.ionian_scale(degree=add,mode = scale.split()[0])
            elif difference == 5:
                return self.dorian_scale(degree=add,mode = scale.split()[0])
            elif difference == 7:
                return self.phrygian_scale(degree=add,mode = scale.split()[0])
            elif difference == 8:
                return self.lydian_scale(degree=add,mode = scale.split()[0])
            elif difference == 10:
                return self.mixolydian_scale(degree=add,mode = scale.split()[0])

        elif scale == "harmonic minor":
            difference = (self.add(120) - Note(tonal_center+"0")) % 12
            if difference == 0:
                return self.minor_scale(degree=add,mode=scale.split()[0])
            elif difference == 2:
                return self.locrian_scale(degree=add,mode = scale.split()[0])
            elif difference == 3:
                return self.ionian_scale(degree=add,mode = scale.split()[0])
            elif difference == 5:
                return self.dorian_scale(degree=add,mode = scale.split()[0])
            elif difference == 7:
                return self.phrygian_scale(degree=add,mode = scale.split()[0])
            elif difference == 8:
                return self.lydian_scale(degree=add,mode = scale.split()[0])
            elif difference == 11:
                return self.mixolydian_scale(degree=add,mode = scale.split()[0])

        elif scale == "melodic minor":
            difference = (self.add(120) - Note(tonal_center+"0")) % 12
            if difference == 0:
                return self.minor_scale(degree=add, mode=scale.split()[0])
            elif difference == 2:
                return self.locrian_scale(degree=add, mode=scale.split()[0])
            elif difference == 3:
                return self.ionian_scale(degree=add, mode=scale.split()[0])
            elif difference == 5:
                return self.dorian_scale(degree=add, mode=scale.split()[0])
            elif difference == 7:
                return self.phrygian_scale(degree=add, mode=scale.split()[0])
            elif difference == 9:
                return self.lydian_scale(degree=add, mode=scale.split()[0])
            elif difference == 11:
                return self.mixolydian_scale(degree=add, mode=scale.split()[0])

    def play(self,tempo = 120, sample_rate=44100):
        time = np.arange(0,(self.duration*60/tempo),1/sample_rate)
        audio = np.array(time.size*[0], dtype=np.int16)
        for i in range(len(self.timbre)):
            audio = audio + self.timbre[i]*np.sin((i+1)*self.frequency()*2*np.pi*time)
        audio = self.dynamic*audio



        sd.play(audio, samplerate=44100)


my_timbre = [1,0.5,0.1,0.1,0.1,0.3,0.05]
note1 = Note("F#4",dynamic = 0.5,timbre=my_timbre)

#tune of symphony no.9 down there

note1.play()
note1.play()
note1.add(1).play()
note1.add(3).play()
note1.add(3).play()
note1.add(1).play()
note1.add(0).play()
note1.add(-2).play()
note1.add(-4).play()
note1.add(-4).play()
note1.add(-2).play()
note1.add(0).play()
note1.add(0).change_duration(1.5).play()
note1.add(-2).change_duration(0.5).play()
note1.add(-2).change_duration(2).play()

note1.play()
note1.play()
note1.add(1).play()
note1.add(3).play()
note1.add(3).play()
note1.add(1).play()
note1.add(0).play()
note1.add(-2).play()
note1.add(-4).play()
note1.add(-4).play()
note1.add(-2).play()
note1.add(0).play()
note1.add(-2).change_duration(1.5).play()
note1.add(-4).change_duration(0.5).play()
note1.add(-4).change_duration(2).play()
