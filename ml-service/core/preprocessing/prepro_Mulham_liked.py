import librosa
import noisereduce as nr
import soundfile as sf
import numpy as np
import scipy.signal as signal


class AudioProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.sr = None
        self.y = None

    def load_audio(self):
        # Загружаем аудиофайл
        self.y, self.sr = librosa.load(self.input_file, sr=None)

    def remove_noise(self):
        # Применяем шумоподавление
        self.y = nr.reduce_noise(y=self.y, sr=self.sr, prop_decrease=0.9)

    def normalize_audio(self):
        # Нормализация громкости (восстанавливаем уровень)
        peak = np.max(np.abs(self.y))
        if peak > 0:
            self.y = self.y / peak  # Масштабируем к диапазону [-1, 1]

    def apply_bandpass_filter(self):
        # Анализируем спектр сигнала для определения частотных границ
        D = librosa.amplitude_to_db(np.abs(librosa.stft(self.y)), ref=np.max)
        freqs = librosa.fft_frequencies(sr=self.sr)
        # Находим индексы частот, которые содержат 95% энергии
        energy = np.sum(D, axis=1)
        total_energy = np.sum(energy)
        cumulative_energy = np.cumsum(energy) / total_energy
        # Ищем диапазон частот, где содержится 95% энергии
        lowcut_index = np.where(cumulative_energy >= 0.025)[0][0]
        highcut_index = np.where(cumulative_energy >= 0.975)[0][0]
        lowcut = freqs[lowcut_index]
        highcut = freqs[highcut_index]
        # Применяем фильтр Баттерворта
        nyquist = 0.5 * self.sr
        low = lowcut / nyquist
        high = highcut / nyquist

        b, a = signal.butter(6, [low, high], btype="band")
        self.y = signal.lfilter(b, a, self.y)

    def save_audio(self, output_file="cleaned_audio_2_vers.wav"):
        sf.write(output_file, self.y, self.sr)

    def process(self, output_file="good_cleaned_audio_2_vers.wav"):
        self.load_audio()
        self.apply_bandpass_filter()
        self.remove_noise()  # Удаляем шумы
        self.normalize_audio()  # Восстанавливаем громкость
        self.save_audio(output_file)

processor = AudioProcessor("good_playing.mp3")
processor.process()
