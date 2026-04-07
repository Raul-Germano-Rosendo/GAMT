import pygame
import random
import numpy as np
import pickle
import os
import sys

# Constants / Configurações
class Config:
    LARGURA = 600
    ALTURA = 600
    TAMANHO = 20
    FPS_INICIAL = 3
    FPS_MAX = 12
    SCORE_POR_MACA = 10
    VELOCIDADE_AUMENTO = 50  # pontos para aumentar FPS
    FEEDBACK_INTERVALO = 40  # frames
    HIGH_SCORE_FILE = 'high_score.pkl'

    CORES = {
        'PRETO': (0, 0, 0),
        'VERDE': (0, 255, 0),
        'VERMELHO': (255, 0, 0),
        'BRANCO': (255, 255, 255),
        'AMARELO': (255, 255, 0),
        'CINZA': (128, 128, 128)
    }

# Audio Manager / Gerenciador de Áudio
class AudioManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        self.sample_rate = 44100
        self.sounds = {}
        self.preload_basic_sounds()
        self.sound_queue = []  # Para evitar overlap

    def gerar_som(self, frequencia=440, duracao=0.1, volume=0.4):
        n_samples = int(self.sample_rate * duracao)
        t = np.linspace(0, duracao, n_samples, False)
        onda = np.sin(2 * np.pi * frequencia * t)
        audio = (onda * 32767 * volume).astype(np.int16)
        audio_estereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(audio_estereo)

    def preload_basic_sounds(self):
        self.sounds['move'] = self.gerar_som(440, 0.05)
        self.sounds['eat'] = self.gerar_som(660, 0.2)
        self.sounds['grow'] = self.gerar_som(880, 0.3)
        self.sounds['wall_warn'] = self.gerar_som(200, 0.3)
        self.sounds['self_warn'] = self.gerar_som(150, 0.4)
        self.sounds['pause'] = self.gerar_som(1000, 0.5)
        self.sounds['unpause'] = self.gerar_som(800, 0.5)
        self.sounds['som_x'] = self.gerar_som(600)
        self.sounds['som_y'] = self.gerar_som(300)
        self.sounds['corner_left'] = self.gerar_som(180, 0.4, 0.6)  # Grave pan left
        self.sounds['corner_right'] = self.gerar_som(250, 0.4, 0.6)  # Agudo pan right

        # Pre-gerar sons espaciais por distância (otimização)
        self.spatial_sounds = {}
        max_dist = (Config.LARGURA**2 + Config.ALTURA**2)**0.5
        for i in range(11):  # 0-10 levels
            dist_ratio = i / 10
            pitch = max(300, 2000 - int(dist_ratio * 1700))
            vol = max(0.1, 1.0 - dist_ratio)
            self.spatial_sounds[i] = self.gerar_som(pitch, 0.2, vol)

    def play(self, sound_key, pan=0.0):
        if isinstance(sound_key, str):
            if sound_key not in self.sounds and sound_key not in self.spatial_sounds:
                return
            sound = self.sounds.get(sound_key) or self.spatial_sounds.get(sound_key)
        else:
            # sound_key is int for spatial or freq for melody
            if isinstance(sound_key, int):
                sound = self.spatial_sounds.get(sound_key)
            else:
                sound = self.gerar_som(sound_key, 0.2)

        if sound is None:
            return

        # Dynamic pan stereo
        if hasattr(sound, 'set_volume'):
            vol = 0.4
            sound.set_volume(vol)
        sound.play()  # Always play alignment/dynamic sounds

    def queue_play(self, sound_key):
        self.sound_queue.append(sound_key)
        if len(self.sound_queue) == 1:
            self.play_from_queue()

    def play_from_queue(self):
        if self.sound_queue:
            key = self.sound_queue.pop(0)
            self.play(key)
            pygame.time.wait(50)  # Short queue delay

# High Score Manager
class HighScore:
    @staticmethod
    def load():
        try:
            if os.path.exists(Config.HIGH_SCORE_FILE):
                with open(Config.HIGH_SCORE_FILE, 'rb') as f:
                    return pickle.load(f)
        except:
            pass
        return 0

    @staticmethod
    def save(score):
        high = HighScore.load()
        if score > high:
            try:
                with open(Config.HIGH_SCORE_FILE, 'wb') as f:
                    pickle.dump(score, f)
                return True
            except:
                pass
        return False

# Main Game Class / Classe Principal do Jogo
class SnakeGame:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((Config.LARGURA, Config.ALTURA))
        pygame.display.set_caption("Snake Acessível Melhorado")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 24)
        self.big_font = pygame.font.SysFont('arial', 36)

        self.audio = AudioManager()
        self.high_score = HighScore.load()
        self.reset_game()
        self.state = 'menu'  # menu, playing, paused, game_over

    def reset_game(self):
        self.score = 0
        self.cobra = [(200, 200)]
        self.direcao = (Config.TAMANHO, 0)
        self.maca = self.safe_maca()
        self.feedback_timer = 0
        self.fps = Config.FPS_INICIAL
        self.paused = False

    def safe_maca(self):
        while True:
            x = random.randint(0, (Config.LARGURA // Config.TAMANHO) - 1) * Config.TAMANHO
            y = random.randint(0, (Config.ALTURA // Config.TAMANHO) - 1) * Config.TAMANHO
            if (x, y) not in self.cobra:
                return (x, y)

    def get_fps_from_score(self):
        levels = self.score // Config.VELOCIDADE_AUMENTO
        return min(Config.FPS_INICIAL + levels, Config.FPS_MAX)

    def spatial_feedback(self):
        cabeca = self.cobra[0]
        rel_x = self.maca[0] - cabeca[0]
        rel_y = self.maca[1] - cabeca[1]
        dist = (rel_x**2 + rel_y**2)**0.5
        max_dist = (Config.LARGURA**2 + Config.ALTURA**2)**0.5
        dist_level = min(10, int((dist / max_dist) * 10))
        pan = rel_x / Config.LARGURA
        self.audio.play(dist_level, pan)

    def check_warnings(self):
        cabeca = self.cobra[0]
        direcao_next = (cabeca[0] + self.direcao[0], cabeca[1] + self.direcao[1])

        # Parede normal
        dist_left = cabeca[0] // Config.TAMANHO
        dist_right = (Config.LARGURA - cabeca[0] - Config.TAMANHO) // Config.TAMANHO
        dist_up = cabeca[1] // Config.TAMANHO
        dist_down = (Config.ALTURA - cabeca[1] - Config.TAMANHO) // Config.TAMANHO
        if min(dist_left, dist_right, dist_up, dist_down) < 2:
            self.audio.queue_play('wall_warn')

        # Cotovelos/Cantos - 2 lados!
        if dist_left < 2 and (dist_up < 2 or dist_down < 2):  # Esquerdo (canto cima ou baixo)
            self.audio.queue_play('corner_left')
        if dist_right < 2 and (dist_up < 2 or dist_down < 2):  # Direito
            self.audio.queue_play('corner_right')

        # Self collision
        if direcao_next in self.cobra[1:]:
            self.audio.queue_play('self_warn')

    def handle_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_RETURN, pygame.K_SPACE):
                    self.state = 'playing'
                    self.play_startup()
        self.draw_menu()
        return True

    def play_startup(self):
        print("Snake Acessível iniciado! Setas: mover | P: pause | Ouça os beeps!")
        melody = [440, 554, 659, 880, 440]
        for f in melody:
            self.audio.play(f)  # Freq for melody
            pygame.time.wait(250)

    def draw_menu(self):
        self.tela.fill(Config.CORES['PRETO'])
        title = self.big_font.render("Snake Acessível", True, Config.CORES['BRANCO'])
        info = self.font.render("Pressione seta ou SPACE para jogar", True, Config.CORES['AMARELO'])
        high = self.font.render(f"Recorde: {self.high_score}", True, Config.CORES['AMARELO'])
        self.tela.blit(title, (150, 200))
        self.tela.blit(info, (100, 300))
        self.tela.blit(high, (200, 350))
        pygame.display.update()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    key = 'pause' if self.paused else 'unpause'
                    self.audio.queue_play(key)
                elif event.key == pygame.K_UP and self.direcao != (0, Config.TAMANHO):
                    self.direcao = (0, -Config.TAMANHO)
                elif event.key == pygame.K_DOWN and self.direcao != (0, -Config.TAMANHO):
                    self.direcao = (0, Config.TAMANHO)
                elif event.key == pygame.K_LEFT and self.direcao != (Config.TAMANHO, 0):
                    self.direcao = (-Config.TAMANHO, 0)
                elif event.key == pygame.K_RIGHT and self.direcao != (-Config.TAMANHO, 0):
                    self.direcao = (Config.TAMANHO, 0)
        return True

    def update_game(self):
        self.feedback_timer += 1
        cabeca = self.cobra[0]
        nova_cabeca = (cabeca[0] + self.direcao[0], cabeca[1] + self.direcao[1])
        self.cobra.insert(0, nova_cabeca)

        if nova_cabeca == self.maca:
            self.score += Config.SCORE_POR_MACA
            self.maca = self.safe_maca()
            self.audio.queue_play('eat')
            pygame.time.wait(50)  # Short pause
            self.audio.queue_play('grow')
            self.score_beep()
        else:
            self.cobra.pop()

        self.audio.queue_play('move')
        
        self.check_warnings()
        if self.feedback_timer % Config.FEEDBACK_INTERVALO == 0:
            self.spatial_feedback()

        # Collision
        if (nova_cabeca[0] < 0 or nova_cabeca[0] >= Config.LARGURA or
            nova_cabeca[1] < 0 or nova_cabeca[1] >= Config.ALTURA or
            nova_cabeca in self.cobra[1:]):
            self.state = 'game_over'

        self.fps = self.get_fps_from_score()

    def score_beep(self):
        num_beeps = min(self.score // 10, 5)
        for i in range(num_beeps):
            f = 400 + i * 100
            self.audio.play(f)
            pygame.time.wait(100)

    def draw_game(self):
        self.tela.fill(Config.CORES['PRETO'])

        # Grid sutil
        for x in range(0, Config.LARGURA, Config.TAMANHO):
            pygame.draw.line(self.tela, Config.CORES['CINZA'], (x, 0), (x, Config.ALTURA))
        for y in range(0, Config.ALTURA, Config.TAMANHO):
            pygame.draw.line(self.tela, Config.CORES['CINZA'], (0, y), (Config.LARGURA, y))

        # Score
        text_score = self.font.render(f"Score: {self.score}", True, Config.CORES['BRANCO'])
        text_high = self.font.render(f"High: {self.high_score}", True, Config.CORES['AMARELO'])
        text_fps = self.font.render(f"FPS: {self.fps}", True, Config.CORES['BRANCO'])
        text_pause = self.font.render("PAUSADO (P para continuar)" if self.paused else "P: Pause", True, Config.CORES['BRANCO'])
        self.tela.blit(text_score, (10, 10))
        self.tela.blit(text_high, (10, 40))
        self.tela.blit(text_fps, (10, 70))
        self.tela.blit(text_pause, (10, Config.ALTURA - 30))

        # Cobra e maçã
        for i, segmento in enumerate(self.cobra):
            alpha = 255 - (i * 5)  # Fade tail
            color = (*Config.CORES['VERDE'][:3], alpha)
            # Approximate fade with darker green
            dark_green = (0, max(50, 255 - i*10), 0)
            pygame.draw.rect(self.tela, dark_green, (*segmento, Config.TAMANHO, Config.TAMANHO))
        pygame.draw.rect(self.tela, Config.CORES['VERMELHO'], (*self.maca, Config.TAMANHO, Config.TAMANHO))

        pygame.display.update()

    def handle_game_over(self):
        HighScore.save(self.score)
        self.high_score = HighScore.load()
        # Game over sound
        for f in [800, 700, 600, 500, 400]:
            self.audio.play(f)
            pygame.time.wait(300)
        print(f"Game Over! Score: {self.score} High: {self.high_score}")
        self.state = 'menu'
        self.reset_game()

    def run(self):
        running = True
        while running:
            self.clock.tick(self.fps if not self.paused else 10)

            if self.state == 'menu':
                running = self.handle_menu()
            elif self.state == 'playing':
                if self.handle_input():
                    if not self.paused:
                        self.update_game()
                    self.draw_game()
                else:
                    running = False
            elif self.state == 'game_over':
                self.handle_game_over()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    try:
        game = SnakeGame()
        game.run()
    except Exception as e:
        print(f"Erro: {e}")
        pygame.quit()

