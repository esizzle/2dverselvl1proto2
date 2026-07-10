from world_grid import CELL_SIZE, LVL1_CHUNK_SIZE, LVL2_CHUNK_SIZE

def distance_squared(obj1, obj2):
    dx = obj1.position[0] - obj2.position[0]
    dy = obj1.position[1] - obj2.position[1]
    return dx * dx + dy * dy

def world_to_lvl2_chunk(player_pos):
    x, y = player_pos
    c2x = int(x / CELL_SIZE / LVL1_CHUNK_SIZE / LVL2_CHUNK_SIZE)
    c2y = int(y / CELL_SIZE / LVL1_CHUNK_SIZE / LVL2_CHUNK_SIZE)
    return c2x, c2y