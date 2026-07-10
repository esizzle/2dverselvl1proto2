import copy
import uuid

import pygame
import math
import random
import pymunk

from colors import GREEN, BLACK, LIME, ORANGE, RED
from env_features import EnvFeatures
from physics_object import *
from world_grid import WaterCell, Particle


class Genome:
    def __init__(self, max_mass=20, acceleration=40, max_speed=40, efficiency_factor=1):
        self.acceleration = acceleration
        self.max_speed = max_speed
        self.max_mass = max_mass
        self.size = max_mass // 2

        self.efficiency_factor = efficiency_factor

        self.mutation_rate = 0.25

        # visual traits
        self.color = (255, 255, 255)

        # boolean mutations
        self.has_cell_wall = False
        self.has_chloroplast = False

        # hard coded bounds
        # max_mass 10 -> 80
        self.mass_range = [10, 80]
        # max_speed 20 -> 240
        self.speed_range = [20, 240]
        # max_size 5 -> 40
        self.size_range = [5,40]

    def mutate_gene(self, env: EnvFeatures, cell):
        """Mutate this genome based on the environment (env) and the parent
        cell's lifetime state (movement history, diet)."""

        # mutate size: size increases in less material dense areas, and decreases in more material dense areas
        if env.chunk_material == 1:
            if random.random() < self.mutation_rate:
                # self.size += random.choice([1, 2, 3, 4])
                # self.size = max(self.size_range[0], min(self.size, self.size_range[1]))
                self.max_mass += random.choice([2, 4, 6, 8])
                self.max_mass = max(self.mass_range[0], min(self.max_mass, self.mass_range[1]))
                self.size = self.max_mass//2

        if env.chunk_material == 2:
            if random.random() < self.mutation_rate:
                # self.size -= random.choice([1, 2, 3, 4])
                # self.size = max(self.size_range[0], min(self.size, self.size_range[1]))
                self.max_mass -= random.choice([2, 4, 6, 8])
                self.max_mass = max(self.mass_range[0], min(self.max_mass, self.mass_range[1]))
                self.size = self.max_mass//2

        # TODO: Add less particles to less nutrient dense areas, so cells can still eat and mutate within them
        #  For now lets just leave mass and size coupled
        # mutate mass: mass decreases in less nutrient dense areas, and increases in more nutrient dense areas.
        # if env.has_particles:
        #     if random.random() < self.mutation_rate:
        #         self.max_mass += random.choice([2, 4, 6, 8])
        #         self.max_mass = max(self.mass_range[0], min(self.max_mass, self.mass_range[1]))
        #
        #
        # if not env.has_particles:
        #     if random.random() < self.mutation_rate:
        #         self.max_mass -= random.choice([2, 4, 6, 8])
        #         self.max_mass = max(self.mass_range[0], min(self.max_mass, self.mass_range[1]))

        # mutate speed: each type-1 particle eaten is a chance at more speed
        for _ in range(cell.amt_type1_particles):
            if random.random() < self.mutation_rate:
                self.max_speed = min(self.max_speed + 5, self.speed_range[1])

        self.acceleration = self.max_speed

        # mutate cell wall: only cells that never moved can evolve one
        if not cell.has_moved:
            if random.random() < self.mutation_rate:
                self.has_cell_wall = True

        # mutate chloroplast: needs a wall, water, and bright light
        # (light_level >= 4 replaces the old hardcoded c2y == 8 check)
        if self.has_cell_wall and not self.has_chloroplast:
            if env.in_water and env.light_level >= 4:
                if random.random() < self.mutation_rate:
                    self.has_chloroplast = True
                    self.color = LIME

        # algae color adapts to depth, mirroring real light absorption:
        # green near the surface, brown mid-depth, red in the deep
        if self.has_chloroplast:
            if env.depth in (8, 9):
                if random.random() < self.mutation_rate:
                    self.color = LIME

            elif env.depth in (10, 11):
                if random.random() < self.mutation_rate:
                    self.color = ORANGE

            elif 12 <= env.depth <= 15:
                if random.random() < self.mutation_rate:
                    self.color = RED


class Cell:
    def __init__(self, position: tuple, genome: Genome, is_player=False):
        self.mass = genome.max_mass / 2
        self.max_mass = genome.max_mass
        self.energy = 5000 * self.mass
        self.max_energy = 5000 * self.max_mass
        self.size = genome.size
        self.acceleration = genome.acceleration
        self.max_speed = genome.max_speed
        self.efficiency_factor = genome.efficiency_factor

        # visual traits
        self.color = genome.color

        self.genome = genome

        # world tracking
        self.last_chunk_pos = None
        self.last_grid_pos = None
        self.neighboring_grid_cells = []

        # food
        self.nearby_particles = []
        self.nearby_entities = []
        self.amt_type1_particles = 0

        # booleans
        self.is_dead = False
        self.has_split = False
        self.is_player = is_player
        self.has_moved = False

        # mutation booleans
        self.has_cell_wall = genome.has_cell_wall
        self.has_chloroplast = genome.has_chloroplast

        # physics
        self.body, self.shape = init_cell_physics(
            self.mass, self.size, position, self.has_cell_wall
        )
        self.shape._object = self

        # object tracking
        self.id = uuid.uuid4()
        self.contact_time = {}

    # ------------------------------------------------------------------
    # Energy
    # ------------------------------------------------------------------
    def add_energy(self, amount):
        """Single place where energy changes, so max_energy is always
        respected. Negative amounts spend energy (starvation is checked
        against <= 0 in the game loop)."""
        self.energy = min(self.energy + amount, self.max_energy)

    def _movement_cost(self):
        return self.mass * self.acceleration * self.efficiency_factor

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def handle_input(self, events, keys):

        # disable movement if the cell has a cell wall
        if not self.has_cell_wall:
            # this should create a glitch in some cases where when you add the velocity the cell
            # reaches a greater speed than its max_speed
            # for now we call this a feature, not a bug
            if keys[pygame.K_a]:
                if self.body.velocity.x > -self.max_speed:
                    self.body.velocity = self.body.velocity.x - self.acceleration, self.body.velocity.y
                else:
                    self.body.velocity = -self.max_speed, self.body.velocity.y

                self.add_energy(-self._movement_cost())
                self.has_moved = True

            if keys[pygame.K_d]:
                if self.body.velocity.x < self.max_speed:
                    self.body.velocity = self.body.velocity.x + self.acceleration, self.body.velocity.y
                else:
                    self.body.velocity = self.max_speed, self.body.velocity.y

                self.add_energy(-self._movement_cost())
                self.has_moved = True

            if keys[pygame.K_w]:
                if self.body.velocity.y > -self.max_speed:
                    self.body.velocity = self.body.velocity.x, self.body.velocity.y - self.acceleration
                else:
                    self.body.velocity = self.body.velocity.x, -self.max_speed

                self.add_energy(-self._movement_cost())
                self.has_moved = True

            if keys[pygame.K_s]:
                if self.body.velocity.y < self.max_speed:
                    self.body.velocity = self.body.velocity.x, self.body.velocity.y + self.acceleration
                else:
                    self.body.velocity = self.body.velocity.x, self.max_speed

                self.add_energy(-self._movement_cost())
                self.has_moved = True

        if keys[pygame.K_k]:
            self.is_dead = True

    # ------------------------------------------------------------------
    # World queries
    # ------------------------------------------------------------------
    def get_neighbor_grid_cells(self):
        gx, gy = self.last_grid_pos

        return [
            (gx + dx, gy + dy)
            for dx in (-1, 0, 1)
            for dy in (-1, 0, 1)
        ]

    def get_nearby_objects(self, world):
        for gx, gy in self.neighboring_grid_cells:
            cell = world.get_lvl1_chunk_local_cell((gx, gy))
            if cell and isinstance(cell, WaterCell):
                self.nearby_particles.extend(cell.particles)
                self.nearby_entities.extend(cell.entities)

    # ------------------------------------------------------------------
    # Eating
    # ------------------------------------------------------------------
    def consume_particle(self, particle, removal_list):
        dx = particle.x - self.body.position.x
        dy = particle.y - self.body.position.y

        if dx * dx + dy * dy <= self.size * self.size:
            self.add_energy(1000 * particle.multiplier)
            self.mass += 1 * particle.multiplier
            if self.mass >= self.max_mass:
                self.mass = self.max_mass
                self.add_energy(4000 * particle.multiplier)

            removal_list.append(particle)
            if particle in self.nearby_particles:
                self.nearby_particles.remove(particle)
            if particle.type == 1:
                self.amt_type1_particles += 1

    def consume_cell(self, cell):
        if cell is self:
            return
        if not cell.has_cell_wall:
            dx = cell.body.position.x - self.body.position.x
            dy = cell.body.position.y - self.body.position.y

            d_squared = dx ** 2 + dy ** 2
            # within cell radius
            if d_squared + cell.size ** 2 <= self.size ** 2:
                cell.is_dead = True

    # TODO: Turn INTO MUTATION
    def convert_mass_to_energy(self):
        self.mass -= 1
        self.add_energy(5000)
        if self.mass <= 0:
            self.is_dead = True

    # ------------------------------------------------------------------
    # Reproduction / death
    # ------------------------------------------------------------------
    def split(self, space, cell_list, env: EnvFeatures):
        # clone genome, mutating each child based on the local environment
        new_genome1 = copy.deepcopy(self.genome)
        new_genome2 = copy.deepcopy(self.genome)
        new_genome1.mutate_gene(env, self)
        new_genome2.mutate_gene(env, self)

        # dynamic spawn positions
        a = -1 if self.body.velocity.x < 0 else 1

        # spawn cells: child 1 inherits player control
        new_cell1 = Cell(
            (self.body.position.x + a * new_genome1.size, self.body.position.y),
            new_genome1,
            self.is_player,
        )
        new_cell2 = Cell(
            (self.body.position.x - a * new_genome2.size, self.body.position.y),
            new_genome2,
            False,
        )

        # configure cell pymunk settings
        space.add(new_cell1.body, new_cell1.shape)
        space.add(new_cell2.body, new_cell2.shape)

        new_cell1.body.velocity = self.body.velocity.x, self.body.velocity.y
        new_cell2.body.velocity = -self.body.velocity.x, self.body.velocity.y

        # add new cells to game cell list
        cell_list.extend([new_cell1, new_cell2])

        # prepare current cell for deletion
        self.is_player = False
        self.has_split = True
        self.is_dead = True

    def cell_death(self, world):
        # from cell mass get amount of large (5x) particles and small particles
        num_large_particles = int(self.mass // 5)
        num_small_particles = int(self.mass % 5)
        total = num_small_particles + num_large_particles

        if total == 0:
            return

        choices = [0] * num_small_particles + [1] * num_large_particles

        # spawn particles around radius of dead cell
        for i in range(total):
            rx = self.size * math.cos(2 * i * math.pi / total)
            ry = self.size * math.sin(2 * i * math.pi / total)

            wx = self.body.position.x + rx
            wy = self.body.position.y + ry
            choice = random.choice(choices)
            choices.remove(choice)

            particle = Particle((wx, wy), choice)

            # get water cell at world position
            gx, gy = world.world_to_grid_cell((wx, wy))

            # get local cell inside chunk
            cell = world.get_lvl1_chunk_local_cell((gx, gy))

            if isinstance(cell, WaterCell):
                cell.add_particle(particle)
            else:
                print("Error, could not find Water Cell!")

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def draw(self, surface, zoom_factor=1.0, offset=(0, 0)):
        x = self.body.position[0] * zoom_factor + offset[0]
        y = self.body.position[1] * zoom_factor + offset[1]

        if self.has_cell_wall:
            # tl, w, h
            rect = (
                (x - self.size * zoom_factor, y - self.size * zoom_factor),
                (self.size * 2 * zoom_factor, self.size * 2 * zoom_factor),
            )
            pygame.draw.rect(surface, BLACK, rect)
            pygame.draw.rect(surface, self.color, rect, 1)

        else:
            pygame.draw.circle(surface, BLACK, (x, y), self.size * zoom_factor)
            pygame.draw.circle(surface, self.color, (x, y), self.size * zoom_factor, 1)
