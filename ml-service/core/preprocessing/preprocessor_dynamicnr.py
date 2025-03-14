import numpy as np
import librosa
import noisereduce as nr
from pydub import AudioSegment
from scipy.signal import butter, filtfilt
from api.logger import setup_logger
import logging
from pathlib import Path

from pydub import AudioSegment
import os

# Добавить перед использованием AudioSegment
ffmpeg_path = Path(__file__).parent.parent.parent / "ffmpeg" / "bin" / "ffmpeg.exe"
ffprobe_path = Path(__file__).parent.parent.parent / "ffmpeg" / "bin" / "ffprobe.exe"

if ffmpeg_path.exists():
    AudioSegment.ffmpeg = str(ffmpeg_path)
    os.environ["PATH"] += os.pathsep + str(ffmpeg_path.parent)
else:
    print(f"ВНИМАНИЕ: ffmpeg не найден по пути {ffmpeg_path}")

if ffprobe_path.exists():
    AudioSegment.ffprobe = str(ffprobe_path)
else:
    print(f"ВНИМАНИЕ: ffprobe не найден по пути {ffprobe_path}")

print("Текущий путь к ffmpeg:", AudioSegment.ffmpeg)
print("PATH:", os.environ["PATH"])

class PianoPreprocessor:
    def __init__(self, input_path, target_sr=22050, output_channels=1):
        self.input_path = Path(input_path)
        print(f"[PianoPreprocessor] Инициализация для: {self.input_path}")
        self.target_sr = target_sr
        self.output_channels = output_channels
        self.audio = None
        self.sr = None
        self.processed_audio = None

    def load_and_convert(self):
        try:
            print(f"[Загрузка] Начинаем обработку файла: {self.input_path}")
            audio = AudioSegment.from_file(str(self.input_path))
            
            print(f"[Конвертация] Каналы: {audio.channels} -> {self.output_channels}")
            audio = audio.set_channels(self.output_channels)
            
            temp_path = self.input_path.parent / "temp_piano.wav"
            print(f"[Временный файл] Сохраняем в: {temp_path}")
            audio.export(str(temp_path), format="wav")
            
            print(f"[Загрузка] Чтение временного файла: {temp_path}")
            self.audio, self.sr = librosa.load(str(temp_path), sr=self.target_sr, mono=True)
            print(f"[Успех] Загружено {len(self.audio)} сэмплов")
            
            temp_path.unlink()
            print("[Очистка] Временный файл удален")
            
        except Exception as e:
            print(f"[ОШИБКА] Ошибка загрузки: {str(e)}")
            raise

    def adaptive_noise_reduction(self, noise_frac=0.25, n_fft=2048):

        try:
            print("Starting adaptive noise reduction")
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
            print("Noise reduction complete")
        except Exception as e:
            print(f"Error in adaptive_noise_reduction: {str(e)}")
            raise

        

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
        try:
            output_path = Path(output_path)
            print(f"Saving output to: {output_path}")
            
            audio_int = librosa.util.normalize(self.processed_audio) * 32767
            audio_int = audio_int.astype(np.int16)
            
            AudioSegment(
                audio_int.tobytes(),
                frame_rate=self.sr,
                sample_width=2,
                channels=1
            ).export(output_path, format="wav")
            
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            AudioSegment(
                audio_int.tobytes(),
                frame_rate=self.sr,
                sample_width=2,
                channels=1
            ).export(str(output_path), format="wav")
            
            print(f"File saved successfully: {output_path}")
            print(f"File exists: {output_path.exists()}, size: {output_path.stat().st_size} bytes")
            
        except Exception as e:
            print(f"Error in save_output: {str(e)}")
            raise

        


#processor = PianoPreprocessor("audio_fullclean.wav")
#processed_audio, sr = processor.process_pipeline()
#processor.save_output("audio_fullclean_prep.wav")

#processor = PianoPreprocessor("audio_norm.wav")
#processed_audio, sr = processor.process_pipeline()
#processor.save_output("audio_norm_prep.wav")

#processor = PianoPreprocessor("audio_silent.wav")
#processed_audio, sr = processor.process_pipeline()
#processor.save_output("audio_silent_prep.wav")

# processor = PianoPreprocessor("audio_hot1.wav")
# processed_audio, sr = processor.process_pipeline()
# processor.save_output("audio_hot1_prep.wav")

# processor = PianoPreprocessor("audio_hot2.wav")
# processed_audio, sr = processor.process_pipeline()
# processor.save_output("audio_hot2_prep.wav")
