import numpy as np
import soundfile as sf
import os

class Multiplexador:
    def __init__(self): # Construtor
        self.__fs = 44100    # Frequência de amostragem (Hz)
        self.__duration = 30  # Duração do sinal (segundos)
        self.__fc = [4000,   # Portadora do sinal A
                     10000,  # Portadora do sinal B
                     14000]  # Portadora do sinal C
        self.nomes_entrada = []  # Inicializar antes
        self.sinais = []         # Inicializar antes
        self.__rodou = 0
        self.__t = self.amostragem()
        self.__muxed = self.multiplexacao()
 
    def amostragem(self):
       t = np.linspace(0, self.__duration, int(self.__fs * self.__duration), endpoint=False)
       return t
    
    def geraSinais(self): #Sinais de áudio base
        pasta = 'audios'
        arquivos = os.listdir(pasta)
        arquivos_audio = [f for f in arquivos][:3]
        arquivos_audio.sort()
        
        # print(arquivos_audio)
        
        self.nomes_entrada = arquivos_audio
        for nome_arquivo in arquivos_audio:
            caminho_arquivo = os.path.join(pasta, nome_arquivo)
            audio, _ = sf.read(caminho_arquivo)
            if audio.ndim > 1:
                audio = audio.mean(axis=1)
            if len(audio) > len(self.__t):
                audio = audio[:len(self.__t)]
            elif len(audio) < len(self.__t):
                audio = np.pad(audio, (0, len(self.__t) - len(audio)))
            self.sinais.append(audio)
    
    def modulacao(self): #  Modulação em amplitude (DSB)
        retorno = []
        n = min(len(self.sinais), len(self.__fc))
        for i in range(n):
            f = self.sinais[i]
            retorno.append(f * np.cos(2 * np.pi * self.__fc[i] * self.__t))
        return retorno

    def salvaSinais(self, muxed):
        # Garante que a pasta 'output' existe
        os.makedirs("output", exist_ok=True)
        sf.write("output/muxed_audio.wav", muxed, self.__fs)
        for i, nome in enumerate(self.nomes_entrada):
            nome_sem_extensao = os.path.splitext(nome)[0]
            sf.write(f"output/{nome_sem_extensao}_base.wav", self.sinais[i], self.__fs)
        print("Multiplexação concluída e salva no arquivo muxed_audio.wav.")

    def multiplexacao(self):
        if self.__rodou == 0:
            self.geraSinais()
            muxed = self.modulacao()
            muxed = sum(muxed) # Multiplexação
            muxed /= np.max(np.abs(muxed)) #Normalizar para evitar clipping
            self.salvaSinais(muxed)
            self.__rodou = 1
            return muxed
        return None