#!/usr/bin/env python3
import numpy
import struct
import sys
import wave

def main() :
  numberOfArguments = 2;

  if len(sys.argv) != numberOfArguments:
    sys.exit('Wrong number of arguments')

  _, waveFile = sys.argv

  with wave.open(waveFile, 'r') as file:
    freq = file.getframerate()
    nframes = file.getnframes()
    nchannels = file.getnchannels()

    lowest = numpy.inf
    highest = -numpy.inf

    for sample in range(int(nframes/freq)):
      frames = file.readframes(freq)
      data = struct.unpack(str(freq * nchannels) + "h", frames)
      data_numpy = numpy.array(data)
      if nchannels == 2:
        reshaped_data = data_numpy.reshape(-1, 2)
        data_numpy = reshaped_data.sum(axis=1) / 2

      average = numpy.fft.rfft(data_numpy) / freq
      average_abs = numpy.abs(average)
    
      peaks = numpy.argwhere(average_abs >= 20*numpy.average(average_abs))
      if len(peaks) > 0:
        if peaks.min() < lowest: lowest = peaks.min()
        if peaks.max() > highest: highest = peaks.max()

    if numpy.isfinite(lowest) and numpy.isfinite(highest):
      print('low = {}, high = {}'.format(lowest, highest))
    else:
      print('no peaks')

if __name__ == '__main__':
  main()