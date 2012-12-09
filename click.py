#!/usr/bin/env python

import numpy
import ordered_yaml_loader
import re
import sys

from pylab import *
from scipy.io import wavfile

_AUDIO_FRAME_RATE = 44100 # hertz


def read_wav_data(wav_filename):
    rate, wav_data = wavfile.read(wav_filename)

    if rate != _AUDIO_FRAME_RATE:
        raise ValueError(
            "Error: %s should be sampled at %d" % (wav_filename,
                                                   _AUDIO_FRAME_RATE))
    return wav_data

def get_tempo_len(tempo):
    return int((60. / tempo) * _AUDIO_FRAME_RATE)

def parse_signature(sig_str):
    match = re.match(r'([0-9]+)/([0-9]+)', sig_str)
    return int(match.groups(0)[0]), int(match.groups(0)[1])

def compute_total_samples(click_map):
    samples = 0

    for section in click_map:
        sec_val = section.values()[0]
        sig = parse_signature(sec_val["signature"])
        effective_tempo = sec_val['tempo'] * sig[1] / 4.
        samples += (sig[0] * sec_val['measures'] *
                    get_tempo_len(effective_tempo))

    return samples

def make_tempo_click(sample, tempo):
    target_len = get_tempo_len(tempo)
    tempo_click = numpy.copy(sample)
    tempo_click.resize(target_len)
    return tempo_click

def create_click_from_map(accent_sample, sample, click_map):
    click_wav = numpy.zeros(compute_total_samples(click_map),
                            numpy.int16)

    start = 0
    for section in click_map:
        sec_val = section.values()[0]
        sig = parse_signature(sec_val["signature"])
        effective_tempo = sec_val['tempo'] * sig[1] / 4.
        off = "silent" in sec_val and sec_val["silent"]

        if (sig[0] > 1):
            this_accent_wav = make_tempo_click(accent_sample,
                                               effective_tempo)
        this_click_wav = make_tempo_click(sample, effective_tempo)
        for i in xrange(sec_val['measures']):
            for j in xrange(sig[0]):
                if off:
                    this_wav = numpy.zeros_like(this_click_wav)
                elif sig[0] != 1 and j == 0:
                    this_wav = this_accent_wav
                else:
                    this_wav = this_click_wav
                click_wav[start:(start+len(this_wav))] = this_wav
                start += len(this_click_wav)

    return click_wav

def main(argv):
    if len(argv) != 3:
        print "usage: %s map_file out_wav" % argv[0]
        return 1

    map_file = argv[1]
    out_wav = argv[2]

    click_sample = read_wav_data("click.wav")
    accent_click_sample = read_wav_data("accent_click.wav")
    click_map = ordered_yaml_loader.load(map_file)
    click_wav = create_click_from_map(accent_click_sample,
                                      click_sample, click_map)

    #plot(click_wav)
    #show()

    print "writing wav file of %0.2f minutes." % (
        len(click_wav) / float(_AUDIO_FRAME_RATE) / 60.)
    wavfile.write(out_wav, _AUDIO_FRAME_RATE, click_wav)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
