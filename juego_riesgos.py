import pygame
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog
import time
import os  # Importamos os para manejar rutas
import random  # Importamos random para el movimiento de los fantasmas

# Inicializar Tkinter antes de Pygame
root = tk.Tk()
root.withdraw()  # Ocultar la ventana raíz
root.attributes('-topmost', True)  # Siempre en primer plano

# Inicializar Pygame
pygame.init()
pygame.mixer.init()  # Inicializar el módulo de audio de Pygame

# Configuración de colores
WHITE = (200, 200, 200)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)    # Inicio y estaciones
RED = (200, 0, 0)      # Final
BLUE = (0, 0, 255)     # Paredes
YELLOW = (255, 255, 0) # Jugador

# Colores para los fantasmas
GHOST_COLORS = [
    (255, 0, 0),        # Rojo
    (255, 184, 255),    # Rosa
    (0, 255, 255),      # Cian
    (255, 184, 82)      # Naranja
]

# Configuración del laberinto
CELL_SIZE = 20.4  # Tamaño de cada celda en píxeles
# Laberinto
additional_columns = "1" * 0  # Columnas adicionales al final de cada fila
maze = [
    "1111111111111111111111111111111111111111111111111111111111111111" + additional_columns,
    "1S00000000000000000000000000000000000000000000000000000000000001" + additional_columns,
    "1011101110111010111011011101110111011101011101110111101110111011" + additional_columns,
    "1000001000000000000000010000000010001000000000010000000010000001" + additional_columns,
    "1110111111101111101111011111101011101011111101011111111010111101" + additional_columns,
    "1000001000000000000000000000000000000000000000000000000000000001" + additional_columns,
    "1011101111111011111111111011111011011101111011111011111111111011" + additional_columns,
    "1000001000000000000000000000100000001000000000100000000000000001" + additional_columns,
    "1110111010111111011101111010111111011101111111111011101111101011" + additional_columns,
    "1000101010000001000100000000000000000000000000001000100000000001" + additional_columns,
    "1011111011111111011111111111111011111011111111111011111111101111" + additional_columns,
    "1000000000000000000000000000000000000000000000000000000000000001" + additional_columns,
    "1111111111111111111111011111101111101111011111011111101111101111" + additional_columns,
    "1000000000000000100000010000000000001000000000100000000000000001" + additional_columns,
    "1011101111011111011111011111011110111011111111011111011101111011" + additional_columns,
    "10000000000000000000000000000000000000000000000000000000000000F1" + additional_columns,
    "1111111111111111111111111111111111111111111111111111111111111111" + additional_columns
]

# Dimensiones del laberinto
ROWS = len(maze)
COLS = len(maze[0])

# Ajustar el tamaño de la ventana según el laberinto
WIDTH = int(COLS * CELL_SIZE)
HEIGHT = int(ROWS * CELL_SIZE)

# Configuración de la ventana
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laberinto de Riesgos - Desafío Extremo")

# Configuración del jugador
player_pos = None  # Se inicializará al encontrar 'S' en el laberinto
start_pos = None   # Variable para guardar la posición inicial del jugador
player_speed = CELL_SIZE / 5  # Usar float para mayor precisión
score = 0
stations = []
start_time = time.time()
player_direction = 'RIGHT'

# Variables para manejar colisiones y elementos
walls = []
finish_rect = None

# Función para obtener la ruta del recurso
def resource_path(relative_path):
    """ Obtiene la ruta absoluta del recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Rutas de los sonidos actualizadas
intro_music = resource_path("pacman-music.mp3")
background_music = resource_path("pacman-waka-waka.mp3")
collision_sound_path = resource_path("pacman-dies.mp3")

# Cargar sonidos
pygame.mixer.music.load(intro_music)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play()

# Cargar sonido de colisión
collision_sound = pygame.mixer.Sound(collision_sound_path)

# Estaciones y preguntas actualizadas con posiciones accesibles
station_questions = [
    {
        "pos": (10, 1),
        "question": "Estación 1: Introducción a la gestión de riesgos\n\n"
                    "Caso: Un director de proyecto en la UNAL está formulando su plan de riesgos y necesita comprender los conceptos básicos.\n\n"
                    "¿Cuál es el objetivo principal de la gestión de riesgos en proyectos de la UNAL?",
        "options": [
            "A. Identificar, analizar y mitigar las amenazas que puedan afectar el cumplimiento de los objetivos, entregables, metas y actividades de los proyectos.",
            "B. Evitar por completo cualquier riesgo en el proyecto.",
            "C. Asegurar financiamiento para proyectos de extensión.",
            "D. Solo cumplir con los requisitos normativos."
        ],
        "correct": "A",
        "points": 10
    },
    {
        "pos": (20, 3),
        "question": "Estación 2: Identificación del riesgo\n\n"
                    "Caso: Un equipo de extensión ha identificado que el retraso en la entrega de insumos podría impactar la calidad del proyecto.\n\n"
                    "¿Qué componente del proyecto está en riesgo si ocurre este retraso?",
        "options": [
            "A. Objetivos.",
            "B. Recursos.",
            "C. Metas y entregables.",
            "D. Todos los anteriores."
        ],
        "correct": "D",
        "points": 15
    },
    {
        "pos": (30, 5),
        "question": "Estación 3: Extensión e impacto social\n\n"
                    "Caso: Una comunidad rural víctima de conflicto armado solicita a la UNAL apoyo técnico para mejorar la producción agrícola sostenible.\n\n"
                    "¿Qué modalidad de extensión es más adecuada para este caso?",
        "options": [
            "A. Innovación y gestión tecnológica.",
            "B. Educación continua y permanente.",
            "C. Extensión solidaria.",
            "D. Proyectos de investigación aplicada."
        ],
        "correct": "C",
        "points": 20
    },
    {
        "pos": (40, 7),
        "question": "Estación 4: Análisis del riesgo\n\n"
                    "Caso: En un proyecto de educación continua, se identificó una alta probabilidad de cancelación por falta de inscripciones.\n\n"
                    "¿Qué parámetro se debe evaluar primero en este caso?",
        "options": [
            "A. Probabilidad del evento.",
            "B. Impacto en los objetivos.",
            "C. Riesgo residual.",
            "D. Eficiencia del control."
        ],
        "correct": "A",
        "points": 20
    },
    {
        "pos": (50, 9),
        "question": "Estación 5: Conceptos en la gestión de riesgos\n\n"
                    "Caso: De acuerdo con el marco integral para la gestión de riesgo de la UNAL.\n\n"
                    "¿Qué es el nivel de aceptabilidad?",
        "options": [
            "A. La probabilidad máxima de ocurrencia de un riesgo dentro de un proyecto.",
            "B. La evaluación de la frecuencia con la que un riesgo puede presentarse en un periodo determinado.",
            "C. El impacto máximo permitido de un riesgo sobre los objetivos del proyecto.",
            "D. Nivel de gravedad obtenido al operar o ubicar en el mapa de calor el nivel de riesgo"
        ],
        "correct": "D",
        "points": 15
    },
    {
        "pos": (15, 11),
        "question": "Estación 6: Propiedad intelectual\n\n"
                    "Caso: Un docente de la UNAL desarrolló una tecnología innovadora en un proyecto de extensión y quiere protegerla.\n\n"
                    "¿Qué mecanismo es más adecuado para proteger la innovación?",
        "options": [
            "A. Publicarla en un artículo académico.",
            "B. Solicitar una patente.",
            "C. Registrar la tecnología como 'proyecto terminado'.",
            "D. Licenciar el uso inmediato a una empresa privada."
        ],
        "correct": "B",
        "points": 30
    },
    {
        "pos": (25, 13),
        "question": "Estación 7: Evaluación del riesgo\n\n"
                    "Caso: En un proyecto de regalías, se aplica un control que reduce el impacto del riesgo identificado. Ahora el equipo quiere medir su eficacia.\n\n"
                    "¿Qué etapa debe realizar el equipo para valorar el riesgo después del control?",
        "options": [
            "A. Identificación del riesgo inherente.",
            "B. Análisis del riesgo residual.",
            "C. Definición de indicadores.",
            "D. Revisión de la probabilidad inicial."
        ],
        "correct": "B",
        "points": 35
    },
    {
        "pos": (35, 15),
        "question": "Estación 8: Educación continua\n\n"
                    "Caso: Un estudiante necesita actualizar sus conocimientos en formulación de proyectos. Decide inscribirse en un curso ofrecido por la UNAL.\n\n"
                    "¿Qué submodalidad de educación continua sería más adecuada?",
        "options": [
            "A. Diplomado.",
            "B. Curso de actualización.",
            "C. Evento temático.",
            "D. Seminario especializado."
        ],
        "correct": "B",
        "points": 10
    },
    {
        "pos": (45, 11),
        "question": "Estación 9: Extensión y búsqueda de oportunidades\n\n"
                    "Caso: Un docente está formulando un proyecto de licitación que encontró como resultado de la búsqueda de oportunidades en SECOP II.\n\n"
                    "¿Cuál de los siguientes pasos es fundamental en la formulación y aval de este proyecto?",
        "options": [
            "A. Apertura del proyecto en Quipu.",
            "B. Seguimiento a los riesgos.",
            "C. Solicitar la ficha financiera del proyecto.",
            "D. Solicitar autorización de la Dirección Nacional de Extensión, Innovación y Propiedad Intelectual."
        ],
        "correct": "D",
        "points": 30
    },
    {
        "pos": (55, 11),
        "question": "Estación 10: Finalización del proyecto\n\n"
                    "Caso: Un proyecto interdisciplinario ha alcanzado sus objetivos y está listo para cerrarse. El director del proyecto desea garantizar el cumplimiento normativo.\n\n"
                    "¿Qué etapa es crítica para cerrar correctamente un proyecto en la UNAL?",
        "options": [
            "A. Evaluación de controles.",
            "B. Comunicación y consulta.",
            "C. Liquidación del proyecto.",
            "D. Revisión del presupuesto final."
        ],
        "correct": "C",
        "points": 20
    }
]

# Variables para la animación de la boca
mouth_timer = 0
mouth_timer_limit = 15  # Ajusta este valor para cambiar la velocidad (un número mayor es más lento)
mouth_open = True  # Estado inicial de la boca del jugador

# Lista y colores para los fantasmas
ghosts = []

# Clase Ghost
class Ghost:
    def __init__(self, x, y, color, initial_direction):
        self.x = x * CELL_SIZE
        self.y = y * CELL_SIZE
        self.color = color
        self.direction = initial_direction
        self.speed = CELL_SIZE / 10  # Velocidad en píxeles por frame
        self.rect = pygame.Rect(int(self.x), int(self.y), int(CELL_SIZE), int(CELL_SIZE))

    def move(self):
        directions = ['LEFT', 'RIGHT', 'UP', 'DOWN']
        dx, dy = 0, 0
        if self.direction == 'LEFT':
            dx = -self.speed
        elif self.direction == 'RIGHT':
            dx = self.speed
        elif self.direction == 'UP':
            dy = -self.speed
        elif self.direction == 'DOWN':
            dy = self.speed

        new_x = self.x + dx
        new_y = self.y + dy
        new_rect = pygame.Rect(int(new_x), int(new_y), int(CELL_SIZE), int(CELL_SIZE))

        if not any(new_rect.colliderect(wall) for wall in walls):
            self.x = new_x
            self.y = new_y
            self.rect.topleft = (int(self.x), int(self.y))
        else:
            # Cambia de dirección aleatoriamente al chocar con una pared
            self.direction = random.choice(directions)

    def draw(self):
        # Dibujar el cuerpo del fantasma
        body_rect = pygame.Rect(int(self.x), int(self.y + CELL_SIZE / 4), int(CELL_SIZE), int(3 * CELL_SIZE / 4))
        pygame.draw.rect(window, self.color, body_rect)
        # Dibujar la cabeza del fantasma
        pygame.draw.circle(window, self.color, (int(self.x + CELL_SIZE / 2), int(self.y + CELL_SIZE / 2)), int(CELL_SIZE / 2))
        # Dibujar los ojos del fantasma
        eye_radius = int(CELL_SIZE / 10)
        eye_offset_x = int(CELL_SIZE / 5)
        eye_offset_y = int(CELL_SIZE / 5)
        pygame.draw.circle(window, WHITE, (int(self.x + CELL_SIZE / 2 - eye_offset_x), int(self.y + CELL_SIZE / 2 - eye_offset_y)), eye_radius)
        pygame.draw.circle(window, WHITE, (int(self.x + CELL_SIZE / 2 + eye_offset_x), int(self.y + CELL_SIZE / 2 - eye_offset_y)), eye_radius)

# Dibuja al jugador estilo Pac-Man con dirección
def draw_player():
    x, y = player_pos
    half_cell = CELL_SIZE / 2
    center = (int(x + half_cell), int(y + half_cell))
    radius = int(half_cell)
    if mouth_open:
        # Jugador con boca abierta
        if player_direction == 'RIGHT':
            pygame.draw.circle(window, YELLOW, center, radius)
            pygame.draw.polygon(window, BLACK, [
                center,
                (int(x + CELL_SIZE), int(y + CELL_SIZE / 4)),
                (int(x + CELL_SIZE), int(y + 3 * CELL_SIZE / 4))
            ])
        elif player_direction == 'LEFT':
            pygame.draw.circle(window, YELLOW, center, radius)
            pygame.draw.polygon(window, BLACK, [
                center,
                (int(x), int(y + CELL_SIZE / 4)),
                (int(x), int(y + 3 * CELL_SIZE / 4))
            ])
        elif player_direction == 'UP':
            pygame.draw.circle(window, YELLOW, center, radius)
            pygame.draw.polygon(window, BLACK, [
                center,
                (int(x + CELL_SIZE / 4), int(y)),
                (int(x + 3 * CELL_SIZE / 4), int(y))
            ])
        elif player_direction == 'DOWN':
            pygame.draw.circle(window, YELLOW, center, radius)
            pygame.draw.polygon(window, BLACK, [
                center,
                (int(x + CELL_SIZE / 4), int(y + CELL_SIZE)),
                (int(x + 3 * CELL_SIZE / 4), int(y + CELL_SIZE))
            ])
    else:
        # Jugador con boca cerrada (un círculo completo)
        pygame.draw.circle(window, YELLOW, center, radius)

# Función para mostrar el puntaje y el temporizador
def draw_score_and_timer():
    elapsed_time = int(time.time() - start_time)
    font = pygame.font.SysFont(None, 25)
    score_text = font.render(f"Puntaje: {score}", True, WHITE)
    timer_text = font.render(f"Tiempo: {elapsed_time} s", True, WHITE)
    window.blit(score_text, (10, 10))
    window.blit(timer_text, (10, 50))

# Inicializar estaciones
def initialize_stations():
    for station in station_questions:
        x, y = station["pos"]
        if maze[y][x] == '0' or maze[y][x] == ' ':
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            station["rect"] = rect
            stations.append(station)
        else:
            print(f"Advertencia: La estación en ({x}, {y}) no está en un camino abierto.")

# Preguntas y validación
def ask_question(station):
    root.deiconify()
    root.lift()
    root.attributes('-topmost', True)
    question = station["question"]
    options = "\n".join(station["options"])
    prompt = f"{question}\n\n{options}\n\nTu respuesta (A, B, C o D):"
    answer = simpledialog.askstring("Pregunta", prompt, parent=root)
    root.attributes('-topmost', False)
    root.withdraw()
    if answer is not None:
        return answer.strip().upper() == station["correct"]
    else:
        return False

# Función para dibujar el laberinto y manejar elementos
def draw_maze():
    global player_pos, finish_rect, start_pos
    walls.clear()
    station_positions = set((station["pos"][0], station["pos"][1]) for station in stations)
    wall_thickness = int(CELL_SIZE / 5)  # Define el grosor de la pared

    for row_index, row in enumerate(maze):
        for col_index, cell in enumerate(row):
            x = col_index * CELL_SIZE
            y = row_index * CELL_SIZE
            if cell == '1':
                # Ajustamos el dibujo de la pared
                wall_rect = pygame.Rect(
                    int(x + (CELL_SIZE - wall_thickness) / 2),
                    int(y + (CELL_SIZE - wall_thickness) / 2),
                    wall_thickness,
                    wall_thickness
                )
                pygame.draw.rect(window, BLUE, wall_rect)
                walls.append(wall_rect)
            elif cell == '0' or cell == ' ':
                pygame.draw.rect(window, BLACK, (int(x), int(y), int(CELL_SIZE), int(CELL_SIZE)))
                # Removed the extra parenthesis here
            elif cell == 'S':
                pygame.draw.rect(window, GREEN, (int(x), int(y), int(CELL_SIZE), int(CELL_SIZE)))
                if player_pos is None:
                    player_pos = [x, y]
                    start_pos = [x, y]
            elif cell == 'F':
                pygame.draw.rect(window, RED, (int(x), int(y), int(CELL_SIZE), int(CELL_SIZE)))
                finish_rect = pygame.Rect(int(x), int(y), int(CELL_SIZE), int(CELL_SIZE))
            else:
                pygame.draw.rect(window, BLACK, (int(x), int(y), int(CELL_SIZE), int(CELL_SIZE)))
            # Dibujar estaciones
            if (col_index, row_index) in station_positions:
                pygame.draw.circle(window, GREEN, (int(x + CELL_SIZE / 2), int(y + CELL_SIZE / 2)), int(CELL_SIZE / 4))

# Inicializar fantasmas
def initialize_ghosts():
    ghost_positions = [(15, 7), (10, 7), (32, 7), (34, 7)]  # Ajusta las posiciones según tu laberinto
    initial_directions = ['LEFT', 'RIGHT', 'UP', 'DOWN']  # Direcciones iniciales variadas
    for idx, (x, y) in enumerate(ghost_positions):
        color = GHOST_COLORS[idx % len(GHOST_COLORS)]
        direction = initial_directions[idx % len(initial_directions)]
        ghost = Ghost(x, y, color, direction)
        ghosts.append(ghost)

# Bucle principal del juego
def game_loop():
    global player_direction, player_pos, score, mouth_timer, mouth_open
    clock = pygame.time.Clock()
    running = True
    initialize_stations()
    initialize_ghosts()  # Inicializa los fantasmas

    # Reproducir música de fondo en bucle
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.play(-1)

    while running:
        window.fill(BLACK)
        draw_maze()
        draw_score_and_timer()

        # Controlar la animación de la boca
        mouth_timer += 1
        if mouth_timer >= mouth_timer_limit:
            mouth_open = not mouth_open
            mouth_timer = 0

        draw_player()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        new_pos = player_pos.copy()
        moved = False
        if keys[pygame.K_LEFT]:
            new_pos[0] -= player_speed
            player_direction = 'LEFT'
            moved = True
        if keys[pygame.K_RIGHT]:
            new_pos[0] += player_speed
            player_direction = 'RIGHT'
            moved = True
        if keys[pygame.K_UP]:
            new_pos[1] -= player_speed
            player_direction = 'UP'
            moved = True
        if keys[pygame.K_DOWN]:
            new_pos[1] += player_speed
            player_direction = 'DOWN'
            moved = True

        # Solo actualizar si el jugador se movió
        if moved:
            player_rect = pygame.Rect(int(new_pos[0]), int(new_pos[1]), int(CELL_SIZE), int(CELL_SIZE))
            if not any(player_rect.colliderect(wall) for wall in walls):
                player_pos = new_pos
            else:
                # Si colisiona con una pared, reproducir sonido de colisión y volver al inicio
                collision_sound.play()
                root.deiconify()
                root.lift()
                root.attributes('-topmost', True)
                messagebox.showinfo("Choque", "Has chocado con una pared. Regresas al inicio.", parent=root)
                root.attributes('-topmost', False)
                root.withdraw()
                player_pos = [start_pos[0], start_pos[1]]
                player_direction = 'RIGHT'

        # Actualizar y dibujar los fantasmas
        for ghost in ghosts:
            ghost.move()
            ghost.draw()
            # Comprobar colisión con el jugador
            player_rect = pygame.Rect(int(player_pos[0]), int(player_pos[1]), int(CELL_SIZE), int(CELL_SIZE))
            if player_rect.colliderect(ghost.rect):
                # Restar 5 puntos al puntaje
                score -= 5
                if score < 0:
                    score = 0  # Evitar puntaje negativo
                # Reproducir sonido de colisión
                collision_sound.play()
                # Mostrar mensaje
                root.deiconify()
                root.lift()
                root.attributes('-topmost', True)
                messagebox.showinfo(
                    "¡Te atraparon!",
                    "No te dejes atrapar por el fantasma del riesgo en tus proyectos.\nRegresas al inicio.",
                    parent=root
                )
                root.attributes('-topmost', False)
                root.withdraw()
                # Reiniciar posición del jugador
                player_pos = [start_pos[0], start_pos[1]]
                player_direction = 'RIGHT'
                break  # No es necesario verificar otros fantasmas

        # Recolección de estaciones
        player_rect = pygame.Rect(int(player_pos[0]), int(player_pos[1]), int(CELL_SIZE), int(CELL_SIZE))
        for station in stations[:]:
            station_rect = pygame.Rect(int(station["pos"][0] * CELL_SIZE), int(station["pos"][1] * CELL_SIZE), int(CELL_SIZE), int(CELL_SIZE))
            if player_rect.colliderect(station_rect):
                if ask_question(station):
                    score += station["points"]
                    stations.remove(station)
                else:
                    # Si falla la pregunta, volver a la posición inicial
                    game_over_sound = pygame.mixer.Sound(resource_path("pacman-dies.mp3"))
                    game_over_sound.play()
                    root.deiconify()
                    root.lift()
                    root.attributes('-topmost', True)
                    messagebox.showinfo("Respuesta incorrecta", "Respuesta incorrecta. Regresas al inicio.", parent=root)
                    root.attributes('-topmost', False)
                    root.withdraw()
                    player_pos = [start_pos[0], start_pos[1]]
                    player_direction = 'RIGHT'
                    break  # Salir del bucle para evitar múltiples actualizaciones

        # Verificar si se alcanzó el final
        if finish_rect and player_rect.colliderect(finish_rect):
            score += 100
            elapsed_time = int(time.time() - start_time)
            root.deiconify()
            root.lift()
            root.attributes('-topmost', True)
            messagebox.showinfo('Juego terminado', f'¡Has completado el juego!\nPuntaje: {score}\nTiempo: {elapsed_time} segundos', parent=root)
            root.attributes('-topmost', False)
            root.withdraw()
            running = False

        pygame.display.update()
        clock.tick(30)

    pygame.quit()
    sys.exit()

game_loop()
