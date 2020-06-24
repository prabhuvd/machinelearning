"""
The classic game of flappy bird. Make with python
and pygame.  The base file were borrowed from Tech With Time

Author : Prabhu Desai

"""
import pygame
import random
from random import randint
import os
import time
# import neat
# import visualize
import pickle
pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 30)
STARTING_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 30)
DRAW_LINES = False

GAME_WINDOW = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (WIN_WIDTH, WIN_HEIGHT))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0
GAME_WINDOW =0
GAME_OVER= False
GAME_MAIN_LOOP = True
DELAYED_START = True
CLOCK = 0

class Bird:
    """
    Bird class representing the flappy bird
    """
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 2

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        #self.vel = -10.5
        self.vel = -9.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, GAME_WINDOW):
        """
        draw the bird
        :param GAME_WINDOW: pygame window or surface
        :return: None
        """
        self.img_count += 1
        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        #print ("Bird : " , self.x, self.y,self.tilt)
        # tilt the bird
        blitRotateCenter(GAME_WINDOW, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    represents a pipe object
    """
    GAP = 350
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL


    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param GAME_WINDOW: pygame window/surface
        :return: None
        """
        #print ("pipes : " , self.x, self.top,self.bottom)
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, int(self.top - round(bird.y)))
        bottom_offset = (self.x - bird.x, int(self.bottom - round(bird.y)))


        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True
        else :
            return False

class Base:
    """
    Represnts the moving floor of the game
    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img
    corner_offset = 30

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        self.BASE_TOP = base_img


    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param GAME_WINDOW: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))

    def collide(self, bird):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        #check if there is a collision at the top or bottom of the window
        if (bird.y + (bird.img.get_height()+ self.corner_offset) >= FLOOR) or (bird.y <(bird.img.get_height()- self.corner_offset)):
            return True
        else :
            return False


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base):
    """
    draws the windows for the main game loop
    :param GAME_WINDOW: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """

    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(GAME_WINDOW)

    base.draw(GAME_WINDOW)
    birds.draw(GAME_WINDOW)

    # for bird in birds:
    #     # draw lines from bird to pipe
    #     if DRAW_LINES:
    #         try:
    #             pygame.draw.line(GAME_WINDOW, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
    #             pygame.draw.line(GAME_WINDOW, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
    #         except:
    #             pass
    #     # draw bird
    #     bird.draw(GAME_WINDOW)
    #
    # score
    #score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    #GAME_WINDOW.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))
    #
    # generations
    # score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    # GAME_WINDOW.blit(score_label, (10, 10))
    #
    # # alive
    # score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    # GAME_WINDOW.blit(score_label, (10, 50))

    pygame.display.update()

class Score:
    def __init__(self):
        self.score =0
    def incr_score(self):
        self.score = self.score +1
    def get_score(self):
        return self.score
    def update_screen(self,win):
        game_score = STAT_FONT.render("Score " + str(self.score) , True, (0,0,0))
        win.blit(game_score, (10,10))
        pygame.display.update()

def checkGameOver(score):
    global GAME_OVER
    global GAME_MAIN_LOOP
    global DELAYED_START

    #Handle the Restart / Quitting of the program
    while GAME_OVER:
        GAME_OVER_text = END_FONT.render("Game Over !! ",True, (0,0,0))
        GAME_WINDOW.blit(GAME_OVER_text, (100,WIN_HEIGHT/2))
        GAME_OVER_text = END_FONT.render("Press Restart(R)/Quit (Q) ",True, (0,0,0))
        GAME_WINDOW.blit(GAME_OVER_text, (100,20+WIN_HEIGHT/2))
        #game_produce = STAT_FONT.render("Prabhu Desai", True, (255,255,255))
        #GAME_WINDOW.blit(game_produce, (100,50+WIN_HEIGHT/2))
        score.update_screen(GAME_WINDOW)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_MAIN_LOOP = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    GAME_MAIN_LOOP = False
                    GAME_OVER = False
                elif event.key == pygame.K_r:
                    GAME_MAIN_LOOP = True
                    GAME_OVER = False
                    DELAYED_START = True
                    main()

def handle_space_bar(bird_obj):
    global GAME_MAIN_LOOP
    # Respond to space-bar for the bird jump
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            GAME_MAIN_LOOP = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_obj.jump()


def startDelaynScore(score):
    global DELAYED_START
    global GAME_WINDOW
    countdown=5*30

    #Handle the delay in starting the game...
    while DELAYED_START:
        CLOCK.tick(30)
        GAME_WINDOW.blit(bg_img, (0,0))
        starting_txt = STARTING_FONT.render("STARTING ..."  +str(countdown/30), True, (0,0,255))
        GAME_WINDOW.blit(starting_txt, (200,WIN_HEIGHT/4))

        score.update_screen(GAME_WINDOW)

        pygame.display.update()
        if(countdown>0):
            countdown= countdown-1
        else:
            DELAYED_START=False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_MAIN_LOOP = False
def main():
    global GAME_MAIN_LOOP
    global GAME_WINDOW
    global GAME_OVER
    global CLOCK

    flappy_score = Score()


    bird = Bird(230,350)
    base= Base(700)
    pipes = [Pipe(600)]

    GAME_WINDOW = pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    CLOCK = pygame.time.Clock()
    score=0
    while GAME_MAIN_LOOP:
        startDelaynScore(flappy_score)
        checkGameOver(flappy_score)
        flappy_score.update_screen(GAME_WINDOW)

        CLOCK.tick(30)
        # Keep the base GAME_MAIN_LOOPning
        base.move()
        bird.move()
        handle_space_bar(bird)

        #check if the bird has a collision with the base
        if(base.collide(bird)):
            GAME_OVER = True

        #Index through pipes that are not required anymore and add new pipes..
        for pipe in pipes:
            if(pipe.x <=0 ):
                pipes.pop()
                pipes.append(Pipe(WIN_WIDTH))
                flappy_score.incr_score()

            if(pipe.collide(bird)):
                GAME_OVER = True

            pipe.move()

        draw_window(GAME_WINDOW,bird,pipes,base)



    pygame.quit()
    quit()


main()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,
                            neat.DefaultSpeciesSet,neat.DefaultStagnation,config_path)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(,50)

if __name__  == "__main__":
    local_dir= os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config-feedforward.txt")
    run(config_path)
