Projeto de Comunicação de Dados - UTFPR Apucarana
Descrição do Projeto
Este projeto foi desenvolvido para a disciplina de Comunicação de Dados do curso de Engenharia de Computação da Universidade Tecnológica Federal do Paraná (UTFPR), campus Apucarana.

O objetivo principal é utilizar os conhecimentos da disciplina para implementar a comunicação entre dois dispositivos Arduino Uno por meio de sinais luminosos. O sistema transmite uma mensagem de texto de um emissor para um receptor, que a decodifica e a exibe, garantindo a integridade dos dados através de um protocolo customizado com detecção de erros.

Autores
Gabriel Ferragini (Gerente)

Vitor Viana

Duda Mafra

Leonardo Dal Poz

Informações da Disciplina

Universidade: Universidade Tecnológica Federal do Paraná (UTFPR), campus Apucarana 

Curso: Engenharia de Computação 

Disciplina: Comunicação de Dados 

Funcionalidades Implementadas

Comunicação via Sinais Luminosos: Transmissão de dados utilizando um LED como emissor e um LDR como receptor.

Mensagem Dinâmica: O protocolo suporta o envio de mensagens de texto de até 64 caracteres, com o tamanho sendo enviado dinamicamente.

Codificações de Linha:

NRZ-L: Implementação obrigatória.

Manchester: Implementação bônus para robustez de sincronismo. O código final utiliza esta codificação por ser mais resiliente a erros de clock drift.

Detecção de Erros: Implementação obrigatória de um detector de erros baseado em CRC (Cyclic Redundance Check) para garantir a integridade da mensagem recebida.

Protocolo Robusto: Desenvolvimento de um protocolo com períodos de silêncio e um Start Frame para garantir um sincronismo inicial confiável.

Hardware Necessário
2x Arduino Uno 

1x LED (qualquer cor)

1x Resistor de ~220Ω (para o LED)

1x LDR (Light Dependent Resistor)

1x Resistor de 10kΩ (para o circuito do LDR)

Protoboard e Jumpers

Montagem dos Circuitos
Circuito Emissor
          Arduino Uno (Emissor)
         +----------------------+
         |         Pino 11  •---|---> [ Perna longa (+) do LED ]
         |                      |
         |             GND  •---|---[ Resistor 220Ω ]---[ Perna curta (-) do LED ]
         +----------------------+
Circuito Receptor
          Arduino Uno (Receptor)
         +----------------------+
         |              5V  •---|---> [ Perna 1 do Resistor 10kΩ ]
         |                      |
         |                      |          +-----> [ Perna 2 do Resistor ] ---+
         |                      |          |                                  |
         |         Pino A0  •---|----------+ (Ponto de Leitura)             |
         |                      |                                              |
         |                      |                 [ LDR ] <--------------------+
         |                      |                    |
         |             GND  •---|--------------------+
         +----------------------+
Nota: Este circuito do receptor corresponde à lógica onde luz alta = valor alto no analogRead.

Protocolo de Comunicação
O protocolo final desenvolvido para a codificação Manchester opera na seguinte sequência para cada transmissão:

Período de Silêncio: O emissor mantém o LED apagado por 5 bit_duration para garantir uma linha limpa.

Start Frame: Envia a sequência de bits 1100 para indicar o início de uma transmissão e permitir a sincronização do receptor.

Byte de Comprimento: Envia um único byte contendo o número de caracteres da mensagem.

Dados (Payload): Envia os bytes correspondentes aos caracteres da mensagem.

CRC: Envia um byte de checksum CRC-8 calculado a partir dos dados da mensagem.

Como Usar o Projeto (Passo a Passo)
Montar os circuitos do Emissor e do Receptor conforme os diagramas.

Calibrar o Receptor:

Carregue um código auxiliar no Emissor que apenas mantém o LED aceso.

Carregue o código PROJETO_RECEPTOR_FINAL.ino no Receptor.

Abra o Monitor Serial do Receptor e siga as instruções para a calibração de claro e escuro. Anote o valor do limiar calculado.

Carregar os Códigos Finais:

Carregue o código PROJETO_EMISSOR_FINAL.ino no Emissor.

Carregue novamente o PROJETO_RECEPTOR_FINAL.ino no Receptor (ele já estará calibrado).

Iniciar a Transmissão:

Abra o Monitor Serial do Emissor e envie qualquer caractere para iniciar a transmissão automática.

Observe o Monitor Serial do Receptor para ver o processo de sincronização e o resultado final da recepção e verificação do CRC.
