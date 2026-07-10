from dataclasses import dataclass

# Material ids, shared by chunks and grid cells.
# Kept here (not in world_grid) so cell.py / world_grid.py can both import
# them without circular imports.
MATERIAL_AIR = 0
MATERIAL_WATER = 1
MATERIAL_SAND = 2


@dataclass(frozen=True)
class EnvFeatures:
    """A snapshot of the environment at one world position.

    Note the deliberate distinction between chunk-level and cell-level
    material: a sand *chunk* is mostly water cells with embedded sand
    blocks, so chunk_material can be SAND while cell_material is WATER.
    """
    depth: int            # lvl2 chunk y (0 = top of world)
    light_level: int      # 0-5, from the lvl2 chunk (WORLD_SHADER)
    chunk_material: int   # material of the lvl1 chunk the position is in
    cell_material: int    # material of the exact grid cell
    in_water: bool        # is the grid cell a WaterCell
    on_sand: bool         # is the grid cell directly below a SandCell
    surface_above: bool   # is the grid cell directly above an AirCell
    has_particles: bool   # does this region spawn food particles

    # room to grow: temperature, current, minerals, ...
