import pygame
import random
import numpy as np
import pickle
import os
import sys
import math

# Constants / Configurações (igual Snake.py + radiais)
class Config:
    LARGURA = 600
    ALTURA = 600
    TAMANHO = 20
    FPS_INICIAL = 4
    FPS_MAX = 12
    SCORE_POR_MACA = 10
    VELOCIDADE_AUMENTO = 50
    FEEDBACK_INTERVALO = 40
    HIGH_SCORE_FILE = 'high_score_radial.pkl'  # Novo high score

    CORES = {
        'PRETO': (0, 0, 0),
        'VERDE': (0, 255, 0),
        'VERMELHO': (255, 0, 0),
        'BRANCO': (255, 255, 255),
        'AMARELO': (255, 255, 0),
        'CINZA': (128, 128, 128),
        'AZUL': (0, 100, 255)  # Destaque radial
    }

    # Radial Config
    RADIAL_SECTORS = 8  # 45° cada
    DOPPLER_FACTOR = 0.2
    HEARTBEAT_BASE_HZ = 2  # Pulsações/seg perto

# Radial Audio Manager (herda e expande)
class RadialAudioManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2)
        self.sample_rate = 44100
        self.sounds = {}
        self.sector_sounds = {}
        self.preload_sounds()
        self.last_heartbeat = 0

    def gerar_som(self, frequencia=440, duracao=0.1, volume=0.4):
        n_samples = int(self.sample_rate * duracao)
        t = np.linspace(0, duracao, n_samples, False)
        onda = np.sin(2 * np.pi * frequencia * t)
        audio = (onda * 32767 * volume).astype(np.int16)
        audio_estereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(audio_estereo)

    def preload_sounds(self):
        # Sons básicos herdados
        basic = ['move', 'eat', 'grow', 'wall_warn', 'self_warn', 'pause', 'unpause']
        for key, freq, dur in [
            ('move', 440, 0.05), ('eat', 660, 0.2), ('grow', 880, 0.3),
            ('wall_warn', 200, 0.3), ('self_warn', 150, 0.4),
            ('pause', 1000, 0.5), ('unpause', 800, 0.5)
        ]:
            self.sounds[key] = self.gerar_som(freq, dur)

        # 8 setores radiais (360°): pitch varia por direção relativa à cobra
        sector_pitches = [800, 900, 1000, 1100, 1000, 900, 600, 500]  # Direita alta → esquerda grave
        for i in range(Config.RADIAL_SECTORS):
            name = f'radial_{i}'
            self.sector_sounds[i] = self.gerar_som(sector_pitches[i], 0.25, 0.6)

    def calculate_radial_params(self, head, apple, direction):
        rel_x = apple[0] - head[0]
        rel_y = apple[1] - head[1]
        dist = math.sqrt(rel_x**2 + rel_y**2)
        max_dist = math.sqrt(Config.LARGURA**2 + Config.ALTURA**2)
        dist_norm = dist / max_dist

        # Ângulo relativo à direção da cobra (0° = frente)
        angle = math.degrees(math.atan2(rel_y, rel_x))
        dir_angle = math.degrees(math.atan2(direction[1], direction[0]))
        rel_angle = (angle - dir_angle + 360) % 360

        # Setor: 0-45°=0, 45-90°=1, etc.
        sector = int(rel_angle // (580 / Config.RADIAL_SECTORS))

        # Doppler: approach_speed (projeção vetor velocidade na direção maçã)
        vel_norm = math.sqrt(direction[0]**2 + direction[1]**2)
        if dist > 0:
            unit_to_apple = (rel_x/dist, rel_y/dist)
            approach = abs(direction[0] * unit_to_apple[0] + direction[1] * unit_to_apple[1]) / vel_norm
        else:
            approach = 0
        doppler_mult = 1 + (approach * Config.DOPPLER_FACTOR)

        # Vol DRÁSTICO: explode perto
        vol = max(0.01, (1 - dist_norm)**3)

        # Pitch DIST drástico LOG: 200Hz longe → 3000Hz perto
        pitch_dist = 200 + 2800 * (1 - dist_norm**0.3)

        # Pan avançado: coseno do angle
        pan = math.cos(math.radians(rel_angle - 180))  # -1 left, +1 right

        return {
            'dist': dist_norm, 'sector': sector, 'rel_angle': rel_angle,
            'doppler_mult': doppler_mult, 'vol': vol, 'pan': pan,
            'pitch_dist': pitch_dist
        }
    
    def play_radial(self, params):
        # Gerar som DINÂMICO com pitch_dist + harmônicos drásticos
        pitch = params['pitch_dist'] * params['doppler_mult']
        dur = 0.15 + (1 - params['dist']) * 0.1  # Mais longo perto
        noise_level = max(0, (1 - params['dist']) * 0.4)  # Ruído alto perto

        n_samples = int(self.sample_rate * dur)
        t = np.linspace(0, dur, n_samples, False)
        
        # Onda complexa: fundamental + 3ª harmônica + noise
        fundamental = np.sin(2 * np.pi * pitch * t)
        harmonic3 = 0.4 * np.sin(2 * np.pi * 3 * pitch * t)
        noise = noise_level * np.random.normal(0, 0.3, n_samples)
        onda = fundamental + harmonic3 + noise
        onda = np.clip(onda, -1, 1)
        
        audio = (onda * 32767 * params['vol']).astype(np.int16)
        
        # Pan: left/right channels
        left_gain = max(0.05, 0.5 * (1 - params['pan']))
        right_gain = max(0.05, 0.5 * (1 + params['pan']))
        left = (audio * left_gain).astype(np.int16)
        right = (audio * right_gain).astype(np.int16)
        audio_pan = np.column_stack((left, right))
        
        radial_sound = pygame.sndarray.make_sound(audio_pan)
        radial_sound.play()

    def play_heartbeat(self, dist_norm):
        now = pygame.time.get_ticks()
        hz = 0.5 + 12 * (1 - dist_norm)**2  # 0.5 longe → 12.5 perto TURBO
        interval = max(50, 1000 / hz)  # Min 50ms
        if now - self.last_heartbeat > interval:
            low_freq = 80 + (1 - dist_norm) * 200  # 80→280Hz
            vol_hb = (1 - dist_norm)**2 * 0.5
            hb_sound = self.gerar_som(low_freq, 0.08, vol_hb)
            hb_sound.play()
            self.last_heartbeat = now

    def play(self, sound_key, params=None):
        if sound_key in self.sounds:
            self.sounds[sound_key].play()
        elif params:
            self.play_radial(params)
            self.play_heartbeat(params['dist'])

# HighScore (mesmo)
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

# Main Game (adaptado)
class SnakeRadialGame:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((Config.LARGURA, Config.ALTURA))
        pygame.display.set_caption("Snake RADIAL Audio")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('arial', 24)
        self.big_font = pygame.font.SysFont('arial', 36)

        self.audio = RadialAudioManager()
        self.high_score = HighScore.load()
        self.reset_game()
        self.state = 'menu'

    def reset_game(self):
        self.score = 0
        self.cobra = [(200, 200)]
        self.direcao = (Config.TAMANHO, 0)
        self.maca = self.safe_maca()
        self.feedback_timer = 0
        self.fps = Config.FPS_INICIAL
        self.paused = False
        print("Snake RADIAL iniciado! Sons 360° + Doppler!")

    def safe_maca(self):
        while True:
            x = random.randint(0, (Config.LARGURA // Config.TAMANHO) - 1) * Config.TAMANHO
            y = random.randint(0, (Config.ALTURA // Config.TAMANHO) - 1) * Config.TAMANHO
            if (x, y) not in self.cobra:
                return (x, y)

    def get_fps_from_score(self):
        levels = self.score // Config.VELOCIDADE_AUMENTO
        return min(Config.FPS_INICIAL + levels, Config.FPS_MAX)

    def update_radial_audio(self):
        head = self.cobra[0]
        params = self.audio.calculate_radial_params(head, self.maca, self.direcao)
        
        # Rate drástico: play mais rápido perto (min 1 frame)
        play_rate = max(1, int(params['dist'] * 8) + 1)
        if self.feedback_timer % play_rate == 0:
            self.audio.play('radial', params)
        
        # Heartbeat sempre
        self.audio.play_heartbeat(params['dist'])
        
        # Debug otimizado
        if self.feedback_timer % 20 == 0:
            pitch = params['pitch_dist'] * params['doppler_mult']
            print(f"Radial: D{params['dist']:.2f} P{int(pitch)}Hz V{params['vol']:.2f} A{params['rel_angle']:.0f}° S{params['sector']}")


    def check_warnings(self):
        # Igual original
        head = self.cobra[0]
        direcao_next = (head[0] + self.direcao[0], head[1] + self.direcao[1])
        dist_left = head[0] // Config.TAMANHO
        dist_right = (Config.LARGURA - head[0] - Config.TAMANHO) // Config.TAMANHO
        dist_up = head[1] // Config.TAMANHO
        dist_down = (Config.ALTURA - head[1] - Config.TAMANHO) // Config.TAMANHO
        if min(dist_left, dist_right, dist_up, dist_down) < 2:
            self.audio.play('wall_warn')
        if direcao_next in self.cobra[1:]:
            self.audio.play('self_warn')

    # Demais métodos iguais a Snake.py (handle_menu, handle_input, update_game, draw_game, etc.)
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
        melody = [440, 554, 659, 880, 660]  # + radial touch
        for f in melody:
            sound = self.audio.gerar_som(f, 0.2)
            sound.play()
            pygame.time.wait(250)

    def draw_menu(self):
        self.tela.fill(Config.CORES['PRETO'])
        title = self.big_font.render("Snake RADIAL Audio", True, Config.CORES['AZUL'])
        info = self.font.render("Setas: mover | P: pause | Sons 360°!", True, Config.CORES['AMARELO'])
        high = self.font.render(f"High: {self.high_score}", True, Config.CORES['AMARELO'])
        self.tela.blit(title, (100, 200))
        self.tela.blit(info, (80, 300))
        self.tela.blit(high, (200, 350))
        pygame.display.update()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.paused = not self.paused
                    self.audio.play('pause' if self.paused else 'unpause')
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
        head = self.cobra[0]
        nova_cabeca = (head[0] + self.direcao[0], head[1] + self.direcao[1])
        self.cobra.insert(0, nova_cabeca)

        if nova_cabeca == self.maca:
            self.score += Config.SCORE_POR_MACA
            self.maca = self.safe_maca()
            self.audio.play('eat')
            pygame.time.wait(50)
            self.audio.play('grow')
        else:
            self.cobra.pop()

        self.audio.play('move')
        self.update_radial_audio()  # NOVO: Todo frame!
        self.check_warnings()

        if (nova_cabeca[0] < 0 or nova_cabeca[0] >= Config.LARGURA or
            nova_cabeca[1] < 0 or nova_cabeca[1] >= Config.ALTURA or
            nova_cabeca in self.cobra[1:]):
            self.state = 'game_over'

        self.fps = self.get_fps_from_score()

    def draw_game(self):
        self.tela.fill(Config.CORES['PRETO'])
        # Grid
        for x in range(0, Config.LARGURA, Config.TAMANHO):
            pygame.draw.line(self.tela, Config.CORES['CINZA'], (x, 0), (x, Config.ALTURA))
        for y in range(0, Config.ALTURA, Config.TAMANHO):
            pygame.draw.line(self.tela, Config.CORES['CINZA'], (0, y), (Config.LARGURA, y))

        # UI
        text_score = self.font.render(f"Score: {self.score}", True, Config.CORES['BRANCO'])
        text_high = self.font.render(f"High: {self.high_score}", True, Config.CORES['AMARELO'])
        text_fps = self.font.render(f"FPS: {self.fps}", True, Config.CORES['BRANCO'])
        self.tela.blit(text_score, (10, 10))
        self.tela.blit(text_high, (10, 40))
        self.tela.blit(text_fps, (10, 70))

        # Cobra e maçã (azul highlight)
        for i, seg in enumerate(self.cobra):
            dark_green = (0, max(50, 255 - i*10), 0)
            pygame.draw.rect(self.tela, dark_green, (*seg, Config.TAMANHO, Config.TAMANHO))
        pygame.draw.rect(self.tela, Config.CORES['VERMELHO'], (*self.maca, Config.TAMANHO, Config.TAMANHO))

        pygame.display.update()

    def handle_game_over(self):
        HighScore.save(self.score)
        self.high_score = HighScore.load()
        for f in [800, 700, 600, 500, 400]:
            sound = self.audio.gerar_som(f, 0.3)
            sound.play()
            pygame.time.wait(300)
        print(f"Game Over Radial! Score: {self.score}")
        self.state = 'menu'
        self.reset_game()

    def get_fps_from_score(self):
        return min(Config.FPS_INICIAL + (self.score // Config.VELOCIDADE_AUMENTO), Config.FPS_MAX)

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
        game = SnakeRadialGame()
        game.run()
    except Exception as e:
        print(f"Erro Radial: {e}")
        pygame.quit()

