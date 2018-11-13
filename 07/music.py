#!/usr/bin/env python3

import numpy
import struct
import sys
import wave
from math import log2, pow

def getUnpackFormat(sample_width, nsamples):
  if sample_width == 1:
    return "%iB" % nsamples
  elif sample_width == 2:
    return "%ih" % nsamples
  else:
    sys.exit('Not supported audio')

def convert_stereo(data):
  result = []
  for index in range(0, len(data), 2):
    avg_value = (data[index] + data[index + 1]) / 2
    result.append(avg_value)
  return result

def group_peaks(peaks):
    if not peaks:
        return []

    clustered_peaks = []

    cluster = []
    prev_frequency = None
    for frequency, magnitude in sorted(peaks):
        if not prev_frequency:
            prev_frequency = frequency

        if (frequency - prev_frequency) > 1:
            clustered_peaks.append(max(cluster, key=lambda x: x[1]))
            cluster = []

        cluster.append((frequency, magnitude))
        prev_frequency = frequency
    clustered_peaks.append(max(cluster, key=lambda x: x[1]))

    return clustered_peaks

def get_peaks(start, end, data):
    window = numpy.abs(numpy.fft.rfft(data[start:end]))
    window_average = numpy.average(window)

    peaks = []
    for index, peak in enumerate(window, start=0):
        if peak >= 20 * window_average:
            peaks.append((index, peak))

    grouped_peaks = group_peaks(peaks)
    grouped_peaks.sort(key=lambda x: x[1])
    max_3 = list(map(lambda x: x[0], grouped_peaks[-3:]))
    max_3.sort()
    return max_3
  
def get_tone(freq, userFreq):
    name = [
      "c", "cis", "d", "es",
      "e", "f", "fis", "g", 
      "gis", "a", "bes", "b"
    ]

    C0 = userFreq * pow(2, -(12*4 + 9)/12)
    steps = round(12 * log2(freq / C0))
    octave = steps // 12

    tone = name[steps % 12]
    if octave < 3:
        tone = tone.title()
        tone += (2 - octave) * ','
    else:
        tone += (octave - 3) * '\''

    cents = round(((12 * log2(freq / C0)) % 1) * 100)
    if cents > 50:
        tone += "-{}".format(100 - cents)
    else:
        tone += "+{}".format(cents)

    return tone

def printTone(pitches, index, freq, previous_pitches):
  print(
    "{}-{} {}"
      .format(
        pitches/10,
        index/10,
        " ".join(map(lambda x: get_tone(x, int(freq)), previous_pitches)))
  )

def main():
  numberOfArguments = 3;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, freq, waveFile = sys.argv

  with wave.open(waveFile, 'r') as file:
    frequency = file.getframerate()
    nframes = file.getnframes()
    nchannels = file.getnchannels()
    sample_width = file.getsampwidth()
    data = file.readframes(nframes)

  unpacked_data = struct.unpack(
    getUnpackFormat(sample_width, nframes * nchannels),
    data
  )
  if nchannels == 2:
    unpacked_data = convert_stereo(unpacked_data)

  start = 0
  end = frequency
  step = frequency // 10
  previous_pitches = None
  pitches = 0
  index = 0
  while end <= len(unpacked_data):
    peaks = get_peaks(start, end, unpacked_data)
    start += step
    end += step
    if peaks != previous_pitches:
      if previous_pitches:
        printTone(pitches, index, freq, previous_pitches)
      previous_pitches = peaks
      pitches = index
    index += 1

  if previous_pitches:
    printTone(pitches, index, freq, previous_pitches)

if __name__ == '__main__':
  main()
