import pygame
import numpy as np
import random
import matplotlib.pyplot as plt

# Configuración
GRID_SIZE = 80  # Dimensiones de la cuadrícula (50x50)
CELL_SIZE = 10  # Tamaño en píxeles de cada celda
FPS = 5  # Cuadros por segundo

# Probabilidades
PROB_HUMIDITY = 0.05  # Probabilidad de que una celda sin nube gane suficiente humedad
PROB_EXTINCTION = 0.02  # Probabilidad de que una celda de nube pierda su estado de nube
PROB_ACT = 0.03  # Probabilidad de que una celda se vuelva lista para transicionar

# Inicialización de PyGame
pygame.init()
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación 2D de Evolución de Nubes")
clock = pygame.time.Clock()

# Colores
BACKGROUND_COLOR = (30, 30, 30)
HUMIDITY_COLOR = (0, 100, 255)  # Azul para humedad
CLOUD_COLOR = (200, 200, 200)  # Blanco para nubes
ACT_COLOR = (255, 165, 0)  # Naranja para "act"

# Inicializa la cuadrícula con humedad aleatoria en la región central
def initialize_grid():
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=[('humidity', bool), ('cloud', bool), ('act', bool)])
    
    # Define la región central
    center_x, center_y = GRID_SIZE // 2, GRID_SIZE // 2
    radius = 3  # Radio para el área central
    initial_humidity_prob = 0.5  # Probabilidad de asignar humedad a las celdas en la región central

    for i in range(center_x - radius, center_x + radius + 1):
        for j in range(center_y - radius, center_y + radius + 1):
            if 0 <= i < GRID_SIZE and 0 <= j < GRID_SIZE:
                if random.random() < initial_humidity_prob:
                    grid[i][j]['humidity'] = True

    return grid

# Función para dibujar la cuadrícula
def draw_grid(grid):
    screen.fill(BACKGROUND_COLOR)
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            x, y = j * CELL_SIZE, i * CELL_SIZE
            if grid[i][j]['cloud']:
                pygame.draw.rect(screen, CLOUD_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
            elif grid[i][j]['act']:
                pygame.draw.rect(screen, ACT_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
            elif grid[i][j]['humidity']:
                pygame.draw.rect(screen, HUMIDITY_COLOR, (x, y, CELL_SIZE, CELL_SIZE))

# Función para actualizar la cuadrícula según las reglas
def update_grid(grid):
    new_grid = grid.copy()
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            cell = grid[i][j]

            # Regla 2: Si cloud o act es verdadero, cloud permanece verdadero
            # Restringir la expansión de nubes a celdas con vecinos activos o nublados
            if cell['cloud'] or cell['act']:
                neighbors = get_neighbors(grid, i, j)
                if any(neighbor['act'] or neighbor['cloud'] for neighbor in neighbors):
                    new_grid[i][j]['cloud'] = True

            # Regla 3: Si act no es verdadero pero humidity es verdadero y un vecino tiene act verdadero, act se vuelve verdadero
            if not cell['act'] and cell['humidity']:
                neighbors = get_neighbors(grid, i, j)
                if any(neighbor['act'] for neighbor in neighbors):
                    new_grid[i][j]['act'] = True

            # Regla 4: Si cloud es verdadero, con probabilidad probExtinction, se vuelve falso
            if cell['cloud'] and random.random() < PROB_EXTINCTION:
                new_grid[i][j]['cloud'] = False

            # Regla 5: Con probabilidad probAct, act se vuelve verdadero
            # Limitar la expansión de act a vecinos de celdas activas o húmedas
            if not cell['act']:
                neighbors = get_neighbors(grid, i, j)
                if any(neighbor['humidity'] or neighbor['act'] for neighbor in neighbors):
                    if random.random() < PROB_ACT:
                        new_grid[i][j]['act'] = True

            # Expansión de humedad con el tiempo desde los vecinos
            if not cell['humidity']:
                neighbors = get_neighbors(grid, i, j)
                if any(neighbor['humidity'] for neighbor in neighbors):
                    if random.random() < 0.2:  # Probabilidad de expansión
                        new_grid[i][j]['humidity'] = True

    return new_grid

# Obtener vecinos de una celda
def get_neighbors(grid, x, y):
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            neighbors.append(grid[nx][ny])
    return neighbors

# Recopilar datos sobre los estados de las nubes, la humedad y act
def collect_data(grid):
    cloud_count = np.sum(grid['cloud'])
    humidity_count = np.sum(grid['humidity'])
    act_count = np.sum(grid['act'])
    return cloud_count, humidity_count, act_count

# Graficar resultados
def plot_results(time_steps, cloud_counts, humidity_counts, act_counts):
    # Gráfico 1: Evolución de las cantidades de células
    plt.figure(figsize=(10, 6))
    plt.plot(time_steps, cloud_counts, label='Celdas de Nubes', color='gray')
    plt.plot(time_steps, humidity_counts, label='Celdas de Humedad', color='blue')
    plt.plot(time_steps, act_counts, label='Celdas Activas', color='orange')
    plt.title("Evolución de los estados de las células")
    plt.xlabel("Paso de tiempo")
    plt.ylabel("Cantidad de células")
    plt.legend()
    plt.grid()
    plt.show()

    # Gráfico 2: Histograma final de las células nubladas
    plt.figure(figsize=(10, 6))
    plt.bar(['Nubes', 'Humedad', 'Act'], [cloud_counts[-1], humidity_counts[-1], act_counts[-1]], color=['gray', 'blue', 'orange'])
    plt.title("Distribución final de estados de células")
    plt.ylabel("Cantidad")
    plt.show()

    # Gráfico 3: Relación entre células de humedad y activadas
    plt.figure(figsize=(10, 6))
    plt.scatter(humidity_counts, act_counts, color='purple', alpha=0.7)
    plt.title("Relación entre Humedad y Act")
    plt.xlabel("Humedad")
    plt.ylabel("Act")
    plt.grid()
    plt.show()

# Simulación principal
def main():
    grid = initialize_grid()
    running = True
    time_step = 0

    # Recopilación de datos
    time_steps = []
    cloud_counts = []
    humidity_counts = []
    act_counts = []

    # Bucle de simulación
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualizar la cuadrícula
        grid = update_grid(grid)

        # Recopilar datos
        cloud_count, humidity_count, act_count = collect_data(grid)
        time_steps.append(time_step)
        cloud_counts.append(cloud_count)
        humidity_counts.append(humidity_count)
        act_counts.append(act_count)

        # Dibujar la cuadrícula
        draw_grid(grid)
        pygame.display.flip()

        # Controlar la velocidad de fotogramas
        clock.tick(FPS)
        time_step += 1

        if time_step >= 200:  # Detener después de 200 pasos
            running = False

    # Graficar resultados
    plot_results(time_steps, cloud_counts, humidity_counts, act_counts)

    # Mantener la visualización activa
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        draw_grid(grid)
        pygame.display.flip()

if __name__ == "__main__":
    main()
