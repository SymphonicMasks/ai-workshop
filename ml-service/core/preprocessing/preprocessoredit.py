import numpy as np
import noisereduce as nr
from pydub import AudioSegment
import librosa

class PianoAudioDenoiser_Edit:
    def __init__(self, input_file, output_file="denoised.wav"):
        self.input_file = input_file
        self.output_file = output_file
        self.audio = None
        self.sr = None
        self.noise_profile = None
        
    def load_audio(self):
        if not self.input_file.endswith('.wav'):
            audio = AudioSegment.from_file(self.input_file)
            audio.export("temp.wav", format="wav")
            self.audio, self.sr = librosa.load("temp.wav", sr=None)
        else:
            self.audio, self.sr = librosa.load(self.input_file, sr=None)

    def reduce_noise(self, stationary=True, prop_decrease=0.8, freq_mask_smooth_hz=500):
        denoised_audio = nr.reduce_noise(
            y=self.audio,
            sr=self.sr,
            stationary=stationary,
            prop_decrease=prop_decrease,
            freq_mask_smooth_hz=freq_mask_smooth_hz
        )

        self.audio = librosa.util.normalize(denoised_audio)

    def post_process(self, lowcut=16, highcut=7903):
        nyq = 0.5 * self.sr
        low = lowcut / nyq
        high = highcut / nyq
        
        from scipy.signal import butter, filtfilt
        b, a = butter(4, [low, high], btype='band')
        self.audio = filtfilt(b, a, self.audio)

    def save_audio(self):
        audio_int = np.int16(self.audio * 32767)
        AudioSegment(
            audio_int.tobytes(),
            frame_rate=self.sr,
            sample_width=2,
            channels=1
        ).export(self.output_file, format="wav")

    def process(self):
        self.load_audio()
        self.reduce_noise()
        #self.post_process()
        self.save_audio()
        return self.output_file


processor = PianoAudioDenoiser_Edit(
        input_file="audio_plusnorm.wav",
        output_file="clean_try.wav"
    )
processor.process()


