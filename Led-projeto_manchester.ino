#define LED_PIN 11
const int bit_duration = 150;
String msg = "O que acontece em Las Vegas, fica em Las Vegas";

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

// Implementa o bit manchester
void send_bit_manchester(int bit) {
  if (bit == 1) {
    digitalWrite(LED_PIN, LOW);
    delay(bit_duration / 2);
    digitalWrite(LED_PIN, HIGH);
    delay(bit_duration / 2);
  } else {
    digitalWrite(LED_PIN, HIGH);
    delay(bit_duration / 2);
    digitalWrite(LED_PIN, LOW);
    delay(bit_duration / 2);
  }
}

void send_byte(char c) {
  for (int i = 7; i >= 0; i--) {
    int bit = (c >> i) & 1;
    send_bit_manchester(bit);
  }
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  Serial.println(">>> Emissor Final Pronto. Envie algo para iniciar.");
}

void loop() {
  if (Serial.available() > 0) { // Espera um sinal (enter) do terminal para iniciar a transmissão
    Serial.read();
    Serial.println("Iniciando transmissao...");

    digitalWrite(LED_PIN, LOW);
    delay(bit_duration * 5);

    // 4 bits iniciais de sincronia com o receptor
    send_bit_manchester(1);
    send_bit_manchester(1);
    send_bit_manchester(0);
    send_bit_manchester(0);
    
    byte tamanho_msg = msg.length();
    send_byte((char)tamanho_msg); // Envia o tamanho da mensagem pro receptor
    
    for (int i = 0; i < msg.length(); i++) {
      send_byte(msg[i]);
    }

    // Envio da mensagem em si
    byte buffer[msg.length()];
    msg.getBytes(buffer, msg.length() + 1);
    byte crc_calculado = calculateCRC8(buffer, msg.length());

    // Chama função que calcula o CRC
    Serial.print("Enviando CRC: ");
    Serial.println(crc_calculado);
    send_byte(crc_calculado); // Envia o CRC

    // Desliga o LED e finaliza a mensagem
    digitalWrite(LED_PIN, LOW);
    Serial.println("\nTransmissao finalizada!");
  }
}
