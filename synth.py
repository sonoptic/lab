import time

import itertools

import math

from collections import OrderedDict

from synthplayer.sample import Sample

from synthplayer.synth import WaveSynth, key_freq, octave_notes, major_chord_keys

from synthplayer.synth import Sine, Triangle, Pulse, Square, SquareH, Sawtooth, SawtoothH, WhiteNoise, Linear, Harmonics

from synthplayer.synth import FastSine, FastPulse, FastSawtooth, FastSquare, FastTriangle

from synthplayer.synth import EchoFilter, EnvelopeFilter, AbsFilter, ClipFilter, DelayFilter

from synthplayer.playback import Output

from synthplayer import params



'''

class Synth(threading.Thread):



    def prepare_waves():



    def __init__():

        self.synth = WaveSynth(samplerate=8000)



        s1 = synth.triangle(freq, duration=2)



    def run():





'''

synth = WaveSynth()







def make_sample(f_carrier):

    duration = 100

    _attack = 0.05

    _sustain = 0.2

    _decay = 0.6

    _release = 0.8

    #fm = Sine(duration / 0.5, amplitude=0.5)

    #s1 = synth.triangle(f_carrier, duration, amplitude=0.6, fm_lfo=fm)

    #s1.envelope(0.01, 0.1, 0.6, 2)





    s1 = synth.triangle(f_carrier, duration, amplitude=0.5)

    s1.envelope(_attack, _sustain, _decay, _release)

    return s1













if __name__ == "__main__":

    with Output(synth.samplerate, nchannels=1) as out:



        for f in range(51, 254, 10):

            print(f)

            sample = make_sample(171)

            out.play_sample(sample, repeat=True)

            out.wait_all_played()





        
