#!/usr/bin/env python

import numpy
from scipy.io import wavfile
import sys
import wave

from pylab import *

_AUDIO_SAMPLE_RATE = 2 # bytes
_AUDIO_FRAME_RATE = 44100 # hertz


def read_map_file(filename):
    click_map = []

    with open(filename, "r") as mapfile:
        for line in mapfile:
            if line[0] == "#":
                continue

            fields = line.strip().split()
            click_map.append((int(fields[0]), int(fields[1]), fields[2]))

    return click_map


def read_wav_data(wav_filename):
    rate, wav_data = wavfile.read(wav_filename)

    import pdb; pdb.set_trace()

    if rate != _AUDIO_FRAME_RATE:
        raise ValueError(
            "Error: %s should be sampled at %d" % (wav_filename,
                                                   _AUDIO_FRAME_RATE))
    return wav_data


def write_wav_data(filename, rate, data):
    wavfile.write(filename, rate, data)

def get_tempo_len(tempo):
    return int((60. / tempo) * _AUDIO_FRAME_RATE)

def compute_total_samples(click_map):
    samples = 0
    beat = click_map[0][0]
    tempo = click_map[0][1]

    for transition in click_map[1:]:
        next_beat = transition[0]
        samples += (next_beat - beat) * get_tempo_len(tempo)
        beat = next_beat
        tempo = transition[1]

    return samples

def make_tempo_click(sample, tempo):
    target_len = get_tempo_len(tempo)
    tempo_click = numpy.copy(sample)
    tempo_click.resize(target_len)
    return tempo_click

def create_click_from_map(sample, click_map):
    click_wav = numpy.zeros(compute_total_samples(click_map),
                            numpy.int16)
    beat = click_map[0][0]
    tempo = click_map[0][1]
    on = click_map[0][2] == "on"

    start = 0
    for transition in click_map[1:]:
        next_beat = transition[0]

        if on:
            this_click_wav = make_tempo_click(sample, tempo)
            for i in xrange(next_beat - beat):
                click_wav[start:(start+len(this_click_wav))] = this_click_wav
                start += len(this_click_wav)
        else:
            # TODO make empty stuff
            pass

        beat = next_beat
        tempo = transition[1]
        on = transition[2] == "on"

    return click_wav

def main(argv):
    if len(argv) != 3:
        print "usage: %s map_file out_wav" % argv[0]
        return 1

    map_file = argv[1]
    out_wav = argv[2]

    click_sample = read_wav_data("click.wav")
    click_map = read_map_file(map_file)
    click_wav = create_click_from_map(click_sample, click_map)

    #plot(click_wav)
    #show()

    print "writing wav file of %0.2f seconds." % (
        len(click_wav) / float(_AUDIO_FRAME_RATE))
    write_wav_data(out_wav, _AUDIO_FRAME_RATE, click_wav)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
