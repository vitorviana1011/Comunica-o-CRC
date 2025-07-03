import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter, spectrogram
import os

class Demultiplexador:
    def __init__(self):
        self.__fs = 44100
        self.__duration = 3
        self.__cutoff_baseband = 3000  # Frequência de corte para filtro LP. Largura de banda do sinal antes da modulação
                        # Se for muito grande, pode pegar interferência de outros self.__canais. Se for muito estreito, pode cortar parte do sinal.
        self.__order = 6 #controle o quão "abrupto" é o filtro. Order = 1 filtro simples, mais leve. Order grande, mais "afiado" ou "forte" o filtro
        self.__canais = {}
        # Frequências das portadoras
        self.__carriers = {'A': 4000, 'B': 10000,'C': 14000}
        self.__muxed, self._fs = self.ler_sinal_multiplexado() 
        self.__demu_dir = "demux"
        if not os.path.exists(self.__demu_dir):
            os.makedirs(self.__demu_dir)

    # === Filtros ===
    @staticmethod
    def bandpass_filter(signal, lowcut, highcut, fs, order):
        nyq = 0.5 * fs
        b, a = butter(order, [lowcut/nyq, highcut/nyq], btype='band')
        return lfilter(b, a, signal)

    @staticmethod
    def lowpass_filter(signal, cutoff, fs, order):
        nyq = 0.5 * fs
        b, a = butter(order, cutoff/nyq, btype='low')
        return lfilter(b, a, signal)

    @staticmethod
    def demodulate(signal, carrier_freq, fs):
        t = np.arange(len(signal)) / fs
        return signal * np.cos(2 * np.pi * carrier_freq * t)

    @staticmethod
    def normalize(signal):
        return signal / np.max(np.abs(signal))

    def plota_spectrograma(self, signal, fs, title, ax):
        f, t, Sxx = spectrogram(signal, fs=fs, nperseg=1024, noverlap=512)
        ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud')
        ax.set_title(title)
        ax.set_ylabel('Frequência (Hz)')
        ax.set_xlabel('Tempo (s)')
        ax.set_ylim(0, 3000)  # Limitar para banda de áudio
        ax.grid(True)

        # === Carregar o sinal multiplexado ===
    def ler_sinal_multiplexado(self):
        muxed, fs_read = sf.read("output/muxed_audio.wav")
        assert fs_read == self.__fs, "Frequência de amostragem incorreta"
        if muxed.ndim > 1:
            muxed = muxed[:, 0]
        return muxed, fs_read
    
    def desmultiplexar(self):
        if not self.__canais:
            arquivos = os.listdir("output")
            arquivos_filtrados = [f for f in arquivos if f.endswith("_base.wav")]
            arquivos_filtrados.sort()
            self.__canais = {
                os.path.splitext(f.replace("_base.wav", ""))[0]: (
                    os.path.join("output", f),
                    os.path.splitext(f)[0] + "_demux.wav"
                ) for f in arquivos_filtrados
            }

        # Obter os nomes dos arquivos
        file_names = sorted(list(self.__canais.keys()))

        # Mapear A, B, C para os nomes dos arquivos em ordem alfabética
        carrier_mapping = dict(zip(['A', 'B', 'C'], file_names))

        for label, fc in self.__carriers.items():
            # 1. Filtrar a banda do canal
            band = self.bandpass_filter(self.__muxed, fc - self.__cutoff_baseband, fc + self.__cutoff_baseband, self.__fs, self.__order)

            # 2. Demodular para baseband
            demod = self.demodulate(band, fc, self.__fs)

            # 3. Filtrar passa-baixa para recuperar o áudio
            baseband = self.lowpass_filter(demod, self.__cutoff_baseband, self.__fs, self.__order)

            # 4. Normalizar e salvar usando o nome do arquivo correspondente
            baseband_norm = self.normalize(baseband)
            if label in carrier_mapping:
                arquivo_nome = carrier_mapping[label]
                # Use o nome base do arquivo original para o arquivo demux
                base_filename = os.path.splitext(os.path.basename(self.__canais[arquivo_nome][0]))[0].replace("_base", "")
                demu_path = os.path.join(self.__demu_dir, f"{base_filename}_demux.wav")
                sf.write(demu_path, baseband_norm, self.__fs)
                print(f"Canal {label} ({base_filename}) demultiplexado e salvo em {demu_path}.")
            else:
                demu_path = os.path.join(self.__demu_dir, f"channel_{label}_demux.wav")
                sf.write(demu_path, baseband_norm, self.__fs)
                print(f"Canal {label} demultiplexado e salvo em {demu_path}.")
        print("Todos os canais extraídos com sucesso.")
    
    def plota_espectro_multiplexador(self):
        N = len(self.__muxed)
        frequencias = fftfreq(N, 1/self.__fs)[:N//2]
        espectro = np.abs(fft(self.__muxed))[:N//2]

        plt.figure(figsize=(10, 4))
        plt.plot(frequencias, espectro)
        plt.title("Espectro do sinal multiplexado")
        plt.xlabel("Frequência (Hz)")
        plt.ylabel("Magnitude")
        plt.grid(True)
        plt.xlim(0, 16000)
        plt.show()


    def ler_pares(self, base_path, demux_path):
        # Ajustar caminho do demux_path para buscar na pasta demu
        demux_path = os.path.join(self.__demu_dir, os.path.basename(demux_path))
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Arquivo base não encontrado: {base_path}")
        if not os.path.exists(demux_path):
            raise FileNotFoundError(f"Arquivo demux não encontrado: {demux_path}")

        try:
            base, fs1 = sf.read(base_path)
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo base {base_path}: {e}")

        try:
            demux, fs2 = sf.read(demux_path)
        except Exception as e:
            raise ValueError(f"Erro ao ler o arquivo demux {demux_path}: {e}")

        if fs1 != fs2:
            raise ValueError("Taxas de amostragem não coincidem")

        min_len = min(len(base), len(demux))
        return base[:min_len], demux[:min_len], fs1

    # Dicionário de pares: base e extraído
    def compara_espectro(self):
        arquivos = os.listdir("output")
        arquivos_filtrados = [f for f in arquivos if f.endswith("_base.wav")]        
        self.__canais = {
                os.path.splitext(f.replace("_base.wav", ""))[0]: (
                os.path.join("output", f),
                f.replace("_base", "_demux")
            ) for f in arquivos_filtrados}
        
        # Gerar espectrogramas para cada canal
        for label, (base_path, demux_path) in self.__canais.items():
            base, demux, fs = self.ler_pares(base_path, demux_path)

            fig, axs = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
            self.plota_spectrograma(base, fs, f"Original - Canal {label}", axs[0])
            self.plota_spectrograma(demux, fs, f"Demux - Canal {label}", axs[1])
            plt.tight_layout()
            plt.show()

    def plota_erros(self):
        #Plotar e comparar cada par
        for label, (base_path, demux_path) in self.__canais.items():
            base, demux, fs = self.ler_pares(base_path, demux_path)
            
            # Calcular erro médio absoluto (MAE)
            mae = np.mean(np.abs(base - demux))
            
            # Plotar primeiros 1000 samples (~23 ms)
            plt.figure(figsize=(10, 3))
            plt.plot(base[:1000], label=f"Sinal original {label}", linewidth=1.5)
            plt.plot(demux[:1000], label=f"Demux {label}", linestyle='dashed', linewidth=1.2)
            plt.title(f"Comparação do Canal {label} - Erro Médio Absoluto: {mae:.6f}")
            plt.xlabel("Amostras")
            plt.ylabel("Amplitude")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()


    def plota_espectro_multiplexadorA(self):
        N = len(self.__muxed)
        frequencias = fftfreq(N, 1/self.__fs)[:N//2]
        # print(frequencias)
        espectro = np.abs(fft(self.__muxed))[:N//2]
        # print(espectro)
        plt.figure(figsize=(10, 4))
        plt.plot(frequencias, espectro)
        plt.title("Espectro do sinal multiplexado")
        plt.xlabel("Frequência (Hz)")
        plt.ylabel("Magnitude")
        plt.grid(True)
        plt.xlim(0, 16000)
        plt.show()