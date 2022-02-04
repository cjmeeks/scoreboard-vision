import sys

import pygame

from pygame.locals import *


pygame.init()
pygame.display.set_caption('game base')
screen = pygame.display.set_mode((400, 400), 0, 32)
clock = pygame.time.Clock()

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i)
             for i in range(pygame.joystick.get_count())]
for joystick in joysticks:
    print(joystick.get_name())

gas = 0
brake = 0
gas_pedal = pygame.Rect(50, 200, 50, 50)
brake_pedal = pygame.Rect(100, 50, 50, 50)
brake_pedal.height = 0
my_square_color = 0

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
motion = [0, 0, 0, 0, 0, 0]

while True:

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, colors[my_square_color], gas_pedal)
    pygame.draw.rect(screen, colors[my_square_color], brake_pedal)
    # print(motion)
    # gas_pedal.h += motion[5] * 10

    for event in pygame.event.get():
        if event.type == JOYAXISMOTION:
            print(event)
            if event.axis == 5:
                gas_pedal.height = ((event.value + 1) / 2) * 100
                gas_pedal.y = 100 - ((event.value + 1) / 2) * 100
            if event.axis == 4:
                brake_pedal.height = ((event.value + 1) / 2) * 100
            motion[event.axis] = event.value
        if event.type == JOYHATMOTION:
            print(event)
        if event.type == JOYDEVICEADDED:
            joysticks = [pygame.joystick.Joystick(
                i) for i in range(pygame.joystick.get_count())]
            for joystick in joysticks:
                print(joystick.get_name())
        if event.type == JOYDEVICEREMOVED:
            joysticks = [pygame.joystick.Joystick(
                i) for i in range(pygame.joystick.get_count())]
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYUP:
            if event.key == K_UP:
                gas_pedal.height = 0
        if event.type == KEYDOWN:
            if event.key == K_UP:
                gas_pedal.height = 100
            print(event)

    pygame.display.update()
    clock.tick(60)
