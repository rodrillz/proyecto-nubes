import pygame
import numpy as np
import random
import matplotlib.pyplot as plt

# Configuración de la simulación
GRID_SIZE = 20  # Tamaño de la cuadrícula (20x20)
CELL_SIZE = 30  # Tamaño de cada celda en píxeles
INITIAL_DROPLET_PROB = 0.3  # Probabilidad inicial de que una celda tenga una gota
MAX_TIME_STEPS = 10000  # Número máximo de pasos de simulación

# Inicialización de PyGame
pygame.init()
WIDTH = GRID_SIZE * CELL_SIZE  # Ancho de la ventana
HEIGHT = GRID_SIZE * CELL_SIZE  # Altura de la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Coalescencia de Gotas")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", CELL_SIZE // 3)  # Tamaño dinámico para la fuente

# Colores
BACKGROUND_COLOR = (224, 224, 224)  # Color de fondo
CELL_COLOR_BASE = (0, 0, 255)  # Color base azul para las gotas
TEXT_COLOR = (255, 255, 255)  # Color del texto (blanco)

# Función para inicializar la cuadrícula
def initialize_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if random.random() < INITIAL_DROPLET_PROB:
                grid[i][j] = max(1, np.random.normal(5, 2))  # Tamaño inicial (distribución normal)
    return grid

# Función para calcular el color basado en el tamaño de la gota
def get_color_for_size(droplet_size):
    # Definir el rango de colores (celeste -> azul)
    celeste = np.array([173, 216, 230])  # Color celeste
    blue = np.array([0, 0, 255])  # Color azul

    # Normalizar el tamaño de la gota al rango [0, 1]
    normalized_size = np.clip(droplet_size / 20, 0, 1)

    # Interpolar entre celeste y azul
    color = celeste * (1 - normalized_size) + blue * normalized_size
    return tuple(color.astype(int))

# Función para mover las gotas en la cuadrícula
def move_droplets(grid):
    new_grid = np.zeros_like(grid)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > 0:  # Si hay una gota en la celda
                # Determinar direcciones válidas
                possible_moves = []
                if i > 0:  # Puede moverse hacia arriba
                    possible_moves.append((-1, 0))
                if i < GRID_SIZE - 1:  # Puede moverse hacia abajo
                    possible_moves.append((1, 0))
                if j > 0:  # Puede moverse hacia la izquierda
                    possible_moves.append((0, -1))
                if j < GRID_SIZE - 1:  # Puede moverse hacia la derecha
                    possible_moves.append((0, 1))
                
                # Elegir movimiento aleatorio válido
                if possible_moves:
                    di, dj = random.choice(possible_moves)
                    ni, nj = i + di, j + dj
                    new_grid[ni][nj] += grid[i][j]  # Coalescencia de gotas
    return new_grid

# Función para dibujar la cuadrícula
def draw_grid(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            droplet_size = grid[i][j]
            if droplet_size > 0:
                # Escalamos el color según el tamaño de la gota (más grande = más brillante)
                color = get_color_for_size(droplet_size)  # Azul más intenso para gotas más grandes
                pygame.draw.rect(
                    screen,
                    color,
                    (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )
                # Renderizamos el tamaño como texto
                text = font.render(f"{droplet_size:.1f}", True, TEXT_COLOR)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)

# Función para recolectar los tamaños de las gotas
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

    all_droplet_sizes = []  # Almacenar tamaños de gotas para el histograma y el gráfico
    average_sizes = []  # Almacenar tamaños promedio de gotas para el gráfico

    while running and time_step < MAX_TIME_STEPS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualizar simulación
        grid = move_droplets(grid)

        # Recolectar datos de las gotas para graficar
        droplet_sizes = collect_droplet_data(grid)
        all_droplet_sizes.append(droplet_sizes)
        average_sizes.append(np.mean(droplet_sizes) if droplet_sizes else 0)

        # Dibujar simulación
        screen.fill(BACKGROUND_COLOR)
        draw_grid(grid)
        pygame.display.flip()

        # Esperar y avanzar
        clock.tick(10)  # 10 FPS
        time_step += 1

    pygame.quit()

    # Graficar los resultados
    #plot_results(all_droplet_sizes, average_sizes)

# Función para graficar los resultados
def plot_results(all_droplet_sizes, average_sizes):
    # Graficar histograma de tamaños de gotas al final de la simulación
    final_droplets = all_droplet_sizes[-1] if all_droplet_sizes else []
    plt.figure(figsize=(10, 5))
    plt.hist(final_droplets, bins=30, edgecolor='black')
    plt.title("Distribución de Tamaños de Gotas al Final del Paso de Simulación")
    plt.xlabel("Tamaño de la Gota")
    plt.ylabel("Frecuencia")
    plt.show()

    # Graficar el tamaño promedio de gotas a lo largo del tiempo
    plt.figure(figsize=(10, 5))
    plt.plot(range(len(average_sizes)), average_sizes, marker='o', color='b')
    plt.title("Tamaño Promedio de las Gotas vs. Tiempo")
    plt.xlabel("Paso de Tiempo")
    plt.ylabel("Tamaño Promedio de la Gota")
    plt.show()

if __name__ == "__main__":
    main()
