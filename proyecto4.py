import pygame
import numpy as np
import random
import matplotlib.pyplot as plt

# Configuration
GRID_SIZE = 40 # Grid dimensions (20x20)
CELL_SIZE = 20  # Pixel size of each cell
INITIAL_DROPLET_PROB = 0.4  # Initial droplet probability
MAX_TIME_STEPS = 400  # Number of simulation steps
ADD_SMALL_DROPLET_PROB = 0.05  # Probability of adding small droplets

# Droplet size thresholds
MEDIUM_THRESHOLD = 6
MEDIUM_LARGE_THRESHOLD = 15
LARGE_THRESHOLD = 20

# PyGame initialization
pygame.init()
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Steady-State Droplet Simulation with Rain Formation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", CELL_SIZE // 3)

# Colors
BACKGROUND_COLOR = (224, 224, 224)
TEXT_COLOR = (255, 255, 255)

# Function to initialize the grid
def initialize_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if random.random() < INITIAL_DROPLET_PROB:
                grid[i][j] = max(1, np.random.normal(5, 2))  # Normally distributed sizes
    return grid

# Function to move droplets based on their size
def move_droplets(grid):
    new_grid = np.zeros_like(grid)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            droplet_size = grid[i][j]
            if droplet_size > 0:
                possible_moves = []
                if droplet_size <= MEDIUM_THRESHOLD:
                    if i < GRID_SIZE - 1: possible_moves.append((1, 0))  # Down
                    if i < GRID_SIZE - 1 and j > 0: possible_moves.append((1, -1))  # Southwest
                    if i < GRID_SIZE - 1 and j < GRID_SIZE - 1: possible_moves.append((1, 1))  # Southeast
                elif droplet_size <= MEDIUM_LARGE_THRESHOLD:
                    if i < GRID_SIZE - 1: possible_moves.append((1, 0))  # Down
                    if i < GRID_SIZE - 1 and j > 0: possible_moves.append((1, -1))  # Southwest
                    if i < GRID_SIZE - 1 and j < GRID_SIZE - 1: possible_moves.append((1, 1))  # Southeast
                else:  # Large droplets
                    if i < GRID_SIZE - 1: possible_moves.append((1, 0))  # Down

                # Move or remove droplet
                if possible_moves:
                    di, dj = random.choice(possible_moves)
                    ni, nj = i + di, j + dj
                    if ni < GRID_SIZE:  # If not off-grid
                        new_grid[ni][nj] += droplet_size  # Coalesce droplets
                    # Else: Droplet falls to the ground (do nothing)
                else:
                    new_grid[i][j] =0  # Stay in place
    return new_grid

# Function to add new small droplets
def add_small_droplets(grid):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if random.random() < ADD_SMALL_DROPLET_PROB and grid[i][j] == 0:
                grid[i][j] = 3  # Small droplets have size 1

# Function to interpolate colors between celeste and blue
def get_color_for_size(droplet_size):
    # Define the color range (celeste -> blue)
    celeste = np.array([173, 216, 230])  # Celeste color
    blue = np.array([0, 0, 255])  # Blue color

    # Normalize droplet size to the range [0, 1]
    normalized_size = np.clip(droplet_size / 20, 0, 1)

    # Interpolate between celeste and blue
    color = celeste * (1 - normalized_size) + blue * normalized_size
    return tuple(color.astype(int))

# Function to draw the grid
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

# Añadido: Función para recolectar datos de los tamaños de gotas
def collect_droplet_data(grid):
    droplet_sizes = []
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > 0:
                droplet_sizes.append(grid[i][j])
    return droplet_sizes

# Añadido: Función para graficar los resultados
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

# Main simulation
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

        # Simulation steps
        grid = move_droplets(grid)
        add_small_droplets(grid)

        # Recolectar datos de tamaños de gotas
        droplet_sizes = collect_droplet_data(grid)
        all_droplet_sizes.append(droplet_sizes)
        average_sizes.append(np.mean(droplet_sizes) if droplet_sizes else 0)

        # Visualization
        screen.fill(BACKGROUND_COLOR)
        draw_grid(grid)
        pygame.display.flip()

        # Wait and update
        clock.tick(10)
        time_step += 1

    

    pygame.quit()
    # Graficar resultados al final de la simulación
    plot_results(all_droplet_sizes, average_sizes)

if __name__ == "__main__":
    main()
