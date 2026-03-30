import pygame
import random
import numpy as np
import pickle
import os

pygame.init()

# 🔥 FORÇA ESTÉREO (evita erro do sndarray)
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Tela (arena maior)
LARGURA = 600
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Snake Acessível")

TAMANHO = 20

PRETO = (0, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (255, 0, 0)

clock = pygame.time.Clock()

# 🔊 Função para gerar beep (AGORA ESTÉREO)
def gerar_som(frequencia=440, duracao=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duracao)

    t = np.linspace(0, duracao, n_samples, False)
    onda = np.sin(2 * np.pi * frequencia * t)

    audio = (onda * 32767).astype(np.int16)

    # 🔥 transforma em estéreo
    audio_estereo = np.column_stack((audio, audio))

    return pygame.sndarray.make_sound(audio_estereo)

# Sons básicos
som_move = gerar_som(440, 0.05)
som_eat = gerar_som(660, 0.2)
som_grow = gerar_som(880, 0.3)

# Sons diferentes
som_x = gerar_som(600)  # agudo
som_y = gerar_som(300)  # grave

# Dict sons
sons = {
    'move': som_move,
    'eat': som_eat,
    'grow': som_grow,
}

# Score
score = 0
HIGH_SCORE_FILE = 'high_score.pkl'

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, 'rb') as f:
            return pickle.load(f)
    return 0

def save_high_score(score):
    high_score = load_high_score()
    if score > high_score:
        with open(HIGH_SCORE_FILE, 'wb') as f:
            pickle.dump(score, f)

high_score = load_high_score()

# 🔥 evita sobreposição infinita de som
som_x.set_volume(0.3)
som_y.set_volume(0.3)

for som in sons.values():
    som.set_volume(0.4)

# Cobra (pos inicial arena maior)
cobra = [(200, 200)]
direcao = (TAMANHO, 0)

def safe_maca():
    while True:
        x = random.randint(0, (LARGURA // TAMANHO) - 1) * TAMANHO
        y = random.randint(0, (ALTURA // TAMANHO) - 1) * TAMANHO
        pos = (x, y)
        if pos not in cobra:
            return pos

def spatial_beep(cabeca_pos, maca_pos):
    rel_x = maca_pos[0] - cabeca_pos[0]
    rel_y = maca_pos[1] - cabeca_pos[1]
    
    dist = (rel_x**2 + rel_y**2)**0.5
    max_dist = (LARGURA**2 + ALTURA**2)**0.5
    
    # Pitch **MUITO mais agudo** = mais perto (300-2000Hz)
    pitch = max(300, 2000 - int(dist / max_dist * 1700))
    
    # Volume mais alto = mais perto
    vol = max(0.1, 1.0 - dist / max_dist)
    
    # Pan: esquerdo negativo, direito positivo
    pan = rel_x / LARGURA  # -1 to 1
    
    # Gerar áudio MONO primeiro
    sample_rate = 44100
    dur = 0.2  # ligeiramente mais longo
    n_samples = int(sample_rate * dur)
    t = np.linspace(0, dur, n_samples, False)
    onda = np.sin(2 * np.pi * pitch * t)
    audio_mono = (onda * 32767 * vol).astype(np.int16)
    
    # Pan: atenuar canais L/R
    left_gain = max(0.1, 1.0 + pan) / 2
    right_gain = max(0.1, 1.0 - pan) / 2
    left = (audio_mono * left_gain).astype(np.int16)
    right = (audio_mono * right_gain).astype(np.int16)
    audio_pan = np.column_stack((left, right))
    
    som_pan = pygame.sndarray.make_sound(audio_pan)
    
    if not pygame.mixer.get_busy():
        som_pan.play()

def score_beep(score):
    num_beeps = score // 10
    for i in range(min(num_beeps, 5)):  # max 5
        f = 400 + i*100
        som = gerar_som(f, 0.1)
        som.play()
        pygame.time.wait(150)

maca = safe_maca()

# Timer para feedback
feedback_timer = 0

# Welcome startup
print("Snake Acessível iniciado! Use setas. Ouça os beeps!")
for f in [440, 554, 659, 880]:  # melodia simples
    som = gerar_som(f, 0.2)
    som.play()
    pygame.time.wait(250)

rodando = True

while rodando:
    clock.tick(4)  # Velocidade mais lenta
    feedback_timer += 1

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_UP and direcao != (0, TAMANHO):
                direcao = (0, -TAMANHO)
            elif evento.key == pygame.K_DOWN and direcao != (0, -TAMANHO):
                direcao = (0, TAMANHO)
            elif evento.key == pygame.K_LEFT and direcao != (TAMANHO, 0):
                direcao = (-TAMANHO, 0)
            elif evento.key == pygame.K_RIGHT and direcao != (-TAMANHO, 0):
                direcao = (TAMANHO, 0)

    cabeca = cobra[0]
    nova_cabeca = (cabeca[0] + direcao[0], cabeca[1] + direcao[1])

    cobra.insert(0, nova_cabeca)

    comeu = False
    if nova_cabeca == maca:
        score += 10
        maca = safe_maca()
        comeu = True
        sons['eat'].play()
        pygame.time.wait(100)
        sons['grow'].play()
        score_beep(score)
    else:
        cobra.pop()
        
    # Som movimento
    sons['move'].play()

    # 🔊 Feedback auditivo dinâmico (volume por distância no eixo)
    if nova_cabeca[0] == maca[0]:
        dist_x = abs(nova_cabeca[0] - maca[0])  # 0 no alinhado, mas varia? Wait no, alinhado=0
        # Volume maior se próximo no outro eixo quando alinhado X
        dist_y_rel = abs(nova_cabeca[1] - maca[1]) / ALTURA
        vol_x = 0.2 + 0.6 * (1 - dist_y_rel)
        som_x.set_volume(vol_x)
        som_x.play()
    if nova_cabeca[1] == maca[1]:
        dist_x_rel = abs(nova_cabeca[0] - maca[0]) / LARGURA
        vol_y = 0.2 + 0.6 * (1 - dist_x_rel)
        som_y.set_volume(vol_y)
        som_y.play()

    # Warnings
    cabeca_pos = cobra[0]
    
    # Parede próxima (2 segmentos)
    dist_left = cabeca_pos[0] // TAMANHO
    dist_right = (LARGURA - cabeca_pos[0] - TAMANHO) // TAMANHO
    dist_up = cabeca_pos[1] // TAMANHO
    dist_down = (ALTURA - cabeca_pos[1] - TAMANHO) // TAMANHO
    min_dist_parede = min(dist_left, dist_right, dist_up, dist_down)
    if min_dist_parede < 2 and not pygame.mixer.get_busy():
        som_warn = gerar_som(200, 0.3)
        som_warn.play()
    
    # Self próximo (next head close)
    prox_cabeca = (cabeca_pos[0] + direcao[0], cabeca_pos[1] + direcao[1])
    if prox_cabeca in cobra[1:] and not pygame.mixer.get_busy():
        som_self = gerar_som(150, 0.4)
        som_self.play()
    
    # Feedback posição periódico
    if feedback_timer % 40 == 0:  # ~5s
        spatial_beep(cabeca_pos, maca)
    
    # TODAS colisões UNIFICADAS (wall OU self)
    game_over = False
    if (nova_cabeca[0] < 0 or nova_cabeca[0] >= LARGURA or
        nova_cabeca[1] < 0 or nova_cabeca[1] >= ALTURA or
        nova_cabeca in cobra[1:]):
        game_over = True
    
    if game_over:
        print("Game Over! Score:", score, "High:", high_score)
        # Game over alarm
        for f in [800, 700, 600, 500, 400]:
            som = gerar_som(f, 0.3)
            som.play()
            pygame.time.wait(300)
        save_high_score(score)
        
        # Auto-restart com setas
        restart = True
        while restart:
            for ev in pygame.event.get():
                if (ev.type == pygame.KEYDOWN and 
                    ev.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)):
                    rodando = True
                    restart = False
                if ev.type == pygame.QUIT:
                    rodando = False
                    restart = False
            clock.tick(10)
        if not rodando:
            break
        # Reset game
        score = 0
        cobra = [(100, 100)]
        direcao = (TAMANHO, 0)
        maca = safe_maca()
        feedback_timer = 0
        continue

    TELA.fill(PRETO)

    # Score texto
    font = pygame.font.SysFont('arial', 24)
    text_score = font.render(f"Score: {score}", True, (255,255,255))
    text_high = font.render(f"High: {high_score}", True, (255,255,0))
    TELA.blit(text_score, (10,10))
    TELA.blit(text_high, (10,40))

    for segmento in cobra:
        pygame.draw.rect(TELA, VERDE, (*segmento, TAMANHO, TAMANHO))

    pygame.draw.rect(TELA, VERMELHO, (*maca, TAMANHO, TAMANHO))

    pygame.display.update()

pygame.quit()
