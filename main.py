import pygame


WINDOW = pygame.display.set_mode((1400, 900))
CLOCK = pygame.time.Clock()
GRID_SIZE = 10
FPS_LIMIT = 1000

GRID = set()
CAMERA = [0, 0]
ZOOM = 1


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
    iterated_grid = set()
    for x, y in grid:
        live_neighboring_squares = get_live_neighbors(grid, (x, y))
        all_neighboring_locations = get_all_neighbors((x, y))
        live_num = len(live_neighboring_squares)

        # Every cell will die unless it is remade every iteration

        # 1. Underpopulation rule - "Any live cell with fewer than two live neighbours dies in the next generation."

        # 2. Survival rule - "Any live cell with two or three live neighbours lives on to the next generation."
        if live_num in [2, 3]:
            iterated_grid.add((x, y))

        # 3. Overpopulation rule - "Any live cell with more than three live neighbours dies in the next generation."

        # 4. Birth rule - "Any dead cell with exactly three live neighbours becomes a live cell in the next generation."
        for neighbor_location in all_neighboring_locations:
            # filter for dead cells
            if neighbor_location not in grid:
                if len(get_live_neighbors(grid, neighbor_location)) == 3:
                    iterated_grid.add(neighbor_location)

    return iterated_grid


camera_mouse_down = None
running = False
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if running:
                running = False
            else:
                running = True

        if event.type == pygame.MOUSEWHEEL:
            # 1. Get mouse position in world space BEFORE zoom
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x_before = (mouse_x - CAMERA[0]) / (GRID_SIZE * ZOOM)
            world_y_before = (mouse_y - CAMERA[1]) / (GRID_SIZE * ZOOM)

            # 2. Change zoom level
            old_zoom = ZOOM
            ZOOM *= 1.1 ** event.y  # Scroll up = zoom in, down = zoom out
            ZOOM = max(0.1, min(ZOOM, 10))  # Clamp between 0.1 and 10

            # 3. Get world position AFTER zoom and adjust CAMERA so world point stays under cursor
            new_world_x_screen = world_x_before * GRID_SIZE * ZOOM
            new_world_y_screen = world_y_before * GRID_SIZE * ZOOM

            CAMERA[0] = mouse_x - new_world_x_screen
            CAMERA[1] = mouse_y - new_world_y_screen

        if event.type == pygame.MOUSEBUTTONDOWN or pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left Click
                GRID.add((
                    round((event.pos[0] - CAMERA[0]) // (GRID_SIZE * ZOOM)),
                    round((event.pos[1] - CAMERA[1]) // (GRID_SIZE * ZOOM))
                ))
            if pygame.mouse.get_pressed()[2]:  # Right Click
                pos = (
                    round((event.pos[0] - CAMERA[0]) // (GRID_SIZE * ZOOM)),
                    round((event.pos[1] - CAMERA[1]) // (GRID_SIZE * ZOOM))
                )
                if pos in GRID:
                    GRID.remove(pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[1]:  # Middle Click
                camera_mouse_down = (
                    event.pos[0] / ZOOM - CAMERA[0] / ZOOM,
                    event.pos[1] / ZOOM - CAMERA[1] / ZOOM
                )
        if event.type == pygame.MOUSEBUTTONUP:
            camera_mouse_down = None

    if camera_mouse_down:
        mouse_pos = pygame.mouse.get_pos()
        CAMERA = [
            mouse_pos[0] - camera_mouse_down[0] * ZOOM,
            mouse_pos[1] - camera_mouse_down[1] * ZOOM
        ]

    if running:
        GRID = iterate_life(GRID)

    WINDOW.fill("white")
    for square in GRID:
        pygame.draw.rect(WINDOW, "black", (
            square[0] * GRID_SIZE * ZOOM + CAMERA[0],
            square[1] * GRID_SIZE * ZOOM + CAMERA[1],
            GRID_SIZE * ZOOM,
            GRID_SIZE * ZOOM))

    CLOCK.tick(FPS_LIMIT)
    pygame.display.flip()

    fps = str(int(CLOCK.get_fps()))
    pygame.display.set_caption(fps)