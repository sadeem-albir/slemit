import pygame as pg
import math as mt
import random as rnd
import numpy as np

pg.display.init()
WIDTH, HEIGHT = pg.display.get_desktop_sizes()[0]
WORLD_WIDTH, WORLD_HEIGHT = WIDTH * 4, WIDTH * 4
CENTER = WIDTH/2, HEIGHT/2

class Snake:
    def __init__(self, color, unit_count, unit_radius, start_pos,
                 unit_spacing=0, angle=(0*mt.pi/180), vel=0, ang_vel=0, head_color="orange"):
        self.original_color = pg.Color(color)
        self.color = pg.Color(color)
        self.head_color = pg.Color(head_color)
        self.brightness = 0
        self.unit_count = unit_count
        self.unit_radius = unit_radius
        self.unit_spacing = unit_spacing
        self.angle = angle
        self.vel = vel
        self.max_vel = 7
        self.vel_rate = 3/4
        self.ang_vel = ang_vel
        self.pos_checkpoint = start_pos
        self.length = self.unit_count * (2 * self.unit_radius + self.unit_spacing) - self.unit_spacing
        self.radius = self.length / (2*mt.pi)
        self.score = 0
        self.state = True
        self.beam_color = pg.Color(225, 225, 225)
        self.beam_distance = WIDTH * (1/8)
        self.beam_angle = 25 * mt.pi/180
        self.normal_beam_light = self.beam_distance
        self.high_beam_light = WIDTH / 2
        self.light_on = False
        self.is_visible = False
        self.radar_color = pg.Color("green")
        self.radar_radius = 3

        self.units = [pg.Rect((start_pos[0] - self.unit_radius, start_pos[1] - self.unit_radius),
                              (2*self.unit_radius, 2*self.unit_radius))]
        for i in range(1, unit_count):
            angle_portion = self.angle + i * ((2*mt.pi) / (unit_count - 25))
            pos = (start_pos[0] - i * (self.unit_spacing + 2*self.unit_radius) * mt.cos(self.angle),
                   start_pos[1] + i * (self.unit_spacing + 2*self.unit_radius) * mt.sin(self.angle))
            self.units.append(pg.Rect((pos[0] - self.unit_radius, pos[1] - self.unit_radius),
                                      (2*self.unit_radius, 2*self.unit_radius)))
        self.rect = self.units[0]
        self.center = pg.Vector2(self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2)

    def draw(self, camera):
        if self.is_visible:
            self.draw_shaded_beam(camera.surf)
            for unit in reversed(self.units[1:]):
                pg.draw.circle(camera.surf, self.color, (unit.x - camera.rect.x, unit.y - camera.rect.y), self.unit_radius)
            pg.draw.circle(camera.surf, self.head_color, (self.units[0].x, self.units[0].y), self.unit_radius)
        else:
            self.beam_distance = 0

    def move(self):
        if abs(self.ang_vel) > 0:
            self.ang_vel *= 0.75 * mt.pi/180
        if self.vel > 0:
            self.vel -= 0.25

        self.update_move()

        self.angle += self.ang_vel
        self.angle %= 2*mt.pi

        # self.units[0].x += self.vel * mt.cos(self.angle)
        # self.units[0].y -= self.vel * mt.sin(self.angle)
        for i in range(1, len(self.units)):
            dx = self.units[i-1].x + self.vel * mt.cos(self.angle) - self.units[i].x
            dy = self.units[i-1].y - self.vel * mt.sin(self.angle) - self.units[i].y
            d = mt.sqrt(dx**2 + dy**2)
            if d > 0:
                self.units[i].x = self.units[i-1].x - (dx / d) * (self.unit_spacing + 2 * self.unit_radius)
                self.units[i].y = self.units[i-1].y - (dy / d) * (self.unit_spacing + 2 * self.unit_radius)

    def update_move(self):
        if pg.key.get_pressed()[pg.K_w] and self.vel < self.max_vel:
            self.vel += self.vel_rate
        if pg.key.get_pressed()[pg.K_a]:
            self.ang_vel += 5 * mt.pi/180
        if pg.key.get_pressed()[pg.K_d]:
            self.ang_vel -= 5 * mt.pi/180

        if pg.key.get_pressed()[pg.K_LSHIFT] or pg.key.get_pressed()[pg.K_RSHIFT]:
            self.max_vel += 1.25
            self.vel_rate = 3 * 3/4
            self.color = pg.Color(rnd.choice(["red", "green", "blue"]))
        else:
            if self.max_vel > 7:
                self.max_vel -= 1
            self.vel_rate = 3/4
            self.color = self.original_color

    def collide(self, rect):
        for i in range(len(self.units)):
            if self.units[i].colliderect(rect):
                return True, i
        return False, None

    def increase_score(self, n):
        self.score += n

    def decrease_score(self, n):
        if self.score >= 0:
            self.score -= n

    def append_unit(self):
        self.units.append(pg.Rect((self.units[-1].x, self.units[-1].y), (2 * self.unit_radius, 2 * self.unit_radius)))

    def get_light_cone(self):
        return {
            "position": pg.Vector2(self.units[0].x, self.units[0].y),
            "direction": self.angle,
            "angle": self.beam_angle,
            "distance": self.beam_distance,
        }
    
    def draw_beam(self, root):
        beam_surface = pg.Surface((2 * self.beam_distance, 2 * self.beam_distance), pg.SRCALPHA)
        beam_surface.set_colorkey((0, 0, 0))
        beam_angle = self.beam_angle


        x_l = self.beam_distance + self.beam_distance * mt.cos(self.angle + beam_angle)
        x_r = self.beam_distance + self.beam_distance * mt.cos(self.angle - beam_angle)
        y_l = self.beam_distance - self.beam_distance * mt.sin(self.angle + beam_angle)
        y_r = self.beam_distance - self.beam_distance * mt.sin(self.angle - beam_angle)

        #pg.draw.polygon(beam_surface, self.beam_color, [(self.beam_distance, self.beam_distance), (x_l, y_l), (x_r, y_r)])
        pg.draw.arc(beam_surface, self.beam_color, beam_surface.get_rect(), self.angle - beam_angle, self.angle + beam_angle)

        points = [(self.beam_distance, self.beam_distance), (x_r, y_r)]
        start_angle = self.angle - beam_angle
        end_angle = self.angle + beam_angle
        gradient_steps = 30
        for i in range(gradient_steps + 1):
            seg_angle = start_angle + (end_angle - start_angle) * (i / gradient_steps)
            seg_x = self.beam_distance + self.beam_distance * mt.cos(seg_angle)
            seg_y = self.beam_distance - self.beam_distance * mt.sin(seg_angle)
            points.append((seg_x, seg_y))
        pg.draw.polygon(beam_surface, [int(self.beam_color[i] * 2.2) for i in range(len(self.beam_color))], points)

        root.blit(beam_surface, (self.units[0].x - self.beam_distance, self.units[0].y - self.beam_distance),
                  special_flags=pg.BLEND_RGB_ADD)

    def draw_shaded_beam(self, root):
        beam_surface = pg.Surface((2 * self.beam_distance, 2 * self.beam_distance), pg.SRCALPHA)
        position = self.beam_distance, self.beam_distance
        gradient_steps = 90
        for i in range(gradient_steps):
            reverse_i = gradient_steps - 1 - i
            alpha = max(0, 255 - (reverse_i * (255 // gradient_steps)))
            self.beam_color.a = alpha

            scale = 1 - (i / gradient_steps)
            beam_width = self.beam_angle * 2 * scale
            beam_length = self.beam_distance * scale
            
            points = []
            p1 = position
            p2 = (position[0] + beam_length * mt.cos(self.angle - beam_width / 2),
                  position[1] - beam_length * mt.sin(self.angle - beam_width / 2))
            points.append(p1)
            points.append(p2)
            for j in range(1, 6):
                x = position[0] + beam_length * mt.cos(self.angle - beam_width / 2 + (j / 5) * beam_width)
                y = position[1] - beam_length * mt.sin(self.angle - beam_width / 2 + (j / 5) * beam_width)
                points.append((x, y))
            p3 = (position[0] + beam_length * mt.cos(self.angle + beam_width / 2),
                  position[1] - beam_length * mt.sin(self.angle + beam_width / 2))
            points.append(p3)

            pg.draw.polygon(beam_surface, self.beam_color, points)

        root.blit(beam_surface, (self.units[0].x - self.beam_distance, self.units[0].y - self.beam_distance))

class Enemy(Snake):
    def __init__(self, color, unit_count, unit_radius, start_pos,
                 unit_spacing=0, angle=(0*mt.pi/180), vel=0, ang_vel=0, head_color="orange"):

        super().__init__(self, "red", unit_count, unit_radius, start_pos,
                 unit_spacing=0, angle=rnd.choice([i * (1/4) * mt.pi for i in range(8)]),
                         vel=0, ang_vel=0, head_color="orange")

        def move(self):
            pass

class Grid:
    def __init__(self, color, spacing=pg.Vector2(WIDTH/6, HEIGHT/6)):
        self.color = color
        self.spacing = spacing
        self.vert_line_x = np.linspace(-WIDTH, 2 * WIDTH, 60)
        self.vert_line_y = (-HEIGHT, 2 * HEIGHT)
        self.vert_points = np.array([([x, self.vert_line_y[0]], [x, self.vert_line_y[1]])
                                     for x in self.vert_line_x])
        self.horiz_line_x = (-WIDTH, 2 * WIDTH)
        self.horiz_line_y = np.linspace(-HEIGHT, 2 * HEIGHT, 60)
        self.horiz_points = np.array([([self.horiz_line_x[0], y], [self.horiz_line_x[1], y])
                                     for y in self.horiz_line_y])

    def draw(self, camera):
        #pg.draw.lines(camera.surf, self.color, False, self.vert_points - np.array([camera.offset.x, camera.offset.y]))
        #pg.draw.lines(camera.surf, self.color, False, self.horiz_points - np.array([camera.offset.x, camera.offset.y]))

        offset = np.array([camera.offset.x, camera.offset.y])
        for i in range(len(self.vert_points)):
            pg.draw.line(camera.surf, self.color,
                         (self.vert_points[i][0][0] - offset[0], self.vert_points[i][0][1]),
                         (self.vert_points[i][1][0] - offset[0], self.vert_points[i][1][1]))

        for i in range(len(self.horiz_points)):
            pg.draw.line(camera.surf, self.color,
                         (self.horiz_points[i][0][0], self.horiz_points[i][0][1] - offset[1]),
                         (self.horiz_points[i][1][0], self.horiz_points[i][1][1] - offset[1]))

    def update(self, camera):
        for i in range(len(self.vert_points)):
            if self.vert_points[i][0][0] - camera.offset.x < -WIDTH:
                self.vert_points[i][0][0], self.vert_points[i][1][0] = 2*WIDTH + camera.offset.x, 2*WIDTH + camera.offset.x
            if self.vert_points[i][0][0] - camera.offset.x > 2*WIDTH:
                self.vert_points[i][0][0], self.vert_points[i][1][0] = -WIDTH + camera.offset.x, -WIDTH + camera.offset.x
            if self.horiz_points[i][0][1] - camera.offset.y < -HEIGHT:
                self.horiz_points[i][0][1], self.horiz_points[i][1][1] = (2*HEIGHT + camera.offset.y,
                                                                          2*HEIGHT + camera.offset.y)
            if self.horiz_points[i][0][1] - camera.offset.y > 2*HEIGHT:
                self.horiz_points[i][0][1], self.horiz_points[i][1][1] = (-HEIGHT + camera.offset.y,
                                                                          -HEIGHT + camera.offset.y)



class Coin:
    def __init__(self, center, radius, immune_to_darkness, color=pg.Color("yellow")):
        self.radius = radius
        self.blueprint_color = pg.Color(color)
        self.color = pg.Color(color)
        self.state = 1 if self.color != "red" else -1
        self.rect = pg.Rect((center[0] - radius, center[1] - radius), (radius*2, radius*2))
        self.immune_to_darkness = immune_to_darkness
        self.radar_color = pg.Color("white")
        self.radar_radius = 2

    def draw(self, camera):
        pg.draw.circle(camera.surf, self.color, (self.rect.x - camera.offset.x,
                                                 self.rect.y - camera.offset.y), self.radius)

    def is_visible(self, light_cone, camera):
        dx = self.rect.x - camera.offset.x - light_cone["position"].x
        dy = self.rect.y - camera.offset.y - light_cone["position"].y
        distance = mt.hypot(dx, dy)

        r = light_cone["distance"]
        if distance > r:
            return False, 0

        phi = mt.atan2(-dy, dx)
        theta = light_cone["direction"]
        alpha = light_cone["angle"]
        delta_phi = mt.atan2(mt.sin(phi - theta), mt.cos(phi - theta))

        if abs(delta_phi) <= alpha:
            brightness = max(0, 1 - 0.5 * (delta_phi / alpha) ** 2 - 0.6 * (distance / r) ** 2)
            return True, brightness

        return False, 0

    def adjust_brightness(self, brightness):
        for i in range(len(self.color) - 1):
            self.color[i] = int(self.blueprint_color[i] * brightness)

    def respawn(self, new_position):
        self.rect.center = new_position

class Radar:
    # objects is a map of <object, color> pairs of the objects (as a small circle) to be shown on the radar
    def __init__(self, pos, original_size, scale, objects,
                 outline_color=pg.Color("blue"), fill_color=pg.Color(255, 255, 255, 128)):
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.original_size = original_size
        self.rect = pg.Rect(pos, original_size * scale)
        self.objects = objects

    def draw(self, root, camera):
        alpha_surface = pg.Surface((self.rect.w, self.rect.h), pg.SRCALPHA)
        pg.draw.rect(alpha_surface, self.fill_color, (0, 0, self.rect.w, self.rect.h))
        root.blit(alpha_surface, (self.rect.x, self.rect.y))
        pg.draw.rect(root, self.outline_color, self.rect, width=3)

        player_obj = self.objects["player"][0]
        player_scaled_x = self.rect.x + ((player_obj.rect.x) * self.rect.w / self.original_size[0])
        player_scaled_y = self.rect.y + ((player_obj.rect.y) * self.rect.h / self.original_size[1] )
        pg.draw.circle(root, player_obj.radar_color, (player_scaled_x, player_scaled_y), player_obj.radar_radius)
        for obj_t in self.objects.keys():
            if obj_t == "player":
                continue
            for i in range(len(self.objects[obj_t])):
                obj = self.objects[obj_t][i]
                scaled_x = self.rect.x + ((obj.rect.x - camera.offset.x) * self.rect.w / self.original_size[0])
                scaled_y = self.rect.y + ((obj.rect.y - camera.offset.y) * self.rect.h / self.original_size[1] )
                if (self.rect.x < scaled_x < self.rect.x + self.rect.w and
                    self.rect.y < scaled_y < self.rect.y + self.rect.h):
                    pg.draw.circle(root, obj.radar_color, (scaled_x, scaled_y), obj.radar_radius)

class Camera:
    def __init__(self, rect_color, inner_rect_color, rect, inner_rect, objects):
        self.rect_color = rect_color
        self.inner_rect_color = inner_rect_color
        self.rect = rect
        self.inner_rect = inner_rect
        self.surf = pg.Surface((self.rect.w, self.rect.h))
        self.objects = objects
        self.offset = pg.Vector2(0, 0)
        self.angle = None

    # "player" here is just snake
    def update(self, player):
        self.angle = player.angle

        self.offset[0] += (player.vel * mt.cos(player.angle)) / 3
        self.offset[1] -= (player.vel * mt.sin(player.angle)) / 3

        distance = mt.hypot(self.offset[0] - player.rect.x, self.offset[1] - player.rect.y)

        #self.offset[0] = player.rect.x + distance * mt.cos(player.angle)
        #self.offset[1] = player.rect.y - distance * mt.sin(player.angle)

