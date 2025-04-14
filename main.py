import pygame as pg
import math as mt
import numpy as np
import random as rnd
import util
from util import WIDTH, HEIGHT, CENTER, WORLD_WIDTH, WORLD_HEIGHT

# initialization
pg.init()
ROOT = pg.display.set_mode((0, 0))
pg.display.set_caption("Snake Entity")

clock = pg.time.Clock()
font = pg.font.Font(size=60)

# objects
snake_element_radius = 15
snake_element_num = 10
snake_unit_spacing = 0
snake = util.Snake("white", snake_element_num, snake_element_radius, CENTER,
                   angle=(90 * (mt.pi/180)), unit_spacing=snake_unit_spacing)


num_coins = 1500
coin_radius = 15
coins = [util.Coin((rnd.randint(WIDTH//2 + coin_radius - WORLD_WIDTH//2, WIDTH//2 - coin_radius + WORLD_WIDTH//2),
                    rnd.randint(HEIGHT//2 + coin_radius - WORLD_HEIGHT//2, HEIGHT//2 - coin_radius + WORLD_HEIGHT//2)),
              coin_radius, False) for _ in range(num_coins)]


objects = {
    "player": [snake],
    "objects": list(coins)
}
scale = 1 / 10

radar = util.Radar(pg.Vector2(WIDTH - 5/4 * WIDTH * scale, (2/5) * WIDTH * scale),
                   pg.Vector2(WIDTH, HEIGHT), scale, objects)

camera_box_size = HEIGHT/4
camera = util.Camera( pg.Color("green"), pg.Color("red"), pg.Rect((0, 0), (WIDTH, HEIGHT)),
                     pg.Rect(WIDTH/2 - camera_box_size/2, HEIGHT / 2 - camera_box_size/2, camera_box_size, camera_box_size),
                     objects)

grid = util.Grid(pg.Color("green"))

def main():

    run = True
    while run:
        clock.tick(60)

        draw(ROOT)
        if update() == -1:
            run = False

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_l:
                    snake.light_on = not snake.light_on
                elif event.key == pg.K_k:
                    coins[0].blueprint_color.update(rnd.choice(["red", "green", "blue"]))
                elif event.key == pg.K_PERIOD:
                    coins[0].blueprint_color.update("yellow")

    pg.quit()

def draw(root):

    root.fill("black")
    camera.surf.fill("black")

    pg.draw.rect(camera.surf, "red", pg.Rect(WIDTH/2 -camera.offset.x, HEIGHT/2 -camera.offset.y, WIDTH / 6, HEIGHT / 6))

    grid.draw(camera)

    snake.draw(camera)
    light_cone = snake.get_light_cone()

    for i in range(len(coins)):
        if ( WORLD_WIDTH/2 < coins[i].rect.x < WORLD_WIDTH/2 + WIDTH/2 or
            WIDTH/2 - WORLD_WIDTH/2 < coins[i].rect.x < WIDTH - WORLD_WIDTH/2 or
            WORLD_HEIGHT/2 < coins[i].rect.y < WORLD_HEIGHT/2 + HEIGHT/2 or
            HEIGHT/2 - WORLD_HEIGHT/2 < coins[i].rect.y < HEIGHT - WORLD_HEIGHT/2 ):
            coins[i].blueprint_color = pg.Color("red")
        elif 0 < coins[i].rect.x < WIDTH and 0 < coins[i].rect.y < HEIGHT:
            coins[i].blueprint_color = pg.Color("green")
        else:
            coins[i].blueprint_color = pg.Color("yellow")

        if coins[i].immune_to_darkness:
            coins[i].adjust_brightness(1)
            coins[i].draw(camera)
        else:
            is_visible, brightness = coins[i].is_visible(light_cone, camera)
            if is_visible and coins[i].rect.colliderect(pg.Rect(camera.offset.x, camera.offset.y, WIDTH, HEIGHT)):
                coins[i].adjust_brightness(brightness)
                coins[i].draw(camera)

    line_length = 30
    line_pos1 = WIDTH * 11/12, HEIGHT * 11/12

    line_pos2 = (line_pos1[0] + line_length * mt.cos(snake.angle),
                 line_pos1[1] - line_length * mt.sin(snake.angle))
    line_left = (line_pos2[0] + (line_length / 5) * mt.cos(snake.angle + (180 - 22.5) * mt.pi/180),
                 line_pos2[1] - (line_length / 5) * mt.sin(snake.angle + (180 - 22.5) * mt.pi/180))
    line_right = (line_pos2[0] + (line_length / 5) * mt.cos(snake.angle - (180 - 22.5) * mt.pi/180),
                 line_pos2[1] - (line_length / 5) * mt.sin(snake.angle - (180 - 22.5) * mt.pi/180))


    root.blit(camera.surf, (0, 0))


    snake_score_font = font.render(f"{snake.score}", True, "yellow")
    root.blit(snake_score_font, (WIDTH * 1/12, HEIGHT * 1/12))

    pg.draw.circle(root, "blue", line_pos1, line_length, width=1)
    pg.draw.line(root, "green", line_pos1, line_pos2)
    pg.draw.line(root, "green", line_pos2, line_left)
    pg.draw.line(root, "green", line_pos2, line_right)

    radar.draw(root, camera)

    pg.display.update()

def update():
    camera.update(snake)
    snake.move()

    grid.update(camera)

    snake.rect.clamp_ip(pg.Rect(0, 0, WIDTH, HEIGHT))

    if pg.key.get_pressed()[pg.K_RIGHTBRACKET]:
        snake.beam_distance = snake.high_beam_light
        snake.is_visible = True
    elif snake.light_on:
        snake.beam_distance = snake.normal_beam_light
        snake.is_visible = True
    else:
        snake.is_visible = False

    for i in range(len(coins)):
        if snake.collide(pg.Rect(coins[i].rect.x - camera.offset.x,
                                 coins[i].rect.y - camera.offset.y,
                                 coins[i].rect.w, coins[i].rect.h))[1] == 0:
            if coins[i].state > 0:
                snake.increase_score(1)
                # snake.append_unit()
            else:
                snake.decrease_score(1)
                if snake.score < 0:
                    return -1
            coins[i].respawn( (rnd.randint(coin_radius, WIDTH - coin_radius),
                                  rnd.randint(coin_radius, HEIGHT - coin_radius)) )
            #coins.pop(i)
    if pg.key.get_pressed()[pg.K_t]:
        for i in range(len(coins)):
            coins[i].respawn( (rnd.randint(WIDTH//2 + coin_radius - WORLD_WIDTH//2, WIDTH//2 - coin_radius + WORLD_WIDTH//2),
                    rnd.randint(HEIGHT//2 + coin_radius - WORLD_HEIGHT//2, HEIGHT//2 - coin_radius + WORLD_HEIGHT//2)) )


if __name__ == "__main__":
    main()
