import copy
import uuid

import pygame
import math
import random
import pymunk

from colors import GREEN, BLACK, LIME, ORANGE, RED
from functions import distance_squared, world_to_lvl2_chunk
from physics_object import *
from world_grid import WaterCell, Particle




class Genome:
    def __init__(self, max_mass = 20, acceleration = 40, max_speed = 40, efficiency_factor = 1):
        self.acceleration = acceleration
        self.max_speed = max_speed
        self.max_mass = max_mass
        self.size = max_mass//2

        self.efficiency_factor = efficiency_factor

        self.mutation_rate = 0.1

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

    def mutate_gene(self, previous_inputs, c2y, amt_type1_particles):
        # mutate mass
        if random.random() < self.mutation_rate:
            self.max_mass += random.choice([-2,2,4,6,8])
            if self.max_mass < self.mass_range[0]:
                self.max_mass = self.mass_range[0]
            if self.max_mass > self.mass_range[1]:
                self.max_mass = self.mass_range[1]
            self.size = self.max_mass//2

        # mutate speed:
        for i in range(amt_type1_particles):
            if random.random() < self.mutation_rate:
                self.max_speed += 5
                if self.max_speed > self.speed_range[1]:
                    self.max_speed = self.speed_range[1]

        self.acceleration = self.max_speed



        # mutate cell wall
        if not previous_inputs:
            if random.random() < self.mutation_rate:
                self.has_cell_wall = True

        # mutate chloroplast
        if self.has_cell_wall:
            if c2y == 8:
                if random.random() < self.mutation_rate:
                    self.has_chloroplast = True
                    self.color = LIME

        if self.has_chloroplast:
            # hard coded values for now
            # green algae
            if c2y == 8 or c2y == 9:
                if random.random() < self.mutation_rate:
                    self.color = LIME

            # brown algae
            if c2y == 10 or c2y == 11:
                if random.random() < self.mutation_rate:
                    self.color = ORANGE

            # red algae
            if c2y == 12 or c2y == 13 or c2y == 14 or c2y == 15:
                if random.random() < self.mutation_rate:
                    self.color = RED

class Cell:
    def __init__(self, position: tuple, genome: Genome, is_player = False):
        self.mass = genome.max_mass/2
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

        # mutation booleans
        self.has_cell_wall = genome.has_cell_wall
        self.has_chloroplast = genome.has_chloroplast

        # physics
        self.body, self.shape = init_cell_physics(
            self.mass, self.size, position, self.has_cell_wall
        )
        self.shape._object = self

        # input tracking
        self.previous_inputs = []

        # object tracking
        self.id = uuid.uuid4()
        self.contact_time = {}


    def handle_input(self, events, keys):

        # disable movement if the cell has a cell wall
        if self.has_cell_wall:
            pass
        else:
            # this should create a glitch in some cases where when you add the velocity the cell
            # reaches a greater speed than its max_speed
            # for now we call this a feature, not a bug
            if keys[pygame.K_a]:
                #dprint(self.body.velocity.x)
                if self.body.velocity.x > -self.max_speed:
                    self.body.velocity = self.body.velocity.x - self.acceleration, self.body.velocity.y
                else:
                    self.body.velocity = -self.max_speed, self.body.velocity.y

                # spend energy for input
                self.energy -= self.mass*self.acceleration*self.efficiency_factor
                self.previous_inputs.append("left")

            if keys[pygame.K_d]:
                if self.body.velocity.x < self.max_speed:
                    self.body.velocity = self.body.velocity.x + self.acceleration, self.body.velocity.y
                else:
                    self.body.velocity = self.max_speed, self.body.velocity.y

                # spend energy for input
                self.energy -= self.mass * self.acceleration * self.efficiency_factor
                self.previous_inputs.append("right")

            if keys[pygame.K_w]:
                if self.body.velocity.y > -self.max_speed:
                    self.body.velocity = self.body.velocity.x, self.body.velocity.y - self.acceleration
                else:
                    self.body.velocity = self.body.velocity.x, -self.max_speed

                # spend energy for input
                self.energy -= self.mass * self.acceleration * self.efficiency_factor
                self.previous_inputs.append("up")

            if keys[pygame.K_s]:
                if self.body.velocity.y < self.max_speed:
                    self.body.velocity = self.body.velocity.x, self.body.velocity.y + self.acceleration

                else:
                    self.body.velocity = self.body.velocity.x, self.max_speed

                # spend energy for input
                self.energy -= self.mass * self.acceleration * self.efficiency_factor
                self.previous_inputs.append("down")

        if keys[pygame.K_k]:
            self.is_dead = True

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

    def consume_particle(self, particle, removal_list):
        dx = particle.x - self.body.position.x
        dy = particle.y - self.body.position.y

        if dx * dx + dy * dy <= self.size * self.size:
            self.energy += 1000 * particle.multiplier
            self.mass += 1 * particle.multiplier
            if self.mass >= self.max_mass:
                self.mass = self.max_mass
                self.energy += 4000 * particle.multiplier

            removal_list.append(particle)
            self.nearby_particles.remove(particle)
            if particle.type == 1:
                self.amt_type1_particles += 1


    def consume_cell(self, cell):
        if cell is self:
            pass
        else:
            if not cell.has_cell_wall:
                dx = cell.body.position.x - self.body.position.x
                dy = cell.body.position.y - self.body.position.y

                d_squared = dx**2 + dy**2
                # within cell radius
                if d_squared + cell.size ** 2 <= self.size ** 2:
                        cell.is_dead = True


    #TODO: Turn INTO MUTATION
    def convert_mass_to_energy(self):
        self.mass -= 1
        self.energy += 5000
        if self.mass <= 0:
            self.is_dead = True

    def split(self, space, cell_list):
        # chunk position
        c2x, c2y = world_to_lvl2_chunk(self.body.position)

        # clone genome
        new_genome1 = copy.deepcopy(self.genome)
        new_genome2 = copy.deepcopy(self.genome)
        new_genome1.mutate_gene(self.previous_inputs, c2y, self.amt_type1_particles)
        new_genome2.mutate_gene(self.previous_inputs, c2y, self.amt_type1_particles)

        # dynamic spawn positions
        a = 0
        if self.body.velocity.x < 0:
            a = -1
        else:
            a = 1

        # spawn cell
        if self.is_player:
            new_cell1 = Cell((self.body.position.x + a*new_genome1.size, self.body.position.y), new_genome1, True)
        else:
            new_cell1 = Cell((self.body.position.x + a*new_genome1.size, self.body.position.y), new_genome1, False)
        new_cell2 = Cell((self.body.position.x - a*new_genome2.size, self.body.position.y), new_genome2, False)

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

        choices = []

        for i in range(num_small_particles):
            choices.append(0)

        for i in range(num_large_particles):
            choices.append(1)
        # spawn particles around radius of dead cell
        for i in range(num_small_particles + num_large_particles):
            rx = self.size * math.cos(2 * i * math.pi/ (num_small_particles + num_large_particles))
            ry = self.size * math.sin(2 * i * math.pi/ (num_small_particles + num_large_particles))

            wx = self.body.position.x + rx
            wy = self.body.position.y + ry
            choice = random.choice(choices)
            choices.remove(choice)

            if choice == 0:
                particle = Particle((wx, wy), 0)

            elif choice == 1:
                particle = Particle((wx, wy), 1)

            else:
                particle = None

            # get water cell at world position
            gx, gy = world.world_to_grid_cell((wx, wy))

            # get local cell inside chunk
            cell = world.get_lvl1_chunk_local_cell((gx, gy))

            if isinstance(cell, WaterCell):
                cell.add_particle(particle)

            else:
                print("Error, could not find Water Cell!")

    def draw(self, surface, zoom_factor = 1.0, offset=(0, 0)):
        if self.has_cell_wall:
            x, y = self.body.position[0] * zoom_factor + offset[0], self.body.position[1] * zoom_factor + offset[1]
            # tl, w, h
            rect = ((x - self.size*zoom_factor,y - self.size*zoom_factor), (self.size*2*zoom_factor, self.size*2*zoom_factor))
            pygame.draw.rect(surface, BLACK, rect)
            pygame.draw.rect(surface, self.color, rect, 1)

        else:
            x, y = self.body.position[0]*zoom_factor + offset[0], self.body.position[1]*zoom_factor + offset[1]
            pygame.draw.circle(surface, BLACK, (x, y), self.size * zoom_factor)
            pygame.draw.circle(surface, self.color, (x, y), self.size*zoom_factor, 1)
