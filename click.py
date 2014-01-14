#!/usr/bin/env python

"""click.py

A utility for creating click tracks from markup. The markup is
yaml. See the file example.clk for markup format and features.
"""

import numpy
import optparse
import ordered_yaml_loader
import os
import re
import sys

from scipy.io import wavfile

_AUDIO_FRAME_RATE = 44100 # hertz

def read_wav_data(wav_filename):
    """Reads a wav file and validates that the frame rate is 44100Hz.
    """
    rate, wav_data = wavfile.read(wav_filename)

    if rate != _AUDIO_FRAME_RATE:
        raise ValueError(
            "Error: %s should be sampled at %d" % (wav_filename,
                                                   _AUDIO_FRAME_RATE))
    return wav_data

def get_tempo_len(tempo):
    """Compute the number of samples in a click at a particular tempo.
    """
    return int((60. / tempo) * _AUDIO_FRAME_RATE)

def parse_signature(sig_str):
    """Parse a string representing a time signature, as [num]/[den]
    """
    match = re.match(r'([0-9]+)/([0-9]+)', sig_str)
    return int(match.groups(0)[0]), int(match.groups(0)[1])

def compute_total_samples(click_map):
    """Compute the total number of samples in a click sound file
    resulting from @p click_map
    """
    samples = 0

    for section in click_map:
        sec_val = section.values()[0]
        try:
            sig = parse_signature(sec_val["signature"])
        except:
            pass
        try:
            tempo = sec_val["tempo"]
        except:
            pass
        effective_tempo = tempo * sig[1] / 4.
        samples += (sig[0] * sec_val['measures'] *
                    get_tempo_len(effective_tempo))

    return samples

def make_tempo_click(sample, tempo):
    """Create a click audio sample from @p sample appropriate for @p
    tempo.
    """
    target_len = get_tempo_len(tempo)
    tempo_click = numpy.copy(sample)
    tempo_click.resize(target_len)
    return tempo_click

def create_click_from_map(accent_sample, sample, click_map):
    """Create audio data representing a click track using the @p
    accent_sample and @p sample as sounds and @p click_map as the
    schedule.
    """
    click_wav = numpy.zeros(compute_total_samples(click_map),
                            numpy.int16)

    start = 0
    last_tempo = None
    last_signature = None
    for section in click_map:
        sec_val = section.values()[0]
        if "signature" in sec_val:
            sig = parse_signature(sec_val["signature"])
            last_sig = sig
        elif last_sig is not None:
            sig = last_sig
        else:
            raise ValueError("No time signature specified")

        if "tempo" in sec_val:
            tempo = sec_val["tempo"]
            last_tempo = tempo
        elif last_tempo is not None:
            tempo = last_tempo
        else:
            raise ValueError("No tempo specified")

        effective_tempo = tempo * sig[1] / 4.
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
    script_dir = os.path.dirname(os.path.realpath(__file__))
    usage = "usage: %prog [options] map_file out_wav"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-c", "--click_sample", dest="click_filename",
                      help="wav file to use as the click sound",
                      metavar="FILE",
                      default=os.path.join(script_dir, "click.wav"))
    parser.add_option("-a", "--accent_sample", dest="accent_filename",
                      help="wav file to use as the accented beat click sound",
                      metavar="FILE",
                      default=os.path.join(script_dir, "accent_click.wav"))

    (options, args) = parser.parse_args(argv)

    # validate
    if len(args) < 2:
        parser.print_help()
        return 1

    map_filename = args[1]
    if len(args) == 2:
        out_filename = map_filename + '.wav'
    else:
        out_filename = args[2]

    if not os.path.exists(map_filename):
        print "Error: click map file %s can't be found" % map_filename
        return 1

    if not os.path.exists(options.click_filename):
        print "Error: click sample file %s can't be found" % options.click_filename
        return 1

    if not os.path.exists(options.accent_filename):
        print "Error: accent sample file %s can't be found" % options.accent_filename
        return 1

    # do it
    click_sample = read_wav_data(options.click_filename)
    accent_click_sample = read_wav_data(options.accent_filename)
    click_map = ordered_yaml_loader.load(map_filename)
    click_wav = create_click_from_map(accent_click_sample,
                                      click_sample, click_map)

    # output
    print "writing wav file of %0.2f minutes." % (
        len(click_wav) / float(_AUDIO_FRAME_RATE) / 60.)
    wavfile.write(out_filename, _AUDIO_FRAME_RATE, click_wav)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
