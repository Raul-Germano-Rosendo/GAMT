# PLANO DE AULAS
# Workshop Desenvolvimento Criativo de Jogos Digitais com Roblox Studio

## Metodologia STEAM - GAMT Lab

---

# Visão Geral da Metodologia

O workshop será desenvolvido utilizando uma abordagem baseada em:

## Criar → Testar → Errar → Melhorar → Inovar

O professor atua como **mentor e facilitador**, apresentando ferramentas, conceitos e desafios.

O objetivo não é fazer com que os alunos copiem um jogo pronto.

A proposta é que cada participante desenvolva sua própria experiência digital, criando soluções próprias, explorando ideias e aplicando conceitos de programação, design e tecnologia.

---

# Estrutura das Aulas

Cada encontro seguirá:

1. Exploração do conceito
2. Demonstração prática
3. Desafio criativo
4. Desenvolvimento individual
5. Testes
6. Apresentação das soluções
7. Melhorias

---

# DIA 1
# Ideação + Introdução ao Roblox Studio

## Objetivo

Apresentar o processo de criação de jogos digitais e transformar os alunos de jogadores em criadores.

---

# Momento 1 - Mentalidade de Criador

## Perguntas iniciais

Professor pergunta:

> Quem aqui já jogou Roblox?

Depois:

> Quem aqui já criou um jogo?

Explicar:

Um jogo não nasce pronto.

O processo envolve:


IDEIA
↓
PLANEJAMENTO
↓
DESIGN
↓
CONSTRUÇÃO
↓
PROGRAMAÇÃO
↓
TESTE
↓
PUBLICAÇÃO


---

# Atividade STEAM

Criar o conceito inicial do jogo.

Cada aluno define:

## Nome do jogo

Exemplo:

Escape da Ilha Perdida

## Objetivo

Chegar ao final superando desafios.

## Elementos

- Fases
- Obstáculos
- Recompensas
- Mecânicas

---

# Introdução ao Roblox Studio

Apresentar:

## Workspace

Local onde os objetos existem.

Exemplo:


Workspace

├── Part
├── SpawnLocation
└── Camera


---

## Explorer

Explicar:

É a estrutura do projeto.

---

## Properties

Mostrar:

- Position
- Size
- Color
- Material

Explicação:

"Todo objeto possui características que podem ser modificadas."

---

# Desafio

Criar:


INÍCIO

[PLATAFORMA]

 |

[OBSTÁCULO]

 |

FINAL


---

<br>

# DIA 2
# Construção de Mundos Digitais

## Objetivo

Criar ambientes e compreender conceitos de design e engenharia.

---

# Conteúdo

## Parts

Explicar:

Parts são blocos básicos de construção.

Tipos:

- Block
- Sphere
- Cylinder

---

# Mecânica 1
# Plataforma que cai

Criar uma peça:

Nome:


FallingPlatform


Script:

```lua
local part = script.Parent

wait(3)

part.Anchored = false

Explicação:

Após 3 segundos a plataforma deixa de estar fixa.

Mecânica 2
Lava (Kill Brick)

Criar uma peça vermelha.

Adicionar:

local lava = script.Parent


lava.Touched:Connect(function(hit)

local humanoid = hit.Parent:FindFirstChild("Humanoid")


if humanoid then

humanoid.Health = 0

end

end)
Explicação do Script
Jogador toca objeto

        ↓

Evento Touched ativa

        ↓

Verifica Humanoid

        ↓

Remove vida
Desafio Criativo

Cada aluno cria:

Lava
Labirinto
Plataforma móvel
Área secreta
<br>
DIA 3
Programação Lua e Mecânicas
Objetivo

Mostrar como códigos controlam comportamentos dentro do jogo.

Introdução a Scripts

Explicar:

Script é uma sequência de instruções.

Exemplo:

print("Olá mundo")

Resultado:

Olá mundo
Variáveis

Guardar informações.

Exemplo:

local moedas = 0
Condições

Tomada de decisão:

if moedas >= 10 then

print("Você venceu!")

end
Criando uma moeda

Criar:

Part

Nome:

Coin

Script:

local moeda = script.Parent


moeda.Touched:Connect(function(hit)

local humanoid = hit.Parent:FindFirstChild("Humanoid")


if humanoid then

moeda.Transparency = 1

moeda.CanCollide = false

end

end)
Criando Pontuação

Sistema:

Jogador

  ↓

Coleta moeda

  ↓

Aumenta contador

Script:

game.Players.PlayerAdded:Connect(function(player)


local leaderstats = Instance.new("Folder")

leaderstats.Name = "leaderstats"

leaderstats.Parent = player



local coins = Instance.new("IntValue")

coins.Name = "Coins"

coins.Value = 0

coins.Parent = leaderstats


end)
<br>
DIA 4
Projeto Final e Apresentação
Objetivo

Aplicar todo conhecimento em um projeto autoral.

Planejamento Final

Cada aluno responde:

Nome do jogo
Objetivo
Público
Mecânica principal

Exemplo:

"Um jogo onde o jogador precisa escapar de uma cidade abandonada."

Mecânicas Disponíveis
Teleporte
local destino = workspace.TeleportPart


script.Parent.Touched:Connect(function(hit)

hit.Parent.HumanoidRootPart.Position = destino.Position

end)
Porta Abrindo
local porta = script.Parent


porta.Touched:Connect(function()

porta.Transparency = 1

porta.CanCollide = false

end)
Plataforma Móvel
local plataforma = script.Parent


while true do

plataforma.Position += Vector3.new(0,0,1)

wait(1)

end
Sistema de Vitória
script.Parent.Touched:Connect(function(hit)

local player = hit.Parent

print(player.Name.." venceu!")

end)
Apresentação Final

Cada participante apresenta:

Ideia do jogo
Construção realizada
Código utilizado
Problemas encontrados
Soluções criadas
Avaliação

O foco não será:

"Quem fez o jogo mais bonito"

O foco será:

Criatividade
Tentativa
Resolução de problemas
Aplicação dos conceitos
Capacidade de explicar sua criação
Resultado Esperado

Ao final do workshop o aluno terá:

✅ Um jogo próprio

✅ Um ambiente criado por ele

✅ Mecânicas programadas

✅ Noção inicial de desenvolvimento

✅ Experiência com pensamento computacional

✅ Capacidade de criar soluções digitais

Papel do Professor

O professor não é um "executor de passo a passo".

O professor é um facilitador que:

Apresenta ferramentas
Propõe desafios
Incentiva experimentação
Auxilia soluções
Estimula criatividade

O objetivo final é formar criadores de tecnologia, não apenas usuários.