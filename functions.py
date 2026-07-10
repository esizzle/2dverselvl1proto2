# Generic helpers with no game-state dependencies.
# world_to_lvl2_chunk was removed: coordinate conversions live on World
# (world_grid.py), and environment queries go through World.get_env_features.

def distance_squared(obj1, obj2):
    dx = obj1.position[0] - obj2.position[0]
    dy = obj1.position[1] - obj2.position[1]
    return dx * dx + dy * dy
