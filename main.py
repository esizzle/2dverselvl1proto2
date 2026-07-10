from turtledemo.nim import SCREENWIDTH

import pygame
import pymunk
from world_grid import *
from camera import *
from player import *
from colors import *

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
WORLD_WINDOW_WIDTH = 600
WORLD_WINDOW_HEIGHT = 600
STAT_BOX_W = 200
STAT_BOX_H = 300
MUT_BOX_W = 200
MUT_BOX_H = 200
SPECIES_BOX_W = 200
SPECIES_BOX_H = 600

class Game:
    def __init__(self):
        self.screen, self.clock = self.init_pygame()
        self.world_surface = pygame.Surface((WORLD_WINDOW_WIDTH, WORLD_WINDOW_HEIGHT))
        self.stat_box_surface = pygame.Surface((STAT_BOX_W, STAT_BOX_H))
        self.mut_box_surface = pygame.Surface((MUT_BOX_W, MUT_BOX_H))
        self.species_box_surface = pygame.Surface((SPECIES_BOX_W, SPECIES_BOX_H))

        self.font = pygame.font.SysFont("Arcade_Classic", 18)

        # World (chunk-based)
        self.world = World()
        self.world.init_world()
        self.world.load_lvl2chunks()

        # Physicis Space
        self.space = pymunk.Space()
        self.world.init_hit_boxes(self.space)

        # handle collisions between carnivorous cells and cells with cell walls
        self.handler = self.space.add_collision_handler(1, 2)
        self.handler.begin = self.on_cell_begin
        self.handler.separate = self.on_cell_separate

        self.camera = Camera(type=0)

        self.player = Player((11500, 11500), self.space)

        # mutations tracking
        self.previous_genome = self.player.cell.genome
        self.increased = []
        self.decreased = []

        self.cells = []
        self.cells.append(self.player.cell)
        self.previous_cell_length = 1

        pos = self.world.world_to_lvl1_chunk(self.player.cell.body.position)
        self.world.load_chunks(pos, self.space)

        self.to_remove_particles = []
        self.running = True

    def init_pygame(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        return screen, clock

    def handle_inputs(self):
        # inputs
        events = pygame.event.get()
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        world_mouse = (
            (mouse_pos[0] - self.camera.offset[0]) / self.camera.zoom,
            (mouse_pos[1] - self.camera.offset[1]) / self.camera.zoom
        )
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

        # camera inputs
        self.camera.handle_input(events, keys)
        # player inputs
        for cell in self.cells:
            if cell.is_player:
                cell.handle_input(events, keys)

    def on_cell_begin(self, arbiter, space, data):
        a, b = arbiter.shapes
        predator_cell = a._object
        prey_cell = b._object

        predator_cell.contact_time[prey_cell] = 0.0
        return True

    def on_cell_separate(self, arbiter, space, data):
        a, b = arbiter.shapes
        predator_cell = a._object
        prey_cell = b._object

        predator_cell.contact_time.pop(prey_cell, None)

    def draw_stat_bar(self, player_stat, player_max_stat, stat_name, units, height, buffer = 1):
        stat_width = player_stat * 120 / player_max_stat
        pygame.draw.rect(self.stat_box_surface, (255, 0, 0), (70, height, STAT_BOX_W - 80, 10), 1)
        pygame.draw.rect(self.stat_box_surface, (255, 0, 0), (70, height, stat_width, 10))
        stat_bar = self.font.render(stat_name + ":", True, (255, 255, 255))
        stat_fraction = self.font.render(
            f"{player_stat // buffer} {units} / {player_max_stat // buffer} {units}",
            True,
            (255, 255, 255))
        self.stat_box_surface.blit(stat_bar, (10, height))
        self.stat_box_surface.blit(stat_fraction, (100, height + 15))


    def draw_stat_box(self):
        self.stat_box_surface.fill(BLACK)

        # Mass
        self.draw_stat_bar(self.player.cell.mass, self.player.cell.max_mass, "MASS", "pg", 25)

        # Energy
        self.draw_stat_bar(self.player.cell.energy, self.player.cell.max_energy, "ENERGY", "nJ", 62 ,1000)

        # OUTLINE
        pygame.draw.rect(self.stat_box_surface, (255, 255, 255), (0, 0, STAT_BOX_W, STAT_BOX_H), 1)

        self.screen.blit(self.stat_box_surface, ((SCREEN_WIDTH + WORLD_WINDOW_WIDTH)//2 + 20, (SCREEN_HEIGHT - WORLD_WINDOW_HEIGHT)//2))

    def draw_mut_box(self):
        self.mut_box_surface.fill(BLACK)
        # WORLD BOX
        pygame.draw.rect(self.mut_box_surface, (255, 255, 255), (0, 0, MUT_BOX_W, MUT_BOX_H), 1)


        if self.player.cell.genome is not self.previous_genome:
            self.increased.clear()
            self.decreased.clear()
            # acceleration = self.player.cell.genome.acceleration - self.previous_genome.acceleration
            # acceleration = self.player.cell.genome.max_speed - self.previous_genome.max_speed
            max_mass = self.player.cell.genome.max_mass - self.previous_genome.max_mass
            if max_mass != 0:
                if max_mass > 0:
                    self.increased.append("MAX MASS")

                else:
                    self.decreased.append("MAX MASS")

            size = self.player.cell.genome.size - self.previous_genome.size
            if size != 0:
                if size > 0:
                    self.increased.append("SIZE")

                else:
                    self.decreased.append("SIZE")

            speed = self.player.cell.genome.max_speed - self.previous_genome.max_speed
            if speed != 0:
                if speed > 0:
                    self.increased.append("SPEED")

                else:
                    self.decreased.append("SPEED")

            if self.player.cell.genome.has_cell_wall != self.previous_genome.has_cell_wall:
                if self.player.cell.genome.has_cell_wall:
                    self.increased.append("EVOLVED CELL WALL")
                    self.decreased.append("CAN NO LONGER MOVE"
                                          "")
            self.previous_genome = self.player.cell.genome

        for i in range(len(self.increased)):
            text = self.font.render("+ " + self.increased[i], True, (0, 255, 0))
            self.mut_box_surface.blit(text, (10, 25*(i + 1)))

        for j in range(len(self.decreased)):
            text = self.font.render("- " + self.decreased[j], True, (255, 0, 0))
            self.mut_box_surface.blit(text, (10, 25*(j + 1)*(len(self.increased)+ 1)))

        if not (self.increased or self.decreased):
            text = self.font.render("No New Mutations", True, (100, 100, 100))
            self.mut_box_surface.blit(text, (10, 25))

        self.screen.blit(self.mut_box_surface, ((SCREEN_WIDTH + WORLD_WINDOW_WIDTH)//2 + 20, (SCREEN_HEIGHT//2) + 20))

    def draw_species_box(self):
        self.species_box_surface.fill(BLACK)
        # WORLD BOX
        pygame.draw.rect(self.species_box_surface, (255, 255, 255), (0, 0, SPECIES_BOX_W, SPECIES_BOX_H), 1)

        self.screen.blit(self.species_box_surface, ((SCREEN_WIDTH - WORLD_WINDOW_WIDTH)//2 - 220 , (SCREEN_HEIGHT - WORLD_WINDOW_HEIGHT)//2))

    def draw_game_world(self):
        self.world_surface.fill(BLACK)

        # draw grid
        self.world.render_chunks(self.world_surface, self.camera)

        # draw cells
        for cell in self.cells:
            cell.draw(self.world_surface, self.camera.zoom, self.camera.offset)

        # WORLD BOX
        pygame.draw.rect(self.world_surface, (255, 255, 255), (0, 0, WORLD_WINDOW_WIDTH, WORLD_WINDOW_HEIGHT), 1)

        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.0f}", True, (255, 255, 255))
        self.world_surface.blit(fps_text, (10, 10))

        self.screen.blit(self.world_surface,
                         ((SCREEN_WIDTH - WORLD_WINDOW_WIDTH) / 2, (SCREEN_HEIGHT - WORLD_WINDOW_HEIGHT) / 2))

    def create_box_label(self, text, top_left):
        label = self.font.render(text, True, (0, 255, 0))
        label_rect = label.get_rect(topleft = top_left)
        pygame.draw.rect(
            self.screen,
            BLACK,
            label_rect.inflate(6,4)
        )
        self.screen.blit(label, label_rect)

    def render(self):
        self.screen.fill(BLACK)
        self.draw_game_world()

        self.draw_stat_box()
        self.draw_mut_box()
        #self.draw_species_box()


        # TEXT FOR WORLD BOX
        self.create_box_label("Game World", (SCREEN_WIDTH/2 - 16, 55))

        # TEXT FOR STAT BOX
        self.create_box_label("Player Stats", ((SCREEN_WIDTH + WORLD_WINDOW_WIDTH + STAT_BOX_W)//2 - 15, 55))

        self.create_box_label("Mutations", ((SCREEN_WIDTH + WORLD_WINDOW_WIDTH + STAT_BOX_W)//2 - 10, 375))

        pygame.display.flip()

        self.clock.tick(60)

    def kill_cell(self, cell):
        #spawn particles for mass
        if cell.is_player:
            self.camera.type = 1
            cell.is_player = False

        if not cell.has_split:
            cell.cell_death(self.world)
        self.cells.remove(cell)
        self.space.remove(cell.body, cell.shape)

    def update(self):
        # physics
        self.space.step(1 / 60)
        if self.camera.type == 1:
            self.camera.update(width = WORLD_WINDOW_WIDTH, height = WORLD_WINDOW_HEIGHT)
        # cell interactions
        for chunk in self.world.loaded_lvl1chunks:
            if self.world.lvl1chunks[chunk].has_particles:
                for grid_cell in self.world.lvl1chunks[chunk].materials:
                    if isinstance(self.world.lvl1chunks[chunk].materials[grid_cell], WaterCell):
                        cell = self.world.lvl1chunks[chunk].materials[grid_cell]
                        if len(cell.particles) >= cell.particle_count:
                            pass
                        else:
                            if random.random() < 0.05 * (1/60): # dt
                                cell.spawn_particle()


        for cell in self.cells:
            self.world.update_entity(cell)

            # player cell functions
            if cell.is_player:
                # update self.player
                self.player.cell = cell
                # load chunks
                self.world.process(cell.body.position, self.space)
                # camera
                self.camera.update(cell.body, WORLD_WINDOW_WIDTH, WORLD_WINDOW_HEIGHT)

            # cell reproduction
            if cell.mass >= cell.max_mass and cell.energy >= cell.max_energy:
                cell.split(self.space, self.cells)

            # gain energy:
            for particle in cell.nearby_particles:
                cell.consume_particle(
                    particle, self.to_remove_particles
                )

            if cell.has_chloroplast:
                # increase energy by 1000 per second
                chunk_pos = world_to_lvl2_chunk(cell.body.position)
                if 0 <= chunk_pos[0] < WORLD_SIZE and 0 <= chunk_pos[1] < WORLD_SIZE:
                    chunk = self.world.lvl2chunks[chunk_pos]
                    if cell.color == LIME:
                        if chunk.light_level == 5:
                            cell.energy += 100
                        elif chunk.light_level == 4:
                            cell.energy += 50
                        elif chunk.light_level == 3:
                            cell.energy += 20
                        elif chunk.light_level == 2:
                            cell.energy += 10
                        else:
                            cell.energy += 0

                    elif cell.color == ORANGE:
                        if chunk.light_level == 5:
                            cell.energy += 50
                        elif chunk.light_level == 4:
                            cell.energy += 20
                        elif chunk.light_level == 3:
                            cell.energy += 50
                        elif chunk.light_level == 2:
                            cell.energy += 20
                        else:
                            cell.energy += 0

                    elif cell.color == RED:
                        if chunk.light_level == 5:
                            cell.energy += 20
                        elif chunk.light_level == 4:
                            cell.energy += 10
                        elif chunk.light_level == 3:
                            cell.energy += 20
                        elif chunk.light_level == 2:
                            cell.energy += 50
                        else:
                            cell.energy += 0

                    else:
                        pass

            # kill conditions
            # remove all dead cells
            if cell.is_dead:
                self.kill_cell(cell)

            # death by starvation
            if cell.energy <= 0:
                cell.is_dead = True

            # death by contact
            for other in cell.contact_time:
                cell.contact_time[other] += 1/60
                if cell.contact_time[other] >= 1:
                    other.is_dead = True

            # death by consumption
            for entity in cell.nearby_entities:
                cell.consume_cell(entity)


        # cleanup
        for particle in self.to_remove_particles:
            gx, gy = particle.x // CELL_SIZE, particle.y // CELL_SIZE
            cell = self.world.get_lvl1_chunk_local_cell((gx, gy))

            if cell and particle in cell.particles:
                cell.particles.remove(particle)

        self.to_remove_particles.clear()

    def main_game_loop(self):
        while self.running:
            self.handle_inputs()
            self.update()
            self.render()

            if len(self.cells) != self.previous_cell_length:
                print("Amount of cells:",len(self.cells))
                self.previous_cell_length = len(self.cells)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.main_game_loop()
