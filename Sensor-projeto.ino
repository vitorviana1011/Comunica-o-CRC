#define SENSOR_PIN A0
const int bit_duration = 150;
int limiar;

// Calcula o checksum CRC-8 para um array de dados.
byte calculateCRC8(const byte *data, size_t len) {
  byte crc = 0x00;
  while (len--) {
    byte extract = *data++;
    for (byte tempI = 8; tempI; tempI--) {
      byte sum = (crc ^ extract) & 0x01;
      crc >>= 1;
      if (sum) {
        crc ^= 0x8C;
      }
      extract >>= 1;
    }
  }
  return crc;
}

int ler_valor_luz() {
  if (analogRead(SENSOR_PIN) > limiar) return 1;
  else return 0;
}

int readBit() {
  delay(bit_duration / 4);
  int primeira_leitura = ler_valor_luz();
  delay(bit_duration / 2);
  int segunda_leitura = ler_valor_luz();
  delay(bit_duration / 4);

  if (primeira_leitura == 0 && segunda_leitura == 1) return 1;
  else if (primeira_leitura == 1 && segunda_leitura == 0) return 0;
  else return -1;
}

char readByte() {
  char char_recebido = 0;
  for (int j = 0; j < 8; j++) {
    int bit_atual = readBit();
    if (bit_atual == -1) bit_atual = 0;
    char_recebido = (char_recebido << 1) | bit_atual;
  }
  return char_recebido;
}

void setup() {
  pinMode(SENSOR_PIN, INPUT);
  Serial.begin(9600);


  // Bloco de Calibração do Sensor LDR
  Serial.println("\n=== INICIANDO CALIBRACAO ===");
  Serial.println("IMPORTANTE: Use o Emissor com LED sempre aceso.");
  delay(1000);
  Serial.println("\nPASSO 1: ESCURO. Cubra o sensor e envie algo.");
  while (Serial.available() == 0) {}
  Serial.read();
  int valor_escuro = analogRead(SENSOR_PIN);
  Serial.print("Leitura no escuro: "); Serial.println(valor_escuro);
  Serial.println("\nPASSO 2: LUZ. Aponte o LED para o LDR e envie algo.");
  while (Serial.available() == 0) {}
  Serial.read();
  int valor_luz = analogRead(SENSOR_PIN);
  Serial.print("Leitura com luz: "); Serial.println(valor_luz);
  limiar = (valor_luz + valor_escuro) / 2;
  Serial.println("---------------------------------");
  Serial.print("CALIBRACAO FINALIZADA! Limiar = "); Serial.println(limiar);
  Serial.println("---------------------------------");
}

void loop() {
  Serial.println("\n>>> MODO DE BUSCA: Procurando o primeiro '1'...");

  while (readBit() != 1) {} // Busca o primeiro bit 1 de inicio da transmissão

  Serial.println(">>> POSSIVEL START FRAME! Verificando sequencia 1100...");
  
  int b2 = readBit();
  int b3 = readBit();
  int b4 = readBit();

  if (b2 == 1 && b3 == 0 && b4 == 0) {
    Serial.println(">>> Start Frame CONFIRMADO! Sincronizado!"); // Se for pego os 4 bits de sincronismo inicia a leitura
    
    byte tamanho_a_ler = readByte();
    Serial.print("Comprimento recebido: "); Serial.println(tamanho_a_ler); // Le o tamanho enviado pelo transmissor
    
    String mensagem_recebida = "";
    byte buffer_msg[tamanho_a_ler];
    
    for (int i = 0; i < tamanho_a_ler; i++) {
      char caractere = readByte();
      mensagem_recebida += caractere;
      buffer_msg[i] = (byte)caractere;
    }

    // Chama CRC
    byte crc_recebido = readByte();
    byte crc_calculado = calculateCRC8(buffer_msg, tamanho_a_ler);
    
    Serial.println("\n--- Verificacao de Integridade (CRC) ---");
    Serial.print("CRC Recebido do Emissor: "); Serial.println(crc_recebido);
    Serial.print("CRC Calculado Localmente: "); Serial.println(crc_calculado);

    // Compara os 2 CRC para verificar a integridade da mensagem
    if (crc_calculado == crc_recebido) {
      Serial.println(">> STATUS: CRC OK! Mensagem integra.");
    } else {
      Serial.println(">> STATUS: ERRO DE CRC! Mensagem corrompida.");
    }
    Serial.println("------------------------------------");

    Serial.println("\n=== MENSAGEM RECEBIDA ===");
    Serial.println(mensagem_recebida);

  } else {
    Serial.println(">>> Falso alarme. Voltando ao modo de busca...");
  }
  
  delay(2000); // Espera 2 segundos antes de buscar a proxima transmisão
}
