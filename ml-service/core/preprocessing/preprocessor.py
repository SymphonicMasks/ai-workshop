import librosa
import librosa.display
import numpy as np
import scipy.signal as signal
import soundfile as sf

class AudioProcessor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.sr = None
        self.y = None

    def load_audio(self):
        self.y, self.sr = librosa.load(self.input_file, sr=None)

    def remove_noise(self):
        # Преобразуем весь сигнал в частотную область
        stft = librosa.stft(self.y)
        stft_magnitude, stft_phase = np.abs(stft), np.angle(stft)
        # Оцениваем шум как среднее значение по всем частотам на основе всей записи
        noise_mean = np.mean(stft_magnitude, axis=1, keepdims=True)
        # Вычитаем шум по всему сигналу
        stft_denoised = np.maximum(stft_magnitude - noise_mean, 0) * np.exp(1j * stft_phase)
        # Преобразуем обратно в аудиосигнал
        self.y = librosa.istft(stft_denoised)


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

    def normalize_audio(self):
        self.y = librosa.util.normalize(self.y)

    def save_audio(self, output_file="good_cleaned_audio_1_vers.wav"):
        sf.write(output_file, self.y, self.sr)

    def process(self, output_file="good_cleaned_audio_1_vers.wav"):
        self.load_audio()
        self.remove_noise()
        self.apply_bandpass_filter()
        self.normalize_audio()
        self.save_audio(output_file)

processor = AudioProcessor("good_playing.mp3")
processor.process()
