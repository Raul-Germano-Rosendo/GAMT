/*
int leds[] = {8, 9, 10, 11};
int botoes[] = {2, 3, 4, 5};

bool travado = false;
int ledAtivo = -1;
unsigned long tempoInicio = 0;
unsigned long duracao = 10000; // 10 segundos

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(leds[i], OUTPUT);
    pinMode(botoes[i], INPUT_PULLUP);
  }
}

void loop() {

  // Se NÃO está travado, verifica botões
  if (!travado) {
    for (int i = 0; i < 4; i++) {
      if (digitalRead(botoes[i]) == LOW) {
        digitalWrite(leds[i], HIGH);
        ledAtivo = i;
        tempoInicio = millis();
        travado = true;
        break; // impede múltiplos ao mesmo tempo
      }
    }
  }

  // Se está travado, espera os 10 segundos
  if (travado) {
    if (millis() - tempoInicio >= duracao) {
      digitalWrite(leds[ledAtivo], LOW);
      travado = false;
      ledAtivo = -1;
    }
  }
}
*/