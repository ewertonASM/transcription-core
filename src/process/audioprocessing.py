import subprocess

import numpy as np


class AudioProcessing:

    def convert_samplerate(self, audio_path, desired_sample_rate):
        """Convert extracted audio to the format expected by DeepSpeech
        """

        sox_cmd = "sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer \
            --endian little --compression 0.0 --no-dither norm -3.0 - ".format(
            quote(audio_path), desired_sample_rate)
        try:
            output = subprocess.check_output(
                shlex.split(sox_cmd), stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("SoX returned non-zero status: {}".format(e.stderr))
        except OSError as e:
            raise OSError(e.errno, "SoX not found, use {}hz files or install it: {}".format(
                desired_sample_rate, e.strerror))

        return np.frombuffer(output, np.int16)
