"""
title: bach
author: murat yaşar baskın @artmyb
goal: a Note class that enables performing various operations on Note objects
initialize a Note objcet by:
my_note = Note("A4")
"""
import numpy as np
import sounddevice as sd
import types


class Note:
    class CircularList(list):
        def __getitem__(self, index):
            if isinstance(index, slice):
                return super().__getitem__(index)
            elif isinstance(index, int):
                return super().__getitem__(index % len(self))

    sets = CircularList(("C","C#","D","Eb","E","F","F#","G","Ab","A","Bb","B"))
    fifths = CircularList(("C","G","D","A","E","B","F#","C#","Ab","Eb","Bb","F"))
    scales = {"major":(0,2,4,5,7,9,11,12),
              "harmonic minor":(0, 2, 3, 5, 7, 8, 11, 12),
              "melodic minor":(0, 2, 3, 5, 7, 9, 11, 12)}
    chords = {"Maj":(0,4,7),
              "m": (0, 3, 7),
              "Maj7": (0, 4, 7, 10),
              "m7": (0, 3, 7, 10),
              "mMaj7": (0, 3, 7, 11),
              "Maj9": (0, 4, 7, 10, 14),
              "7": (0,4,7,10),
              "dim": (0,3,6),
              "aug":(0,4,8),
              "maug7":(0,3,7,11),
              "dim7": (0,3,6,10),
              "mM7":(0,3,7,9)}

    @staticmethod
    def bykey(key,duration=1,dynamic=0.25,timbre=[1]):
        #creates a note object by MIDI number
        octave = key//12 -1
        index = key % 12
        name_set = Note.sets[index]
        name = name_set+str(octave)
        return Note(name,duration=duration,dynamic=dynamic,timbre=timbre)

    @staticmethod
    def byfreq(frequency,duration=1,dynamic=0.25,timbre=[1]):
        #created a Note object by a frequency
        key = 69+12*np.log(frequency/440)/np.log(2)
        return Note.bykey(round(key),duration=duration,dynamic=dynamic,timbre=timbre)

    def __init__(self,name,duration=1,dynamic=0.25,timbre=[1]):
        #timbre is the relative amplitudes of the harmonics. default timbre [1] representts a sinusoidal.
        self.name = name
        self.duration = duration
        self.dynamic = dynamic
        self.timbre = timbre
        self.name1 = self.name
        if "Db" in self.name:
            self.name1 = self.name1.replace("Db","C#")
        if "D#" in self.name:
            self.name1 = self.name1.replace("D#","Eb")
        if "Gb" in self.name:
            self.name1 = self.name1.replace("Gb","F#")
        if "G#" in self.name:
            self.name1 = self.name1.replace("G#", "Ab")
        if "A#" in self.name:
            self.name1 = self.name1.replace("A#","Bb")

    def set(self):
        #returns the name of the note without octave indicator (  A4 = Note("A4), A4.set() = "A" )
        set = ""
        for i in self.name1:
            if i.isalpha() or i == "#" or i == "b":
                set = set + i
        return set

    def octave(self):
        octave = self.name1.replace(self.set(),"")
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
        if type(semitone) != int:
            raise Exception("'semitone' parameter must be an integer.")
        return Note.bykey(self.key()+semitone,duration=self.duration,dynamic=self.dynamic,timbre=self.timbre)

    def __add__(self,other):
        #adding an integer and a note returns a note that is that integerx(semi-tone) above the original note.
        if type(other) == int:
            return self.add1(other)
        if type(other) == Note:
            return Note.array([self,other])
        if type(other) == Note.array:
            return Note.array([self]+other.list)

    def __radd__(self,other):
        if type(other) == int:
            return self.add1(other)
        if type(other) == Note:
            return Note.array([other,self])

    def change_duration(self,new_duration):
        return Note(self.name1, duration=new_duration, dynamic=self.dynamic,
                    timbre=self.timbre)

    def __sub__(self, other):
        #subtracting two notes returns the semi-tone difference
        #subtracting an integer from a returns a note that is that integerx(semi-tone) below the original note.
        if type(other) == Note:
            return self.key() - other.key()
        elif type(other) == int:
            return self.add1(-other)
        else:
            raise Exception("Subtraction is only allowed between Note object & Note object or Note object & integer.")

    def __mul__(self, relative_duration):
        #multiplying the note by a number multiplies the duration of it
        if (type(relative_duration) != int or type(relative_duration) != float) or (relative_duration == 0 or relative_duration < 0):
            raise Exception("'relative_duration' parameter must be positive number.")
        new_duration = self.duration * relative_duration
        return self.change_duration(new_duration)

    def __rmul__(self, relative_duration):
        if (type(relative_duration) != int and type(relative_duration) != float) or (relative_duration == 0 or relative_duration < 0):
            raise Exception("'relative_duration' parameter must be positive number.")
        new_duration = self.duration * relative_duration
        return self.change_duration(new_duration)

    def change_dynamic(self,new_dynamic):
        return Note(self.name1, duration=self.duration, dynamic=new_dynamic,
                    timbre=self.timbre)

    def f(self):
        return Note(self.name1, duration=self.duration, dynamic=3*self.dynamic,
                    timbre=self.timbre)


    def dominant(self,which = 0):
        if type(which) != int:
            raise Exception("'which' parameter must be integer.")
        return self.add1(-5+which*12)

    def subdominant(self,which = 0):
        if type(which) != int:
            raise Exception("'which' parameter must be integer.")
        return self.add1(-7 + which * 12)

    def supertonic(self,which = 0):
        if type(which) != int:
            raise Exception("'which' parameter must be integer.")
        return self.add1(+2 + which * 12)

    def leading_tone(self):
        return self.add1(-1)

    def harmonic(self,n):
        #returns harmonics of the note (as a note)
        key_difference = 12*np.log(n)/np.log(2)
        return self.add1(round(key_difference))

    def subharmonic(self,n):
        if type(n) != int:
            raise Exception("'n' parameter must be integer.")
        return self.harmonic(1/n)

    def chord(self,degree=0,root=0,intervals = (0,4,7)):
        if "Db" in root:
            root = root.replace("Db", "C#")
        if "D#" in root:
            root = root.replace("D#", "Eb")
        if "Gb" in root:
            root = root.replace("Gb", "F#")
        if "G#" in root:
            root = root.replace("G#", "Ab")
        if "A#" in root:
            root = root.replace("A#", "Bb")
        if type(degree) != int:
            raise Exception("'degree' parameter must be integer.")
        try:
            temp = Note("root")
        except:
            raise Exception("'root' parameter is invalid, must be a note name. (e.g.: C5, Ab4)")
        if type(intervals) != tuple:
            raise Exception("'intervals' parameter must be a tuple.")
        if len(intervals) < 3:
            raise Exception("'intervals' parameter must have length of at least 3.")
        for i in intervals:
            if type(i) != int:
                Exception("'intervals' parameter must be a tuple of integers types.")

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
                if root_note.chord(i,intervals = intervals).name == self.name1:
                    is_there += 1
                    difference = i
                    break
            if is_there == 0:
                raise Exception("Note object is not in root note's chord.")
                return
            return root_note.chord(degree =degree+difference,intervals = intervals)

    def Maj(self, degree=0, root=0): #major chord
        return self.chord(degree, root, Note.chords["Maj"])

    def d7(self,degree=0,root=0): # dominant major seventh chord
        return self.chord(degree,root,Note.chords["7"])

    def M7(self,degree=0,root=0): #major seventh chord
        return self.chord(degree, root, Note.chords["M7"])

    def m(self,degree = 0,root=0): #minor chord
        return self.chord(degree, root, Note.chords["m"])

    def m7(self,degree = 0,root=0): #minor seventh chord
        return self.chord(degree, root, Note.chords["m7"])

    def m7dim(self,degree = 0,root=0): #diminished minor seventh chord
        return self.chord(degree, root, Note.chords["m7dim"])

    def maug7(self, degree=0, root=0): #augmented minor seventh chord
        return self.chord(degree, root, Note.chords["maug7"])

    def dim(self,degree = 0,root=0): #diminished seventh chord
        return self.chord(degree, root, Note.chords["dim"])

    def dim7(self,degree = 0,root=0): #diminished seventh chord
        return self.chord(degree, root, Note.chords["dim7"])

    def add(self,add=1,tone = None, scale = "major"):
        # returns a shift of the input note within a scale.
        # default scale is the major scale of the input note.
        # tone parameter must be a note name without octave indicator. ("C", "Ab",...)
        if tone == "Db":
            tone = "C#"
        if tone == "D#":
            tone =="Eb"
        if tone == "Gb":
            tone = "F#"
        if tone == "G#":
            tone = "Ab"
        if tone == "A#":
            tone = "Bb"
        if type(add) != int:
            raise Exception("'add' parameter must be integer.")
        if scale not in list(Note.scales.keys()):
            str = ""
            for i in list(Note.scales.keys()):
                str += ", "+i
            raise Exception("'scale' parameter must be one of the following:",str)
        mainnote_octave = self.octave()
        mainset = self.name1.replace(str(mainnote_octave), "")
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
        print("Name:",self.name1,",Duration:",self.duration,",MIDI number:",self.key(),",Note set:",self.set())

    def wave(self, tempo = 120, sample_rate = 44100, fade_time = 0.05):
        time = np.arange(0, (self.duration * 60 / tempo), 1 / sample_rate)
        audio = np.array(time.size * [0], dtype=np.int16)
        for i in range(len(self.timbre)):
            audio = audio + self.timbre[i] * np.sin((i + 1) * self.frequency() * 2 * np.pi * time)
        audio = self.dynamic * audio
        def fadeout(n):
            t = np.linspace(0, np.pi, n)
            return 0.5*(1 + np.cos(t))
        def fadein(n):
            t = np.linspace(np.pi, 2 * np.pi, n)
            return 0.5*(1 + np.cos(t))

        fadein_length = int(fade_time*time.size)
        fadeout_length = int(fade_time*time.size)

        unity = np.array((audio.size-fadeout_length-fadeout_length) * [1], dtype=np.int16)

        unity = np.append(fadein(fadein_length),unity)
        unity = np.append(unity,fadeout(fadeout_length))

        return audio*unity

    def play(self,tempo = 120, sample_rate=44100):
        audio = self.wave(tempo, sample_rate = sample_rate)
        sd.play(audio, samplerate=44100)
        sd.wait()

    class array:
        #a class to contain note(s)
        # initialize by my_notes = Notes.array([my_note,my_note2])
        def __init__(self,note_list):
            self.size = len(note_list)
            self.list = note_list

        def __getitem__(self,index):
            if isinstance(index, int):
                return self.list[index]
            elif isinstance(index, slice):
                return Note.array(self.list[index])
            else:
                raise TypeError("Index must be integer or slice.")

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
            return Note.array([i.add1(semitone) for i in self])

        def change_duration(self,new_duration):
            return Note.array(i.change_duration(new_duration) for i in self)

        def change_dynamic(self,new_dynamic):
            return Note.array(i.change_dynamic(new_dynamic) for i in self)

        def display(self):
            for i in self:
                i.display()

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

        def duration(self):
            total = 0
            for i in self:
                total += i.duration
            return total

        def sort(self,mode = "duration",reverse = False):
            if mode == "duration":
                attributes = [i.duration for i in self]
                sorted_index = sorted(range(self.size), key = lambda k: attributes[k],reverse=reverse)
                return Note.array([self[i] for i in sorted_index])
            elif mode == "pitch":
                attributes = [i.key() for i in self]
                sorted_index = sorted(range(self.size), key=lambda k: attributes[k], reverse=reverse)
                return Note.array([self[i] for i in sorted_index])
            elif mode == "dynamic":
                attributes = [i.dynamic for i in self]
                sorted_index = sorted(range(self.size), key=lambda k: attributes[k], reverse=reverse)
                return Note.array([self[i] for i in sorted_index])
            else:
                raise Exception("'mode' parameter must be one of the following: 'duration', 'pitch', 'dynamic'")

        def tone(self,aslist=True,probabilistic = False,probability_base = 10, scales = 0, hidden = 0):
            # returns a list of pairs that contain the possible tone of a given note array
            # if probabilistic == False, any note within the array that is out of a tone will exclude that tone from the result
            # else, the duration of the notes will affect the result:
            #   the longer a note ise, the higher the probability parameter of the tones it might belong well be.
            #   the result is a list of tuples, sorted according to probability parameter. (tonal center, scale, probablity parameter)
            if scales == 0:
                scales = Note.scales
            result = []
            if type(aslist) != bool:
                raise Exception("'aslist' parameter must be a boolean.")
            if type(probabilistic) != bool:
                raise Exception("'probabilistic' parameter must be a boolean.")
            if hidden == 1:
                space = ""
            else:
                space = " "
            for scale in list(scales.keys()):
                tone_values = 12 * [1]
                for i in self:
                    belongs = [(i - j).note_index() for j in scales[scale]]
                    for k in range(len(tone_values)):
                        if k not in belongs and i.dynamic != 0:
                            if probabilistic == False:
                                tone_values[k] = 0
                            else:
                                tone_values[k] *= probability_base**(-i.duration*i.dynamic**0.25)
                if probabilistic == False:
                    if 1 in tone_values:
                        indexes = [item for item, x in enumerate(tone_values) if x == 1]
                        if aslist == False:
                            result = result + [(Note.sets[note] + space + scale) for note in indexes]
                        else:
                            result = result + [(Note.sets[note], scale) for note in indexes]
                else:
                    if aslist == False:
                        result.append([[Note.sets[i]+space+scale, tone_values[i]] for i in range(12)])
                        x = 1
                    else:
                        result.append([(Note.sets[i],scale, tone_values[i]) for i in range(12)])
                        x = 2
            if probabilistic == True:
                results = []
                for i in result:
                    for j in i:
                        results.append(j)
                results = sorted(results, key= lambda k: k[x], reverse=True)
                normalize = [i[x] for i in results]
                normalize = sum(normalize)
                if aslist == True:
                    result = [(i[0],i[1],i[2]/normalize) for i  in results]
                else:
                    result = [(i[0], i[1] / normalize) for i in results]
            return result

        def root(self,aslist=True,probabilistic = False, probability_base = 2, chords = 0): #returns the chords to which the notes belong, as string
            # aslist = False return conventional chord names like CM7
            # aslist = True returns pairs whose first index is the root note (string), the second index is chord type
            if chords == 0:
                chords = Note.chords
            result = self.tone(aslist=aslist,probabilistic=probabilistic,probability_base=probability_base,scales=chords, hidden = 1)
            return result

        def consonance(self,n=1): #gives consonance value between multiple notes as an integer
            #the number on its own might not be mean anything.
            #calculate a base consonance with the note itself to compare and get a relevant result.
            """
            the algorithm is a calculation of how well the notes fit together within any harmonic series.

            according to this algorithm, the rank of consonance within an octave;

            with the upper note held constant:
            unison, octave, perfect fifth, perfect fourth, major sixth, major third, minor third, minor seventh, tritone, minor sixth, major second, major seventh, minor second

            with the lower note held constant:
            octave, unison, perfect fifth, major sixth, perfect fourth, minor seventh, major third, minor sixth, tritone, minor third, major seventh, major second, minor second
            """
            keys = [i.key() for i in self]
            sep = max(keys) - min(keys)
            subharmonics = [[j.subharmonic(i).key() for i in range(1,sep+20+1)] for j in self]
            for i in range(sep+20):
                for j in range(1,len(subharmonics)):
                    current = subharmonics[0][i]
                    for k in range(sep+20):
                        found = True
                        if subharmonics[j][k] != current:
                            found = False
                        if found == True:
                            return current


        def wave(self, tempo = 120, sample_rate=44100, fade_time = 0.05):
            wave1 = np.array([])
            for i in self:
                wave1 = np.append(wave1,i.wave(tempo = tempo, sample_rate=sample_rate, fade_time = fade_time))
            return wave1

        def play(self, tempo=120, sample_rate=44100):
            audio = self.wave(tempo= tempo, sample_rate=sample_rate)
            sd.play(audio, samplerate=44100)
            sd.wait()

        class poly: #class to store note arrays.
            def __init__(self,arrays):
                self.size = len(arrays)
                self.list = arrays

            def __getitem__(self, index):
                if isinstance(index, int):
                    return self.list[index]
                elif isinstance(index, slice):
                    return Note.array.poly(self.list[index])
                else:
                    raise TypeError("Index must be integer or slice.")

            def __setitem__(self, index, value):
                self.list[index] = value

            def __len__(self):
                return len(self.list)

            def transpose(self, semitone=1):
                # transposes all the notes by semitone input.
                return Note.array.poly([i.transpose(semitone) for i in self])

            def change_duration(self, new_duration):
                return Note.array.poly(i.change_duration(new_duration) for i in self)

            def change_dynamic(self, new_dynamic):
                return Note.array.poly(i.change_dynamic(new_dynamic) for i in self)

            def __add__(self,other):
                if type(other) == int:
                    return self.transpose(other)
                elif type(other) == Note.array:
                    return Note.array.poly(self.list.append(other))
                elif type(other) == Note.array.poly:
                    return Note.array.poly(self.list + other.list)

            def __radd__(self, other):
                if type(other) == int:
                    return self.transpose(other)
                elif type(other) == Note.array:
                    return Note.array.poly([other]+self.list)
                elif type(other) == Note.array.poly:
                    return Note.array.poly(other.list+ self.list)

            def __mul__(self,other):
                if type(other) == int:
                    return Note.array.poly([other*i for i in self.list])

            def __rmul__(self,other):
                if type(other) == int:
                    return Note.array.poly([other*i for i in self.list])

            def __sub__(self, other):
                if type(other) == int:
                    return self.transpose(-other)
                return

            def duration(self):
                max = 0
                for i in self:
                    if i.duration() > max:
                        max = i.duration()
                return max

            def wave(self, tempo=120, sample_rate=44100, fade_time = 0.05):
                v1 = self[0].wave(tempo=tempo,sample_rate = sample_rate, fade_time = fade_time)
                if self.size > 1:
                    for i in range(1,self.size):
                        v2 = self[i].wave(tempo=tempo,sample_rate = sample_rate, fade_time = fade_time)
                        if len(v1) < len(v2):
                            res = v2.copy()
                            res[:len(v1)] += v1
                        else:
                            res = v1.copy()
                            res[:len(v2)] += v2
                        v1 = res
                return v1

            def play(self, tempo=120, sample_rate=44100):
                audio = self.wave(tempo=tempo, sample_rate=sample_rate)
                sd.play(audio, samplerate=44100)
                sd.wait()

            def tone(self, aslist=True, probabilistic=False, probability_base=10, scales=0, hidden=0):
                # returns a list of pairs that contain the possible tone of a given note array
                # if probabilistic == False, any note within the array that is out of a tone will exclude that tone from the result
                # else, the duration of the notes will affect the result:
                #   the longer a note ise, the higher the probability parameter of the tones it might belong well be.
                #   the result is a list of tuples, sorted according to probability parameter. (tonal center, scale, probablity parameter)
                if scales == 0:
                    scales = Note.scales
                result = []
                if type(aslist) != bool:
                    raise Exception("'aslist' parameter must be a boolean.")
                if type(probabilistic) != bool:
                    raise Exception("'probabilistic' parameter must be a boolean.")
                if hidden == 1:
                    space = ""
                else:
                    space = " "
                for scale in list(scales.keys()):
                    tone_values = 12 * [1]
                    for j in self:
                        for i in j:
                            belongs = [(i - j).note_index() for j in scales[scale]]
                            for k in range(len(tone_values)):
                                if k not in belongs:
                                    if probabilistic == False and i.dynamic != 0:
                                        tone_values[k] = 0
                                    else:
                                        tone_values[k] *= probability_base ** (-i.duration*i.dynamic**0.25)
                    if probabilistic == False:
                        if 1 in tone_values:
                            indexes = [item for item, x in enumerate(tone_values) if x == 1]
                            if aslist == False:
                                result = result + [(Note.sets[note] + space + scale) for note in indexes]
                            else:
                                result = result + [(Note.sets[note], scale) for note in indexes]
                    else:
                        if aslist == False:
                            result.append([[Note.sets[i] + space + scale, tone_values[i]] for i in range(12)])
                            x = 1
                        else:
                            result.append([(Note.sets[i], scale, tone_values[i]) for i in range(12)])
                            x = 2
                if probabilistic == True:
                    results = []
                    for i in result:
                        for j in i:
                            results.append(j)
                    results = sorted(results, key=lambda k: k[x], reverse=True)
                    normalize = [i[x] for i in results]
                    normalize = sum(normalize)
                    if aslist == True:
                        result = [(i[0], i[1], i[2] / normalize) for i in results]
                    else:
                        result = [(i[0], i[1] / normalize) for i in results]
                return result
Note.es = Note("C0",dynamic = 0)
