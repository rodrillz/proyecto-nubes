import pygame
import numpy as np
import random
import matplotlib.pyplot as plt

# Configuración
GRID_SIZE = 20  # Dimensiones de la cuadrícula (20x20)
CELL_SIZE = 40  # Tamaño en píxeles de cada celda
INITIAL_DROPLET_PROB = 0.3  # Probabilidad inicial de gotas
MAX_TIME_STEPS = 10000  # Número de pasos de la simulación
SPLIT_PROB = 0.02  # Probabilidad de dividir una gota grande
SPLIT_THRESHOLD = 10  # Tamaño mínimo para dividir

# Inicialización de PyGame
pygame.init()
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Gotas en Estado Estable con División")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", CELL_SIZE // 3)

# Colores
BACKGROUND_COLOR = (224,224,224)
TEXT_COLOR = (255, 255, 255)

# Función para inicializar la cuadrícula
def initialize_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if random.random() < INITIAL_DROPLET_PROB:
                grid[i][j] = max(1, np.random.normal(5, 2))  # Tamaños distribuidos normalmente
    return grid

# Función para mover gotas
def move_droplets(grid):
    new_grid = np.zeros_like(grid)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > 0:  # Si hay una gota en la celda
                possible_moves = []
                if i > 0: possible_moves.append((-1, 0))  # Arriba
                if i < GRID_SIZE - 1: possible_moves.append((1, 0))  # Abajo
                if j > 0: possible_moves.append((0, -1))  # Izquierda
                if j < GRID_SIZE - 1: possible_moves.append((0, 1))  # Derecha
                
                if possible_moves:
                    di, dj = random.choice(possible_moves)
                    ni, nj = i + di, j + dj
                    new_grid[ni][nj] += grid[i][j]  # Coalescencia de gotas
    return new_grid

# Función para dividir gotas grandes
def split_large_droplets(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > SPLIT_THRESHOLD and random.random() < SPLIT_PROB:
                size = grid[i][j]
                possible_moves = []

                # Verificar vecinos para celdas vacías
                if i > 0 and grid[i-1][j] == 0: possible_moves.append((-1, 0))  # Arriba
                if i < GRID_SIZE - 1 and grid[i+1][j] == 0: possible_moves.append((1, 0))  # Abajo
                if j > 0 and grid[i][j-1] == 0: possible_moves.append((0, -1))  # Izquierda
                if j < GRID_SIZE - 1 and grid[i][j+1] == 0: possible_moves.append((0, 1))  # Derecha

                if possible_moves:
                    di, dj = random.choice(possible_moves)
                    ni, nj = i + di, j + dj

                    # Generar tamaños aleatorios para las nuevas gotas
                    size1 = random.uniform(1, size - 1)
                    size2 = size - size1

                    # Colocar las nuevas gotas en la celda actual y el vecino vacío
                    grid[i][j] = size1
                    grid[ni][nj] = size2

# Función para interpolar colores entre celeste y azul
def get_color_for_size(droplet_size):
    # Definir el rango de colores (celeste -> azul)
    celeste = np.array([173, 216, 230])  # Color celeste
    blue = np.array([0, 0, 255])  # Color azul

    # Normalizar el tamaño de la gota al rango [0, 1]
    normalized_size = np.clip(droplet_size / 20, 0, 1)

    # Interpolar entre celeste y azul
    color = celeste * (1 - normalized_size) + blue * normalized_size
    return tuple(color.astype(int))

# Función para dibujar la cuadrícula
def draw_grid(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            droplet_size = grid[i][j]
            if droplet_size > 0:
                color = get_color_for_size(droplet_size)
                pygame.draw.rect(
                    screen,
                    color,
                    (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )
                text = font.render(f"{droplet_size:.1f}", True, TEXT_COLOR)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)

# Función para recolectar datos de los tamaños de gotas
def collect_droplet_data(grid):
    droplet_sizes = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > 0:
                droplet_sizes.append(grid[i][j])
    return droplet_sizes

# Función para graficar los resultados
def plot_results(all_droplet_sizes, average_sizes):
    # Gráfico 1: Histograma de tamaños de gotas al final de la simulación
    final_droplets = all_droplet_sizes[-1] if all_droplet_sizes else []
    plt.figure(figsize=(10, 5))
    plt.hist(final_droplets, bins=30, edgecolor='black', color='blue')
    plt.title("Distribución de Tamaños de Gotas al Final de la Simulación")
    plt.xlabel("Tamaño de Gota")
    plt.ylabel("Frecuencia")
    plt.show()

    # Gráfico 2: Promedio de tamaños de gotas a lo largo del tiempo
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(average_sizes)), average_sizes, marker='o', color='blue')
    plt.title("Promedio del Tamaño de Gotas vs Tiempo")
    plt.xlabel("Paso de Tiempo")
    plt.ylabel("Promedio del Tamaño de Gotas")
    plt.show()

# función main para recopilar datos y graficar (y correr el juego...)
def main():
    grid = initialize_grid()
    running = True
    time_step = 0

    all_droplet_sizes = []  # Lista para almacenar tamaños de gotas en cada paso
    average_sizes = []  # Lista para el promedio de tamaños en cada paso

    while running and time_step < MAX_TIME_STEPS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simulación
        grid = move_droplets(grid)
        split_large_droplets(grid)

        # Recolectar datos de tamaños de gotas
        droplet_sizes = collect_droplet_data(grid)
        all_droplet_sizes.append(droplet_sizes)
        average_sizes.append(np.mean(droplet_sizes) if droplet_sizes else 0)

        # Visualización
        screen.fill(BACKGROUND_COLOR)
        draw_grid(grid)
        pygame.display.flip()

        clock.tick(20)
        time_step += 1

    pygame.quit()

    # Graficar resultados al final de la simulación
    #plot_results(all_droplet_sizes, average_sizes)

if __name__ == "__main__":
    main()
