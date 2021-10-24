import base64
import os
import sys
import wave

import numpy as np

from process import audioprocessing


class DeepSpeechAudio:
   
    def process(self, ds, message):
    
        """Run DeepSpeech inference on each audio file generated after silenceRemoval
        and write to file pointed by file_handle
        """

        base_directory = os.getcwd()

        audio_file = base64.b64decode(message["audio"])
        tmp_file = os.path.join(base_directory, f'tmp/{message["interval"]}.wav')

        with open(tmp_file, "wb") as f:
            f.write(audio_file)

        fin = wave.open(tmp_file, "rb")
        fs_orig = fin.getframerate()
        desired_sample_rate = ds.sampleRate()

        if fs_orig != desired_sample_rate:
            print("Warning: original sample rate ({}) is different than {}hz. Resampling might \
                produce erratic speech recognition".format(fs_orig, desired_sample_rate), file=sys.stderr)
            audio = audioprocessing.AudioProcessing.convert_samplerate(audio_file, desired_sample_rate)
        else:
            audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)

        fin.close()

        metadata = ds.sttWithMetadata(audio)

        current_token_index = 0
        split_start_index = 0
        num_tokens = len(metadata.transcripts[0].tokens)

        split_inferred_text = ''
        while current_token_index < num_tokens:
            is_final_character = current_token_index + 1 == num_tokens
            if is_final_character:
                split_inferred_text = ''.join(
                    [x.text for x in metadata.transcripts[0].tokens[split_start_index:current_token_index + 1]])

                split_start_index = current_token_index + 1
            current_token_index += 1


        return split_inferred_text
