import numpy as np
import librosa
import noisereduce as nr
from pydub import AudioSegment
from scipy.signal import butter, filtfilt

class PianoPreprocessor:
    def __init__(self, input_path, target_sr=22050, output_channels=1):
        self.input_path = input_path
        self.target_sr = target_sr
        self.output_channels = output_channels
        self.audio = None
        self.sr = None
        self.processed_audio = None

    def load_and_convert(self):
        audio = AudioSegment.from_file(self.input_path)
        audio = audio.set_channels(self.output_channels)
        audio.export("temp.wav", format="wav")
        
        self.audio, self.sr = librosa.load("temp.wav", sr=self.target_sr, mono=True)

    def adaptive_noise_reduction(self, noise_frac=0.25, n_fft=2048):
        noise_samples = int(len(self.audio) * noise_frac)
        noise_profile = self.audio[:noise_samples]
        
        rms_noise = np.sqrt(np.mean(noise_profile**2))
        rms_signal = np.sqrt(np.mean(self.audio**2))

        snr_ratio = rms_signal / (rms_noise + 1e-7)  
    
        prop_decrease = np.clip(
            0.75 + 0.2 * (1 - np.tanh(snr_ratio)), 
            0.4, 
            0.95
        )
        
        stationary_flag = rms_noise < 0.1 * rms_signal

        self.processed_audio = nr.reduce_noise(
            y=self.audio,
            y_noise=noise_profile,
            sr=self.sr,
            n_fft=n_fft,
            stationary=stationary_flag,
            prop_decrease=prop_decrease,
            time_constant_s=2.0 if stationary_flag else 0.5,
            freq_mask_smooth_hz=300 if stationary_flag else 100
        )

    def _butter_bandpass(self, lowcut=80, highcut=4000, order=2):
        nyq = 0.5 * self.sr
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    def apply_piano_eq(self):
        b, a = self._butter_bandpass()
        self.processed_audio = filtfilt(b, a, self.processed_audio)

        D = librosa.stft(self.processed_audio)
        magnitude, phase = librosa.magphase(D)
        magnitude = librosa.decompose.nn_filter(magnitude)
        self.processed_audio = librosa.istft(magnitude * phase)

    def normalize_audio(self, target_db=-20):
        rms = np.sqrt(np.mean(self.processed_audio**2))
        desired_rms = 10**(target_db / 20)
        self.processed_audio = self.processed_audio * (desired_rms / rms)
        

    def process_pipeline(self):
        self.load_and_convert()
        self.adaptive_noise_reduction()
        self.apply_piano_eq()
        self.normalize_audio()
        
        return self.processed_audio, self.sr

    def save_output(self, output_path):

        audio_int = librosa.util.normalize(self.processed_audio) * 32767
        audio_int = audio_int.astype(np.int16)
        
        AudioSegment(
            audio_int.tobytes(),
            frame_rate=self.sr,
            sample_width=2,
            channels=1
        ).export(output_path, format="wav")

