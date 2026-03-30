# SnakeGame Acessível & Radial

## 🎮 Snake.py (Versão Base)
Arena 600x600. Sons espaciais, alinhamento X/Y, warnings.

**Rodar:** `python Snake.py`  
**High:** `high_score.pkl`

## 🌐 SnakeRadial.py (Nova Versão RADIAL!)
**Som 360° avançado:**
- **8 setores angulares** (45°): Tons únicos por direção (frente/detrás/lados).
- **Doppler**: Pitch sobe se aproximando!
- **Volume radial**: Alto perto (1/dist^1.5).
- **Pan 3D**: Coseno do ângulo.
- **Heartbeat**: Pulsa rápido perto da maçã.
- Update **todo frame** + debug console (dist/ângulo).

**Radar:** `python SnakeRadial.py`  
**High:** `high_score_radial.pkl`  
**Debug:** Console mostra dist/ângulo/setor.

**Sons Base (ambos):**
- Startup melodia, move/eat/grow, walls/self warns, pause(P).

**Controles:** Setas mover, P pause. Feche olhos—sinta o radial! 🎧

## 🚀 Setup
```
pip install pygame numpy
```

**Aula:** Veja `Aula_SnakeGame_Criancas.md` pros passos lógicos! 🐍✨
