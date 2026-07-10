import random
import math
from dataclasses import dataclass
import pygame
from physics_object import *
from colors import *

WORLD_KEY = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2],[1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2],[1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2],[1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2],[1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2],[1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2],[1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]

WORLD_PARTICLES = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1],[0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0],[0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0],[0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0],[0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0],[0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0]]

WORLD_SHADER = [[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],[4,4,4,4,4,4,4,4,4,4,4,4,4,4,0,0],[4,4,4,4,4,4,4,4,4,0,0,0,0,0,0,0],[3,3,3,3,3,3,0,0,0,0,0,0,0,0,0,0],[3,3,3,3,3,0,0,0,0,0,0,0,0,0,0,0],[2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0],[2,2,2,2,0,0,0,0,0,0,0,0,0,0,0,0],[2,2,2,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]

WORLD_KEY2 = [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],[2,2,1,1,1,1,1,1,1,1,1,1,1,1,2,2],[2,2,2,1,1,1,1,1,1,1,1,1,2,2,2,2],[2,2,2,2,2,1,1,1,1,1,1,2,2,2,2,2],[2,2,2,2,2,2,1,1,1,1,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],[2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]]



MATERIALS =  {0: ('AIR', AIR),1: ('WATER', BLUE),2: ('SAND', SAND)}

WORLD_SIZE = 16
LVL4_CHUNK_SIZE = 2
LVL3_CHUNK_SIZE = 2
LVL2_CHUNK_SIZE = 2
LVL1_CHUNK_SIZE = 16
CELL_SIZE = 40

class World:
    def __init__(self):
        self.loaded_lvl1chunks = set()
        self.loaded_shapes = {}
        self.loaded_bodies = {}

        # (0,0) -> (15 , 15)
        self.lvl2chunks = {}

        #(0,0) -> (31, 31)
        self.lvl1chunks = {}

    def init_world(self):
        for x in range(WORLD_SIZE):
            for y in range(WORLD_SIZE):
                material = WORLD_KEY[y][x]
                # simple case for test, all compositions are the same as the cell type
                composition = [[material, material], [material, material]]
                self.lvl2chunks[(x,y)] = Level2Chunk((x,y), material, composition)
                self.lvl2chunks[(x,y)].light_level = WORLD_SHADER[y][x]
                if WORLD_PARTICLES[y][x] == 1:
                    self.lvl2chunks[(x, y)].has_particles = True

    def init_hit_boxes(self, space):
        for chunk in self.lvl1chunks:
            self.load_hit_boxes(space, chunk)

    def load_lvl2chunks(self):
        for x in range(WORLD_SIZE):
            for y in range(WORLD_SIZE):
                self.lvl2chunks[(x,y)].load_lvl2_chunk()
                for key in self.lvl2chunks[(x,y)].lvl1chunks:
                    cx = self.lvl2chunks[(x,y)].lvl1chunks[key].wx
                    cy = self.lvl2chunks[(x,y)].lvl1chunks[key].wy
                    self.lvl1chunks[(cx, cy)] = self.lvl2chunks[(x,y)].lvl1chunks[key]

    def load_chunks(self, entity_tile_pos, space):
        px, py = entity_tile_pos


        for dx in (px - 1, px, px + 1):
            for dy in (py - 1, py, py + 1):
                if dx < 0 or dy < 0 or dx > 31 or dy > 31:
                    continue
                if (dx,dy) not in self.loaded_lvl1chunks:
                    self.loaded_lvl1chunks.add((dx, dy))
                    #self.load_hit_boxes(space, (dx, dy))

    def load_hit_boxes(self, space, chunk):
        bodies = []
        shapes = []
        for material in self.lvl1chunks[chunk].materials:
            if isinstance(self.lvl1chunks[chunk].materials[material], SandCell):
                sand_cell = self.lvl1chunks[chunk].materials[material]
                sx, sy = sand_cell.wx * CELL_SIZE + CELL_SIZE/2, sand_cell.wy * CELL_SIZE + CELL_SIZE / 2
                body, shape = sand_body((sx, sy))
                space.add(body, shape)
                bodies.append(body)
                shapes.append(shape)

        self.loaded_bodies[chunk] = bodies
        self.loaded_shapes[chunk] = shapes

    def unload_distant_chunks(self, player_tile_pos, space):
        unload_dist = 2
        to_remove = set()

        for chunk in self.loaded_lvl1chunks:
            if self.dist(chunk, player_tile_pos) > unload_dist:
                to_remove.add(chunk)

        for chunk in to_remove:
            # self.clear_chunk(space, chunk)
            self.loaded_lvl1chunks.remove(chunk)

    def clear_chunk(self, space, chunk):
        space.remove(*self.loaded_bodies[chunk])
        space.remove(*self.loaded_shapes[chunk])

    def dist(self, chunk, player):
        cx, cy = chunk
        px, py = player
        rx = cx - px
        ry = cy - py

        return rx ** 2 + ry **2

    def world_to_lvl2_chunk(self, player_pos):
        x, y = player_pos
        c2x = int(x / CELL_SIZE / LVL1_CHUNK_SIZE / LVL2_CHUNK_SIZE)
        c2y = int(y / CELL_SIZE / LVL1_CHUNK_SIZE / LVL2_CHUNK_SIZE)
        return c2x, c2y

    def world_to_lvl1_chunk(self, player_pos):
        x, y = player_pos
        c1x = int(x / CELL_SIZE / LVL1_CHUNK_SIZE)
        c1y = int(y / CELL_SIZE / LVL1_CHUNK_SIZE)
        return c1x, c1y

    def world_to_grid_cell(self, position):
        x, y = position
        gcx = int(x / CELL_SIZE)
        gcy = int(y / CELL_SIZE)

        return gcx, gcy

    def get_lvl1_chunk_local_cell(self, cell_position):
        gx, gy = cell_position
        x, y = gx * CELL_SIZE, gy * CELL_SIZE
        c1x,c1y = self.world_to_lvl1_chunk((x,y))

        if c1x < 0 or c1y < 0 or c1x >31 or c1y > 31:
            chunk = None
        else:
            chunk = self.lvl1chunks[(c1x, c1y)]

        if chunk is None:
            return None #chunk not loaded

        local_x = gx % LVL1_CHUNK_SIZE
        local_y = gy % LVL1_CHUNK_SIZE

        if chunk.material == 0:
            return chunk.materials[(local_x, local_y)]

        else:
            return chunk.materials[(local_x, local_y)]



    def process(self, entity_pos, space):
        entity_tile_pos = self.world_to_lvl1_chunk(entity_pos)
        self.load_chunks(entity_tile_pos, space)
        self.unload_distant_chunks(entity_tile_pos, space)

    def render_chunks(self, surface, camera):
        zoom = camera.zoom
        ox, oy = camera.offset

        # hard coded for now
        screen_w, screen_h = (surface.get_size())

        cell_px = CELL_SIZE * zoom
        chunk_px = LVL1_CHUNK_SIZE * cell_px

        # visible chunk bounds
        min_cx = int((-ox) // chunk_px) - 1
        max_cx = int((screen_w - ox) // chunk_px) + 1
        min_cy = int((-oy // chunk_px) - 1)
        max_cy = int((screen_h - oy) // chunk_px) + 1

        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                if cx <0 or cy< 0:
                    continue
                if cx >= 32 or cy >= 32:
                    continue

                if 0.1 > zoom :
                    self.lvl2chunks[(cx//2, cy//2)].draw(surface, camera)
                else:
                    self.lvl1chunks[(cx, cy)].draw(surface, camera)

    def draw_loaded_chunks(self, surface, camera):
        for chunk in self.loaded_lvl1chunks:
            lvl1chunk = self.lvl1chunks[chunk]
            lvl1chunk.draw(surface,camera)

    def draw_chunk_bounds(self, surface, camera):

        zoom = camera.zoom
        ox, oy = camera.offset

        chunk_px = LVL2_CHUNK_SIZE * LVL1_CHUNK_SIZE * CELL_SIZE * zoom

        for (cx, cy) in self.lvl2chunks.keys():
            x = cx * chunk_px + ox
            y = cy * chunk_px + oy

            pygame.draw.rect(
                surface,
                (255, 0, 0),
                (x, y, chunk_px, chunk_px),
                1
            )

    def update_entity(self, entity):
        entity_grid_pos = self.world_to_grid_cell(entity.body.position)
        self.handle_grid_physics(entity, entity_grid_pos)
        entity_chunk_pos = self.world_to_lvl1_chunk(entity.body.position)
        if entity.last_chunk_pos != entity_chunk_pos:
            entity.last_chunk_pos = entity_chunk_pos

        if entity.last_grid_pos != entity_grid_pos:

            # remove entity from previous grid cell
            if entity.last_grid_pos is not None:
                old_cell = self.get_lvl1_chunk_local_cell(entity.last_grid_pos)
                if isinstance(old_cell, WaterCell):
                    old_cell.entities.remove(entity)

            # reset entity nearby objects
            entity.nearby_particles.clear()
            entity.nearby_entities.clear()

            # update entity position
            entity.last_grid_pos = entity_grid_pos
            entity.neighboring_grid_cells = entity.get_neighbor_grid_cells()

            # update current grid cell data
            cell = self.get_lvl1_chunk_local_cell(entity_grid_pos)
            if isinstance(cell, WaterCell):
                cell.entities.append(entity)

            # get objects in entity neighbors
            entity.get_nearby_objects(self)

    def handle_grid_physics(self, entity, grid_pos):
        self.air_ontop_water_phys(entity, grid_pos)

    def air_ontop_water_phys(self, entity, grid_pos):
        cell = self.get_lvl1_chunk_local_cell(grid_pos)
        if isinstance(cell, WaterCell):
            above_cell = self.get_lvl1_chunk_local_cell((grid_pos[0], grid_pos[1]-1))
            if isinstance(above_cell, AirCell):
                # dampen cell velocity to prevent it from crossing water air boundary
                if entity.body.velocity.y < 1:
                    entity.body.velocity = entity.body.velocity.x, min(0, entity.body.velocity.y + 0.5)

        if isinstance(cell, AirCell):
            entity.body.velocity = entity.body.velocity.x, entity.body.velocity.y + 98.1

class Level2Chunk:
    def __init__(self, world_pos, material, composition):# 0 - 16
        self.world_pos = world_pos
        self.wx, self.wy = world_pos
        self.material = material
        self.composition = composition

        self.material_name, self.material_color = MATERIALS[material]
        self.lvl1chunks = {}

        self.light_level = 0
        self.has_particles = False

    def load_lvl2_chunk(self):
        for x in range(LVL2_CHUNK_SIZE):
            for y in range(LVL2_CHUNK_SIZE):
                material = self.composition[y][x]
                cx = (self.wx + x / LVL2_CHUNK_SIZE) * LVL2_CHUNK_SIZE
                cy = (self.wy + y / LVL2_CHUNK_SIZE) * LVL2_CHUNK_SIZE
                self.lvl1chunks[(x, y)] = Level1Chunk((cx, cy), material, self.has_particles)

    def draw(self, surface, camera):
        zoom = camera.zoom
        ox, oy = camera.offset

        if self.light_level == 5:
            color = (255 , 0 , 0)

        elif self.light_level == 4:
            color = (200, 0 , 0)

        elif self.light_level == 3:
            color = (150, 0 ,0)

        elif self.light_level == 2:
            color = (100 , 0 ,0 )

        else:
            color = (0, 255, 0)
        # 15 * 2 * 2 * 20 = 1200 = chunk world x (top right corner)
        chunk_world_x = self.wx * LVL2_CHUNK_SIZE * LVL1_CHUNK_SIZE * CELL_SIZE
        chunk_world_y = self.wy * LVL2_CHUNK_SIZE * LVL1_CHUNK_SIZE * CELL_SIZE

        chunk_pixel_size = LVL2_CHUNK_SIZE * LVL1_CHUNK_SIZE * CELL_SIZE * zoom

        pygame.draw.rect(
            surface,
            self.material_color,
            (
                chunk_world_x * zoom + ox,
                chunk_world_y * zoom + oy,
                chunk_pixel_size,
                chunk_pixel_size
            ),
            1
        )

        # for c1x in range(LVL2_CHUNK_SIZE):
        #     for c1y in range(LVL2_CHUNK_SIZE):
        #         lvl1chunk = self.lvl1chunks[(c1x, c1y)]
        #         lvl1chunk.draw(surface, camera)

class Level1Chunk:
    def __init__(self, world_pos, material, has_particles):# 0 - 32
        self.world_pos = world_pos
        self.wx, self.wy = world_pos

        self.material = material

        self.material_name, self.material_color = MATERIALS[material]
        self.materials = {}
        self.has_particles = has_particles

        self.init_grid()

    def init_grid(self):
            # Air
            if self.material == 0:
                for x in range(LVL1_CHUNK_SIZE):
                    for y in range(LVL1_CHUNK_SIZE):
                        # x, y: values from 0 -> 15
                        cx = (self.wx + x / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                        cy = (self.wy + y / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                        cell = AirCell((cx, cy))
                        cell.entities = []
                        # cell.create_particles(self.chunk_x, self.chunk_y)
                        self.materials[(x, y)] = cell

            # Water
            elif self.material == 1:
                for x in range(LVL1_CHUNK_SIZE):
                    for y in range(LVL1_CHUNK_SIZE):
                        # x, y: values from 0 -> 15
                        cx = (self.wx + x / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                        cy = (self.wy + y / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                        cell = WaterCell((cx,cy))
                        cell.particle_count = 3
                        if self.has_particles:
                            cell.create_particles()
                        cell.entities = []
                        #cell.create_particles(self.chunk_x, self.chunk_y)
                        self.materials[(x, y)] = cell

            # Sand
            elif self.material == 2:
                for x in range(LVL1_CHUNK_SIZE):
                    for y in range(LVL1_CHUNK_SIZE):
                        cx = (self.wx + x / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                        cy = (self.wy + y / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                        cell = WaterCell((cx, cy))
                        cell.particle_count = 3
                        if self.has_particles:
                            cell.create_particles()
                        cell.entities = []
                        self.materials[(x, y)] = cell
                self.generate_sand_cell()

            else:
                pass

    def generate_sand_cell(self):
        import random

        REGION_SIZE = 4
        BLOCK_SIZE = 2

        for rx in range(0, LVL1_CHUNK_SIZE, REGION_SIZE):
            for ry in range(0, LVL1_CHUNK_SIZE, REGION_SIZE):

                local_positions = [
                    (x, y)
                    for x in range(rx, rx + REGION_SIZE - BLOCK_SIZE + 1)
                    for y in range(ry, ry + REGION_SIZE - BLOCK_SIZE + 1)
                ]

                x, y = random.choice(local_positions)

                offsets = [(0,0), (1,0), (0,1), (1,1)]

                for dx, dy in offsets:
                    lx, ly = x + dx, y + dy
                    # 0 - 15
                    cx = (self.wx + lx / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                    cy = (self.wy + ly / LVL1_CHUNK_SIZE) * LVL1_CHUNK_SIZE
                    self.materials[(lx, ly)] = SandCell((cx, cy))

    def draw(self, surface, camera):
        zoom = camera.zoom
        ox, oy = camera.offset

        # 15 * 2 * 2 * 20 = 1200 = chunk world x (top right corner)
        chunk_world_x = self.wx * LVL1_CHUNK_SIZE * CELL_SIZE
        chunk_world_y = self.wy * LVL1_CHUNK_SIZE * CELL_SIZE

        chunk_pixel_size = LVL1_CHUNK_SIZE * CELL_SIZE * zoom

        if 0.10 < zoom < 0.5:
            pygame.draw.rect(
                surface,
                self.material_color,
                (
                    chunk_world_x * zoom + ox,
                    chunk_world_y * zoom + oy,
                    chunk_pixel_size,
                    chunk_pixel_size
                ),
                1
            )

        if zoom > 0.50:
            for bx in range(LVL1_CHUNK_SIZE):
                for by in range(LVL1_CHUNK_SIZE):
                    if not self.materials:
                        pass
                    else:
                        material = self.materials[(bx, by)]
                        material.draw(surface, camera)

class AirCell:
    def __init__(self, world_pos):
        self.wx, self.wy = world_pos
        self.color = AIR
        self.density = 1

        self.entities = []

    def draw(self, surface, camera):
        zoom = camera.zoom
        ox, oy = camera.offset

        # 15 * 2 * 2 * 20 = 1200 = chunk world x (top right corner)
        chunk_world_x = self.wx * CELL_SIZE
        chunk_world_y = self.wy * CELL_SIZE

        chunk_pixel_size = CELL_SIZE * zoom

        pygame.draw.rect(
            surface,
            self.color,
            (
                chunk_world_x * zoom + ox,
                chunk_world_y * zoom + oy,
                chunk_pixel_size,
                chunk_pixel_size
            ),
            1
        )

class SandCell:
    def __init__(self, world_pos):
        self.wx, self.wy = world_pos
        self.density = 1500
        self.color = SAND
        # TODO: Remove later
        self.entities = []

    def draw(self, surface, camera):
        zoom = camera.zoom
        ox, oy = camera.offset

        # 15 * 2 * 2 * 20 = 1200 = chunk world x (top right corner)
        chunk_world_x = self.wx * CELL_SIZE
        chunk_world_y = self.wy * CELL_SIZE

        chunk_pixel_size = CELL_SIZE * zoom

        pygame.draw.rect(
            surface,
            self.color,
            (
                chunk_world_x * zoom + ox,
                chunk_world_y * zoom + oy,
                chunk_pixel_size,
                chunk_pixel_size
            ),
            1
        )

class WaterCell:
    def __init__(self, world_pos, particle_count: int = 0):# 0 - 15
        self.wx, self.wy = world_pos
        self.density = 1000

        self.particle_count = particle_count
        self.particles = []

        self.entities = []

        self.color = BLUE

    def create_particles(self):
        PADDING = 10
        for _ in range(self.particle_count):
            px = int(
                self.wx * CELL_SIZE +
                PADDING +
                random.random() * (CELL_SIZE - 2 * PADDING)
            )
            py = int(
                self.wy * CELL_SIZE +
                PADDING +
                random.random() * (CELL_SIZE - 2 * PADDING)
            )

            self.particles.append(Particle((px, py), 0))

    def spawn_particle(self):
        PADDING = 10
        px = int(
            self.wx * CELL_SIZE +
            PADDING +
            random.random() * (CELL_SIZE - 2 * PADDING)
        )
        py = int(
            self.wy * CELL_SIZE +
            PADDING +
            random.random() * (CELL_SIZE - 2 * PADDING)
        )
        self.particles.append(Particle((px, py), 0))

    def add_particle(self, particle):
        self.particles.append(particle)

    def draw(self, surface, camera):
        zoom = camera.zoom
        ox, oy = camera.offset

        # 15 * 2 * 2 * 20 = 1200 = chunk world x (top right corner)
        chunk_world_x = self.wx * CELL_SIZE
        chunk_world_y = self.wy * CELL_SIZE

        chunk_pixel_size = CELL_SIZE * zoom

        pygame.draw.rect(
            surface,
            self.color,
            (
                chunk_world_x * zoom + ox,
                chunk_world_y * zoom + oy,
                chunk_pixel_size,
                chunk_pixel_size
            ),
            1
        )

        for p in self.particles:
            p.draw_at(surface, ox, oy, zoom)

class Particle:
    def __init__(self, world_pos, type = 0):
        self.x, self.y = world_pos
        self.type = type

        if type == 0:
            self.multiplier = 1
            self.radius = 2
            self.color = TEAL

        elif type == 1:
            self.multiplier = 5
            self.radius = 5
            self.color = MAGENTA

        else:
            self.multiplier = 0
            self.radius = 0
            self.color = (0, 0, 0)

    def draw_at(self, surface, ox, oy, zoom):
        sx = self.x * zoom + ox
        sy = self.y * zoom + oy

        pygame.draw.circle(
            surface,
            self.color,
            (int(sx), int(sy)),
            self.radius*zoom, 1
        )