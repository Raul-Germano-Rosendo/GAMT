# 🐍 Aula: Programação com o Jogo da Cobrinha Mágica! 🎮

**Oi, crianças!**  
Bem-vindos à aula de **programação divertida**! Hoje vamos aprender a **fazer o jogo da cobrinha** que **fala** (com sons!) e é para todo mundo jogar, até de olhos fechados! 😎  

**Professor(a):** Use este guia para explicar **passo a passo** os **problemas difíceis** que encontramos no jogo e **como resolvemos** com código. Cada problema tem:
- **🧠 Problema**: O que é chato?
- **🔧 Solução**: Como o código conserta!
- **✏️ Atividade**: Desenhe ou teste!
- **💻 Código**: Olhe no Snake.py!

**Para rodar o jogo primeiro:**  
1. Abra o terminal no VSCode (Ctrl+`).  
2. Digite: `pip install pygame numpy` (só uma vez!).  
3. `cd SnakeGame`  
4. `python Snake.py`  
**Feche os olhos e jogue só com sons! 🐛➡️🍎**

---

## 1. Problema: A cobrinha tem que mexer! 🏃‍♂️
**🧠 Problema:** Como fazer a cabeça ir pra frente e o corpo seguir **sem bagunçar**? Se só mover tudo, vira salada!  

**🔧 Solução:** Usamos uma **lista** de posições (como caixinhas).  
- Cabeça nova = cabeça velha + direção (setas).  
- **Inserir** na frente, **tirar** do final (só cresce se comer).  

**💻 Código (em Snake.py):**
```python
nova_cabeca = (cabeca[0] + self.direcao[0], cabeca[1] + self.direcao[1])
self.cobra.insert(0, nova_cabeca)  # Adiciona na frente!
if not comeu:
    self.cobra.pop()  # Tira do rabo!
```

**✏️ Atividade:** Desenhe 3 posições da cobra virando. Onde vai a nova cabeça?

---

## 2. Problema: Maçã não pode aparecer no corpo! 🍎🚫
**🧠 Problema:** Maçã aleatória pode nascer **dentro** da cobra. Bagunça!  

**🔧 Solução:** **Loop while** tenta posições aleatórias até achar uma **livre** (não na lista cobra).  

**💻 Código:**
```python
def safe_maca(self):
    while True:  # Tenta pra sempre até dar certo!
        x = random.randint(0, 29) * 20  # Grade 30x30
        y = random.randint(0, 29) * 20
        if (x, y) not in self.cobra:
            return (x, y)
```

**✏️ Atividade:** Invente 3 posições ruins pra maçã. Como o código pula elas?

---

## 3. Problema: Bater na parede ou em si mesma! 💥
**🧠 Problema:** Cobra sai da tela ou morde o rabo. Game over!  

**🔧 Solução:** **Verifica** nova cabeça: fora da tela (0 a 600)? Ou no corpo? Aviso sonoro antes!  

**💻 Código:**
```python
if (nova_cabeca[0] < 0 or nova_cabeca[0] >= 600 or
    nova_cabeca in self.cobra[1:]):  # [1:] pula cabeça
    self.state = 'game_over'
```

**✏️ Atividade:** Desenhe cobra batendo na parede. O que o `if` faz?

---

## 4. Problema: Como avisar onde tá a maçã? (Acessível!) 🔊👂
**🧠 Problema:** Jogador cego precisa achar maçã só por som!  

**🔧 Solução:** **Sons mágicos** com numpy:  
- **Agudo** se alinhado no X (esquerda/direita).  
- **Grave** no Y (cima/baixo).  
- **Tom alto/volume forte** = perto. Pan estéreo (L/R)!  

**💻 Código:**
```python
if nova_cabeca[0] == self.maca[0]:  # Alinhado X
    self.audio.play('som_x')  # Beep agudo!
```

**✏️ Atividade:** Feche olhos! Jogue 1 min. Anote sons que guiam.

---

## 5. Problema: Jogo lento no começo, rápido depois! ⚡
**🧠 Problema:** Fácil pra iniciantes, mas cresce desafio.  

**🔧 Solução:** **FPS** (frames por segundo) = 4 + (score / 50). Máx 12.  

**💻 Código:**
```python
self.fps = min(4 + self.score // 50, 12)
self.clock.tick(self.fps)
```

**✏️ Atividade:** Score 100 = quantos FPS? Mais rápido ou lento?

---

## 6. Problema: Pausar e menu! ⏸️
**🧠 Problema:** Precisa parar (P), menu inicial, game over volta pro menu.  

**🔧 Solução:** **Estados** como 'menu', 'playing', 'paused'. Loop principal checa estado.  

**💻 Código:**
```python
if self.state == 'menu':
    running = self.handle_menu()
elif self.state == 'playing' and not self.paused:
    self.update_game()
```

**✏️ Atividade:** Liste 3 estados. O que cada faz?

---

## 7. Problema: Salvar recorde! 🏆
**🧠 Problema:** Fechou jogo, perdeu pontuação máxima.  

**🔧 Solução:** Arquivo `high_score.pkl` com pickle. Salva se maior.  

**💻 Código:**
```python
pickle.dump(score, f)  # Salva!
```

**✏️ Atividade:** Abra `high_score.pkl` no notepad. É número mágico?

---

## 🎉 Parabéns, programadores! 
Vocês viram **7 problemas reais** e **soluções com código**!  
**Desafio final:** Mude cor da cobra pra azul. Rode e mostre!  

**Glossário para kids:**  
- **Lista**: Caixinhas com coisas [(x,y), (x,y)].  
- **While True**: Tenta até dar certo!  
- **If**: "Se isso, faz aquilo".  
- **Função**: Receita reutilizável (def gera_som).  

**Perguntas?** Rode o jogo e experimente! 🐍✨  
**Professor(a):** Imprima colorido. Tempo: 45min + 15min jogo livre.

---
*Feito com ❤️ pro GAMT. Base: Snake.py acessível.*

