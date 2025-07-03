from multiplexador import Multiplexador
from demultiplexador import Demultiplexador

def menu():
    print("\n=== Sistema de Multiplexação ===")
    print("1. Multiplexar sinais")
    print("2. Demultiplexar sinais")
    print("3. Plotar espectro do sinal multiplexado")
    print("4. Comparar espectros dos canais")
    print("5. Plotar erros dos canais")
    print("0. Sair")
    return input("Escolha uma opção: ")

if __name__ == "__main__":
    mult = Multiplexador()
    demux = Demultiplexador()
    while True:
        opcao = menu()
        if opcao == "1":
            mult.multiplexacao()
        elif opcao == "2":
            demux.desmultiplexar()
        elif opcao == "3":
            demux.plota_espectro_multiplexadorA()
        elif opcao == "4":
            demux.compara_espectro()
        elif opcao == "5":
            demux.plota_erros()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")