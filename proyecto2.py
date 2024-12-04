import pygame
import numpy as np
import random
import matplotlib.pyplot as plt
# Configuración
GRID_SIZE = 20  # Dimensiones de la cuadrícula (20x20)
CELL_SIZE = 30  # Tamaño en píxeles de cada celda
INITIAL_DROPLET_PROB = 0.3  # Probabilidad inicial de que haya gotas
MAX_TIME_STEPS = 10000  # Número máximo de pasos de simulación
ADD_DROPLET_PROB = 0.05  # Probabilidad de añadir gotas pequeñas
REMOVE_DROPLET_PROB = 0.03  # Probabilidad de eliminar gotas grandes
MAX_DROPLET_SIZE_TO_REMOVE = 20  # Umbral para eliminar gotas grandes
NEW_DROPLET_SIZE = 3  # Tamaño de las gotas añadidas

# Inicialización de PyGame
pygame.init()
WIDTH = GRID_SIZE * CELL_SIZE  # Ancho de la ventana
HEIGHT = GRID_SIZE * CELL_SIZE  # Altura de la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de gotas en estado estacionario")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", CELL_SIZE // 3)

# Colores
BACKGROUND_COLOR = (224, 224, 224)  # Color de fondo
TEXT_COLOR = (255, 255, 255)  # Color del texto

# Función para inicializar la cuadrícula
def initialize_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if random.random() < INITIAL_DROPLET_PROB:
                grid[i][j] = max(1, np.random.normal(5, 2))  # Tamaños distribuidos normalmente
    return grid

# Función para mover las gotas
def move_droplets(grid):
    new_grid = np.zeros_like(grid)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > 0:  # Si hay una gota en la celda
                # Determinar direcciones válidas (sin envolver en los bordes)
                possible_moves = []
                if i > 0: possible_moves.append((-1, 0))  # Arriba
                if i < GRID_SIZE - 1: possible_moves.append((1, 0))  # Abajo
                if j > 0: possible_moves.append((0, -1))  # Izquierda
                if j < GRID_SIZE - 1: possible_moves.append((0, 1))  # Derecha
                
                # Elegir aleatoriamente un movimiento válido
                if possible_moves:
                    di, dj = random.choice(possible_moves)
                    ni, nj = i + di, j + dj
                    new_grid[ni][nj] += grid[i][j]  # Unir gotas
    return new_grid

# Función para añadir nuevas gotas pequeñas
def add_small_droplets(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if random.random() < ADD_DROPLET_PROB and grid[i][j] == 0:
                grid[i][j] = NEW_DROPLET_SIZE

# Función para eliminar gotas grandes
def remove_large_droplets(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > MAX_DROPLET_SIZE_TO_REMOVE and random.random() < REMOVE_DROPLET_PROB:
                grid[i][j] = 0

# Función para interpolar colores entre celeste y azul
def get_color_for_size(droplet_size):
    # Definir el rango de colores (celeste -> azul)
    celeste = np.array([173, 216, 230])  # Color celeste
    blue = np.array([0, 0, 255])  # Color azul

    # Normalizar el tamaño de la gota al rango [0, 1]
    normalized_size = np.clip(droplet_size / MAX_DROPLET_SIZE_TO_REMOVE, 0, 1)

    # Interpolar entre celeste y azul
    color = celeste * (1 - normalized_size) + blue * normalized_size
    return tuple(color.astype(int))

# Función para dibujar la cuadrícula
def draw_grid(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            droplet_size = grid[i][j]
            if droplet_size > 0:
                color = get_color_for_size(droplet_size)  # Obtener color según tamaño de gota
                pygame.draw.rect(
                    screen,
                    color,
                    (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )
                # Mostrar el tamaño de la gota como texto encima de la celda
                text = font.render(f"{droplet_size:.1f}", True, TEXT_COLOR)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)

# Función para recolectar tamaños de gotas
def collect_droplet_data(grid):
    droplet_sizes = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > 0:
                droplet_sizes.append(grid[i][j])
    return droplet_sizes

# Simulación principal
def main():
    grid = initialize_grid()
    running = True
    time_step = 0

    all_droplet_sizes = []  # Para almacenar tamaños de gotas para el histograma
    average_sizes = []  # Para almacenar el tamaño promedio de las gotas para el gráfico

    while running and time_step < MAX_TIME_STEPS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Pasos de la simulación
        grid = move_droplets(grid)
        add_small_droplets(grid)  # Añadir nuevas gotas
        remove_large_droplets(grid)  # Eliminar gotas grandes

        # Recolectar tamaños de gotas para el gráfico
        droplet_sizes = collect_droplet_data(grid)
        all_droplet_sizes.append(droplet_sizes)
        average_sizes.append(np.mean(droplet_sizes) if droplet_sizes else 0)

        # Visualización
        screen.fill(BACKGROUND_COLOR)
        draw_grid(grid)
        pygame.display.flip()

        # Esperar y actualizar
        clock.tick(10)
        time_step += 1

    pygame.quit()
