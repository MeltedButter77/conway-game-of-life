import asyncio
import pygame


def get_live_neighbors(grid, location):
    x, y = location
    neighboring = []
    # iterates through 8 surrounding locations
    for x_change in [-1, 0, 1]:
        for y_change in [-1, 0, 1]:
            if x_change == 0 and y_change == 0:
                continue
            neighbor_x, neighbor_y = x + x_change, y + y_change
            if (neighbor_x, neighbor_y) in grid:
                neighboring.append((neighbor_x, neighbor_y))
    return neighboring


def get_all_neighbors(location):
    x, y = location
    neighboring = []
    # iterates through 8 surrounding locations
    for x_change in [-1, 0, 1]:
        for y_change in [-1, 0, 1]:
            if x_change == 0 and y_change == 0:
                continue
            neighbor_x, neighbor_y = x + x_change, y + y_change
            neighboring.append((neighbor_x, neighbor_y))
    return neighboring


def iterate_life(grid):
    # Our grid is a set of tuples. This means we are not storing dead cells.
    # We start by creating a new empty grid
    iterated_grid = set()
    for x, y in grid:
        live_neighboring_squares = get_live_neighbors(grid, (x, y))
        all_neighboring_locations = get_all_neighbors((x, y))
        live_num = len(live_neighboring_squares)

        # Every cell will die unless it is remade every iteration
        # Therefore both rules 1 and 3 are automatically true if rules 2 and 4 implemented

        # 1. Underpopulation rule - "Any live cell with fewer than two live neighbours dies in the next generation."
        # 2. Survival rule - "Any live cell with two or three live neighbours lives on to the next generation."
        # 3. Overpopulation rule - "Any live cell with more than three live neighbours dies in the next generation."
        # 4. Birth rule - "Any dead cell with exactly three live neighbours becomes a live cell in the next generation."

        # 2. Survival rule
        if live_num in [2, 3]:
            iterated_grid.add((x, y))

        # 4. Birth rule
        # iterates through 8 surrounding locations of a cell. This is how we can check dead cells despite not storing them in the grid
        for neighbor_location in all_neighboring_locations:
            # filter for dead cells
            if neighbor_location not in grid:
                # if a dead cell has 3 live neighbors, it becomes a live cell
                if len(get_live_neighbors(grid, neighbor_location)) == 3:
                    iterated_grid.add(neighbor_location)

    return iterated_grid


def handle_zoom(event):
    global ZOOM, CAMERA
    mouse_x, mouse_y = pygame.mouse.get_pos()
    world_x_before = (mouse_x - CAMERA[0]) / (GRID_SIZE * ZOOM)
    world_y_before = (mouse_y - CAMERA[1]) / (GRID_SIZE * ZOOM)

    # Adjust zoom
    ZOOM *= 1.1 ** event.y
    ZOOM = max(0.1, min(ZOOM, 10))

    new_world_x_screen = world_x_before * GRID_SIZE * ZOOM
    new_world_y_screen = world_y_before * GRID_SIZE * ZOOM

    CAMERA[0] = mouse_x - new_world_x_screen
    CAMERA[1] = mouse_y - new_world_y_screen


def get_mouse_grid_pos(pos):
    return (
        round((pos[0] - CAMERA[0]) // (GRID_SIZE * ZOOM)),
        round((pos[1] - CAMERA[1]) // (GRID_SIZE * ZOOM))
    )


def handle_mouse_buttons(event):
    global camera_mouse_down

    left, middle, right = pygame.mouse.get_pressed()

    if left:
        GRID.add(get_mouse_grid_pos(event.pos))
    if right:
        pos = get_mouse_grid_pos(event.pos)
        if pos in GRID:
            GRID.remove(pos)
    if middle and event.type == pygame.MOUSEBUTTONDOWN:
        camera_mouse_down = (
            event.pos[0] / ZOOM - CAMERA[0] / ZOOM,
            event.pos[1] / ZOOM - CAMERA[1] / ZOOM
        )
    if event.type == pygame.MOUSEBUTTONUP:
        camera_mouse_down = None


async def run():
    global GRID, GRID_SIZE, CAMERA, ZOOM

    GRID_SIZE = 10
    GRID = set()
    CAMERA = [0, 0]
    ZOOM = 1

    window = pygame.display.set_mode((1400, 900))
    clock = pygame.time.Clock()
    fps_limit = 1000

    camera_mouse_down = None
    running = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = not running

            if event.type == pygame.MOUSEWHEEL:
                handle_zoom(event)

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                handle_mouse_buttons(event)

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            CAMERA[0] += 5
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            CAMERA[0] -= 5
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            CAMERA[1] += 5
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            CAMERA[1] -= 5

        if camera_mouse_down:
            mouse_pos = pygame.mouse.get_pos()
            CAMERA = [
                mouse_pos[0] - camera_mouse_down[0] * ZOOM,
                mouse_pos[1] - camera_mouse_down[1] * ZOOM
            ]

        if running:
            GRID = iterate_life(GRID)

        window.fill("white")
        for square in GRID:
            pygame.draw.rect(window, "black", (
                square[0] * GRID_SIZE * ZOOM + CAMERA[0],
                square[1] * GRID_SIZE * ZOOM + CAMERA[1],
                GRID_SIZE * ZOOM,
                GRID_SIZE * ZOOM))

        clock.tick(fps_limit)
        pygame.display.flip()

        fps = str(int(clock.get_fps()))
        pygame.display.set_caption(fps)

        await asyncio.sleep(0)  # Yield to web

asyncio.run(run())
