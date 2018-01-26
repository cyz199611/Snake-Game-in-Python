# snake game

import pygame, sys, random


# game screen
screen_info = dict(step = 18, screen_width = 18*46 , screen_height = 18 * 36)

# colors
red = pygame.Color(255, 0, 0)  # game over
green = pygame.Color(0, 255, 0)  # snake body
black = pygame.Color(0, 0, 0)  # player score
white = pygame.Color(255, 255, 255)  # game background
brown = pygame.Color(165, 42, 42)  # food


class StateManager(object):
    def __init__(self):
        # states initialization
        self.game_menu = GameMenu(self)
        self.game_play = GamePlay(self)
        self.game_pause = GamePause(self)
        self.game_over = GameOver(self)

        self.go_to(self.game_menu) # start state

    def go_to(self, state): # go to next state
        self.state = state


class State(object):
    def __init__(self, game_manager):
        self.StateManager = game_manager
        self.screen_width = screen_info['screen_width']
        self.screen_height = screen_info['screen_height']
        self.step = screen_info['step']

    def render(self, game_screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError


class GameMenu(State):
    def __init__(self, game_manager):
        super(GameMenu, self).__init__(game_manager)
        self.font = pygame.font.SysFont('Lucida Grande', 50)

    def render(self, game_screen):
        game_screen.fill(white)

        start_surface = self.font.render('Press Enter to start', True, black)
        start_rect = start_surface.get_rect()
        start_rect.midtop = (self.screen_width / 2, self.screen_height / 10)
        game_screen.blit(start_surface, start_rect)

        esc_surface = self.font.render('''Press Esc to exit during game''', True, black)
        esc_rect = esc_surface.get_rect()
        esc_rect.midtop = (self.screen_width / 2, self.screen_height / 10 + 100)
        game_screen.blit(esc_surface, esc_rect)

        pause_surface = self.font.render('''Press Space to pause the game''', True, black)
        pause_rect = pause_surface.get_rect()
        pause_rect.midtop = (self.screen_width / 2, self.screen_height / 10 + 200)
        game_screen.blit(pause_surface, pause_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.StateManager.go_to(self.StateManager.game_play)


class GamePlay(State):
    def __init__(self, game_manager):
        super(GamePlay, self).__init__(game_manager)

        # game variables
        self.start_x = self.screen_width // 2
        self.start_y = self.screen_height // 2
        self.initial_body_length = 5

        self.snake_head = [self.start_x, self.start_y]  # snake start position [x, y]
        # initialize snake body, index 0 contains the snake head
        self.snake_body = [ [self.start_x - i * self.step, self.start_y]
                           for i in range(self.initial_body_length) ]

        self.direction = 'RIGHT'
        self.next_direction = self.direction  # new direction after user hits keyboard

        self.score = 0
        self.level = 0

        # don't put food at the border of the screen
        self.food_pos = [random.randrange(3, self.screen_width / self.step - 2) * self.step,
                         random.randrange(3, self.screen_height / self.step - 2) * self.step]
        while self.food_snake_collision():
            self.food_pos = [random.randrange(3, self.screen_width / self.step - 2) * self.step,
                             random.randrange(3, self.screen_height / self.step - 2) * self.step]

        self.food_spawn = True

        self.user_input = None

        # variables calculate delta_time between two frames and use this to control speed
        self.last_time = 0
        self.current_time = 0

    def show_score(self, game_screen):
        my_font = pygame.font.SysFont('monaco', 50)
        score_surface = my_font.render('Score: {0}'.format(self.score), True, red)
        score_rect = score_surface.get_rect()

        score_rect.topleft = (self.screen_width / 40, 10)

        game_screen.blit(score_surface, score_rect)

    def food_snake_collision(self):
        for block in self.snake_body:
            if block[0] == self.food_pos[0] and block[1] == self.food_pos[1]:
                return True
        return False

    def render(self, game_screen):
        game_screen.fill(white)

        # draw snake body
        for pos in self.snake_body:
            pygame.draw.rect(game_screen, green,
                             pygame.Rect(pos[0], pos[1], self.step, self.step))
        # draw food
        pygame.draw.rect(game_screen, brown,
                            pygame.Rect(self.food_pos[0], self.food_pos[1],
                            self.step, self.step))
        # show score
        self.show_score(game_screen)

    def update(self):
        self.current_time = pygame.time.get_ticks()

        # move the snake only after a specific time interval depending on game level
        if self.current_time - self.last_time >= 180 - 15*self.level:
            if self.user_input == pygame.K_RIGHT:
                self.next_direction = 'RIGHT'
            elif self.user_input == pygame.K_LEFT:
                self.next_direction = 'LEFT'
            elif self.user_input == pygame.K_UP:
                self.next_direction = 'UP'
            elif self.user_input == pygame.K_DOWN:
                self.next_direction = 'DOWN'

            # validation of direction
            if self.next_direction == 'RIGHT' and self.direction != 'LEFT':
                self.direction = 'RIGHT'
            elif self.next_direction == 'LEFT' and self.direction != 'RIGHT':
                self.direction = 'LEFT'
            elif self.next_direction == 'DOWN' and self.direction != 'UP':
                self.direction = 'DOWN'
            elif self.next_direction == 'UP' and self.direction != 'DOWN':
                self.direction = 'UP'

            # move snake head
            if self.direction == 'RIGHT':
                self.snake_head[0] += self.step
            elif self.direction == 'LEFT':
                self.snake_head[0] -= self.step
            elif self.direction == 'DOWN':
                self.snake_head[1] += self.step
            elif self.direction == 'UP':
                self.snake_head[1] -= self.step

            # check if snake hits the border
            if self.snake_head[0] == self.screen_width:
                self.snake_head[0] = 0
            if self.snake_head[0] < 0:
                self.snake_head[0] = self.screen_width - self.step
            if self.snake_head[1] == self.screen_height:
                self.snake_head[1] = 0
            if self.snake_head[1] < 0:
                self.snake_head[1] = self.screen_height - self.step

            self.snake_body.insert(0, list(self.snake_head))

            if self.snake_head[0] == self.food_pos[0] and self.snake_head[1] == self.food_pos[1]:
                self.food_spawn = False
                self.score += 1
            else:
                self.snake_body.pop()

            while not self.food_spawn:
                self.food_pos = \
                    [random.randrange(2, self.screen_width / self.step - 2) * self.step,
                     random.randrange(2, self.screen_height / self.step - 2) * self.step]
                if self.food_snake_collision():
                    self.food_spawn = False
                else:
                    self.food_spawn = True

            # check if snake hits itself
            for block in self.snake_body[1:]:
                if self.snake_head[0] == block[0] and self.snake_head[1] == block[1]:
                    self.StateManager.go_to(self.StateManager.game_over)

            self.level = self.score // 6 + 1
            if self.level > 8:
                self.level = 8

            self.last_time = self.current_time # update time

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.StateManager.go_to(self.StateManager.game_pause)
                elif event.key == pygame.K_ESCAPE:
                    self.StateManager.go_to(self.StateManager.game_over)

                if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN]:
                    self.user_input = event.key
                else:
                    self.user_input = None


class GamePause(State):
    def __init__(self, game_manager):
        super(GamePause, self).__init__(game_manager)
        self.font = pygame.font.SysFont('Lucida Grande', 60)

    def render(self, game_screen):
        pause_surface = self.font.render('Press Space to continue', True, black)
        pause_rect = pause_surface.get_rect()
        pause_rect.midtop = (self.screen_width / 2, self.screen_height / 10 + 100)
        game_screen.blit(pause_surface, pause_rect)
        exit_surface = self.font.render('Press Esc to exit', True, black)
        exit_rect = exit_surface.get_rect()
        exit_rect.midtop = (self.screen_width / 2, self.screen_height / 10 + 200)
        game_screen.blit(exit_surface, exit_rect)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.StateManager.go_to(self.StateManager.game_play)
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


class GameOver(State):
    def __init__(self, game_manager):
        super(GameOver, self).__init__(game_manager)
        self.font = pygame.font.SysFont('Lucida Grande', 70)

    def show_score(self, game_screen):
        my_font = pygame.font.SysFont('Lucida Grande', 70)
        score_surface = my_font.render('Score: {0}'.\
                                       format(self.StateManager.game_play.score), True, red)
        score_rect = score_surface.get_rect()
        score_rect.midtop = (self.screen_width / 2, self.screen_height / 10 + 100)
        game_screen.blit(score_surface, score_rect)

    def render(self, game_screen):
        GO_surface_1 = self.font.render('Game Over !', True, red)
        GO_rect_1 = GO_surface_1.get_rect()
        GO_rect_1.midtop = (self.screen_width / 2, self.screen_height / 10)
        game_screen.blit(GO_surface_1, GO_rect_1)

        GO_surface_2 = self.font.render('Press Esc to exit', True, red)
        GO_rect_2 = GO_surface_2.get_rect()
        GO_rect_2.midtop = (self.screen_width / 2, self.screen_height / 10 + 200)
        game_screen.blit(GO_surface_2, GO_rect_2)

        self.show_score(game_screen)

    def update(self):
        pass

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()  # quit the game
                    sys.exit()  # exit the console


def main():
    # FPS controller
    fps_controller = pygame.time.Clock()

    # game initialization
    check_errors = pygame.init()
    if check_errors[1] > 0:
        print('(!) Got {0} errors during initializing pygame \
            exiting...'.format(check_errors[1]))
        sys.exit(-1)
    else:
        print('(+) pygame successfully initialized.')

    game_screen = pygame.display.set_mode((screen_info['screen_width'],
                                           screen_info['screen_height']))
    pygame.display.set_caption('Snake game')

    running = True

    # game state manager
    game_manager = StateManager()

    while running:
        fps_controller.tick(60)

        if pygame.event.get(pygame.QUIT):
            running = False
            return

        game_manager.state.handle_events(pygame.event.get())
        game_manager.state.update()
        game_manager.state.render(game_screen)

        pygame.display.flip()


if __name__ == '__main__':
    main()