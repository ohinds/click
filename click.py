#!/usr/bin/env python

import numpy
import sys
import wave

_AUDIO_SAMPLE_RATE = 2 # bytes
_AUDIO_FRAME_RATE = 44100 # hertz


def read_map_file(filename):
    click_map = []

    with open(filename, "r") as mapfile:
        for line in mapfile:
            if line[0] == "#":
                continue

            fields = line.strip().split()
            click_map.append(int(fields[0]), int(fields[1]), fields[2])

    return click_map


def read_wav_data(wav_filename):
    wav = wave.open(wav_filename, "rb")

    if wav.getnchannels() != 1:
        raise ValueError(
            "Error: %s should only have one channel" % wav_filename)

    if wav.getsampwidth() != _AUDIO_SAMPLE_RATE:
        raise ValueError(
            "Error: %s should have a 16 bit sample width" % wav_filename)

    if wav.getframerate() != _AUDIO_FRAME_RATE:
        raise ValueError(
            "Error: %s should only have one channel" % wav_filenameb)

    data = numpy.array(wav.readframes(wav.getnframes()))
    wav.close()
    return data


def write_wav_data(data, filename):
    wav = wave.open(filename, "wb")

    wav.setnchannels(1)
    wav.setsampwidth(_AUDIO_SAMPLE_RATE)
    wav.setframerate(_AUDIO_FRAME_RATE)
    wav.setnframes(len(data))
    wav.writeframes(data)
    wav.close()

def create_click_from_map(sample, click_map)

def main(argv):
    if len(argv) != 2:
        print "usage: %s [options] map_file"

    sample = read_wav_data(click_sample)
    click_map = read_map_file(map_file)
    output_wav = create_click_from_map(click_sample, click_map)
    write_wav_data(click_wav, output_wav)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
