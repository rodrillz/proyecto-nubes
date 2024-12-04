import pygame
import numpy as np
import random

# Configuración de la simulación
GRID_SIZE = 50  # Tamaño de la cuadrícula (50x50)
CELL_SIZE = 20  # Tamaño de cada celda en píxeles
INITIAL_DROPLET_PROB = 0.3  # Probabilidad inicial de gotas
MAX_TIME_STEPS = 500  # Número máximo de pasos de simulación
ADD_SMALL_DROPLET_PROB = 0.05  # Probabilidad de añadir gotas pequeñas

# Inicialización de PyGame
pygame.init()
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Formación de Lluvia")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", CELL_SIZE // 3)

# Colores
BACKGROUND_COLOR = (224,224,224)
GROUND_COLOR = (139, 69, 19)  # Marrón tierra
TEXT_COLOR = (255, 255, 255)

# Función para inicializar la cuadrícula
def initialize_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if random.random() < INITIAL_DROPLET_PROB:
                grid[i][j] = max(1, np.random.normal(5, 2))
    return grid

# Función de movimiento de gotas
def move_droplets(grid):
    new_grid = np.zeros_like(grid)
    
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] > 0:
                droplet_size = grid[i][j]
                
                # Determinar movimientos válidos según el tamaño de la gota
                possible_moves = []
                if droplet_size > 5 and droplet_size <= 15:  # Gotas medianas
                    possible_moves = [(1, 0), (1, 1), (1, -1)]
                elif droplet_size > 15:  # Gotas grandes
                    possible_moves = [(1, 0)]
                else:  # Gotas pequeñas
                    possible_moves = [
                        (0, 1), (0, -1), (1, 0), (-1, 0),
                        (1, 1), (1, -1), (-1, 1), (-1, -1)
                    ]
                
                # Filtrar movimientos dentro de los límites de la cuadrícula
                valid_moves = [
                    (di, dj) for di, dj in possible_moves
                    if 0 <= i + di < GRID_SIZE and 0 <= j + dj < GRID_SIZE
                ]
                
                # Realizar movimiento si hay opciones válidas
                if valid_moves:
                    di, dj = random.choice(valid_moves)
                    new_i, new_j = i + di, j + dj
                    new_grid[new_i][new_j] += droplet_size
    
    return new_grid


# Función para añadir gotas pequeñas
def add_small_droplets(grid):
    for j in range(GRID_SIZE):
        if random.random() < ADD_SMALL_DROPLET_PROB:
            grid[0][j] = max(1, np.random.normal(3, 1))

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

# Función para dibujar la cuadrícula
def draw_grid(grid):
    # Dibujar suelo
    pygame.draw.rect(
        screen, 
        GROUND_COLOR, 
        (0, (GRID_SIZE-1) * CELL_SIZE, WIDTH, CELL_SIZE)
    )
    
    for i in range(GRID_SIZE - 1):  # Excluir la última fila (suelo)
        for j in range(GRID_SIZE):
            droplet_size = grid[i][j]
            if droplet_size > 0:
                color = get_color_for_size(droplet_size)  # Azul intensidad según tamaño de gota
                pygame.draw.rect(
                    screen,
                    color,
                    (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                )
                text = font.render(f"{droplet_size:.1f}", True, TEXT_COLOR)
                text_rect = text.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2, i * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(text, text_rect)

# Simulación principal
def main():
    grid = initialize_grid()
    running = True
    time_step = 0

    while running and time_step < MAX_TIME_STEPS:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Añadir gotas pequeñas en la parte superior
        add_small_droplets(grid)
        
        # Mover gotas
        grid = move_droplets(grid)

        # Dibujar simulación
        screen.fill(BACKGROUND_COLOR)
        draw_grid(grid)
        pygame.display.flip()

        # Control de velocidad
        clock.tick(10)
        time_step += 1

    pygame.quit()

if __name__ == "__main__":
    main()