'''
two main classes Gamewindow() and Maingame() which actually
cause the graphics of the game
'''

from . import gameinfo
from . import objects_to_display as ob
import sdl2
import sdl2.ext as sdl
import sdl2.sdlttf as ttf
import random
import sys
import ctypes
from math import floor, sqrt

class Gamewindow(sdl.Renderer):
    '''
    This class contains the window and renderer for the game
    with methods to draw the objects in objects_to_display module
    '''
    YELLOW = sdl2.SDL_Color(255, 255, 0, 0)
    WHITE = sdl2.SDL_Color(255, 255, 255, 0)
    BLACK = sdl2.SDL_Color(0, 0, 0, 0)
    Rscore = sdl2.SDL_Rect(0, 0, 250, 50)

    def __init__(self):
        self.w = sdl.Window("Adnesh's Snake vs Block Game", (gameinfo.WINDOW_WIDTH, gameinfo.WINDOW_HEIGHT))
        sdl.Renderer.__init__(self, self.w)
        self.mode = gameinfo.BLOCK_IN_MOTION
        self.t = ttf.TTF_OpenFont(b"support/font.ttf", 30)

    def __rendercircle(self, xc, yc, r = ob.Snake.RADIUS):
        '''function to draw circle of radius and XY coordinates'''
        for x in range(r): 
            y = floor(sqrt(r ** 2 - x ** 2))
            self.draw_line((xc + x, yc + y, xc + x, yc - y))
            self.draw_line((xc - x, yc + y, xc - x, yc - y))

    def __renderblock(self, number, val, y):
        '''drawing blocks of color according the strength of blocks'''
        if 0 < val < 10:
            self.color = gameinfo.COLOR_GRID["white-green"]
        elif 9 < val < 20:
            self.color = gameinfo.COLOR_GRID["green"]
        elif 19 < val < 30:
            self.color = gameinfo.COLOR_GRID["blue-green"]
        elif 29 < val < 40:
            self.color = gameinfo.COLOR_GRID["blue"]
        else:
            self.color = gameinfo.COLOR_GRID["red"]
        sx = gameinfo.BLOCKSTART[number]
        self.fill((sx, y - gameinfo.BLOCKSIZE, gameinfo.BLOCKSIZE, gameinfo.BLOCKSIZE))
        texttodisplay = "%2d" %val
        sur = ttf.TTF_RenderText_Solid(self.t, texttodisplay.encode(), self.BLACK)
        tex = sdl2.SDL_CreateTextureFromSurface(self.sdlrenderer, sur)
        Rblock = sdl2.SDL_Rect(sx + gameinfo.RECTSTART_X, y - gameinfo.RECTSTART_Y, gameinfo.RECTWIDTH, gameinfo.RECTHEIGHT)
        sdl2.SDL_RenderCopy(self.sdlrenderer, tex, None, Rblock)
        sdl2.SDL_FreeSurface(sur)
        sdl2.SDL_DestroyTexture(tex)

    def __renderblockrows(self, br):
        '''draw all the blocks in rows'''
        for row in br.row:
            for b in range(ob.Row.MAX_PER_ROW):
                if row.a[b] != 0:
                    self.__renderblock(b, row.a[b], row.pos)

    def rendersnake(self, snake):
        '''drawing snake object'''
        if snake.l > 0:
            self.color = gameinfo.COLOR_GRID["red-blue"]
            for i in range(0, len(snake.a)):
                self.__rendercircle(snake.a[i][0], snake.a[i][1])
                if i > ob.Snake.SHOWABLE:
                    break
            sur = ttf.TTF_RenderText_Solid(self.t, snake.l.__str__().encode(), self.WHITE)
            tex = sdl2.SDL_CreateTextureFromSurface(self.sdlrenderer, sur)
            Rsnake = sdl2.SDL_Rect(snake.head[0] - gameinfo.TSPACE_X, snake.head[1] - gameinfo.TSPACE_Y, gameinfo.TWIDTH, gameinfo.THEIGHT)
            sdl2.SDL_RenderCopy(self.sdlrenderer, tex, None, Rsnake)
            sdl2.SDL_FreeSurface(sur)
            sdl2.SDL_DestroyTexture(tex)

    def rendergoodies(self, g_row):
        '''draw the goodies in game'''
        self.color = sdl.Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 0)
        for r in g_row:
            for g in range(r.num):
                self.__rendercircle(r.co[g], r.pos, gameinfo.BONUSRADIUS)
           
    def renderall(self, snake, br, g):
        '''
        a function which calls all other functions 
        to render the objects in the game
        '''
        self.__renderblockrows(br)
        self.rendersnake(snake)
        self.rendergoodies(g)
        if self.mode == gameinfo.BLOCK_IN_MOTION:
            self.mode = br.advance(snake)
            for gd in g:
                gd.pos += snake.s
                if gd.pos > gameinfo.WINDOW_HEIGHT:
                    g.remove(gd)
        else:
            self.mode = snake.advance(br)
        texttodisplay = "score:" 
        texttodisplay += "%8d" %snake.score
        texttodisplay = texttodisplay.encode()
        sur = ttf.TTF_RenderText_Solid(self.t, texttodisplay, self.YELLOW)
        tex = sdl2.SDL_CreateTextureFromSurface(self.sdlrenderer, sur)
        sdl2.SDL_RenderCopy(self.sdlrenderer, tex, self.Rscore, self.Rscore)
        sdl2.SDL_FreeSurface(sur)
        sdl2.SDL_DestroyTexture(tex)
        snake.adjust()

class Maingame:
    '''all the game variables contained in this class'''
    def __init__(self):
        self.r = Gamewindow()
        self.snake = ob.Snake()
        self.rows = ob.BlockRows()
        self.g = []

    def ResetGame(self):
        '''resets the game'''
        self.snake = ob.Snake()
        self.rows = ob.BlockRows()
        self.g = []

    def Start(self, ischeck, repete):
        '''function which calls the starting function of the game'''
        self.r.w.show()
        n = 1 if repete else 0
        rep = self.StartGame(ischeck) and repete
        self.__print_update_score(n)
        while rep:
            n += 1
            self.ResetGame()
            rep = self.StartGame(ischeck) and repete
            self.__print_update_score(n)
        self.r.w.hide()
        ttf.TTF_CloseFont(self.r.t)

    def StartGame(self, ischeck):
        '''starting the actual game'''
        self.r.w.show()
        Running = flag = True
        mouse = False
        i_ = 0
        scoreholder = sdl2.SDL_Rect(0, 0, 200, 200)
        lim = random.randint(gameinfo.BLOCKSIZE, 900)
        move = gameinfo.STABLE
        d = 0
        delay_ = gameinfo.DELAY1
        xco = 0
        x, y = ctypes.pointer(ctypes.c_int()), ctypes.pointer(ctypes.c_int())
        while Running:
            C = sdl2.SDL_GetTicks()
            if self.snake.head == None:
                Running =  False
            i_ += 1
            self.r.clear(gameinfo.COLOR_GRID["black"])
            self.r.renderall(self.snake, self.rows, self.g)
            events = sdl.get_events()
            for e in events:
                if e.type == sdl2.SDL_QUIT:
                    Running = False
                    return False
                    break
                elif e.type == sdl2.SDL_KEYDOWN and self.snake.head != None:
                    mouse = False
                    k = e.key.keysym.sym
                    if k == sdl2.SDLK_SPACE:
                        while Running:
                            events_ext = sdl.get_events()
                            for e in events_ext:
                                if e.type == sdl2.SDL_KEYDOWN:
                                    Running = False
                                    break
                        Running = True
                    elif k == sdl2.SDLK_RIGHT:
                        if flag:
                            t_stamp = sdl2.SDL_GetTicks()
                            mul = 1
                            move = gameinfo.RIGHT
                            flag = False
                    elif k == sdl2.SDLK_LEFT:
                        if flag:
                            t_stamp = sdl2.SDL_GetTicks()
                            mul = 1
                            move = gameinfo.LEFT
                            flag = False
                    elif k == sdl2.SDLK_q:
                        return False
                        break
                elif e.type == sdl2.SDL_KEYUP:
                    if (e.key.keysym.sym == sdl2.SDLK_RIGHT and move == gameinfo.RIGHT) or (e.key.keysym.sym == sdl2.SDLK_LEFT and move == gameinfo.LEFT):
                        flag = True
                        move = gameinfo.STABLE
                elif e.type == sdl2.SDL_MOUSEMOTION:
                    sdl2.SDL_GetMouseState(x, y)
                    if self.snake.RADIUS < x.contents.value < gameinfo.WINDOW_WIDTH - self.snake.RADIUS and self.snake.head:
                        if not mouse:
                            if self.snake.head[0] - gameinfo.BLOCKSIZE < x.contents.value < self.snake.head[0] + gameinfo.BLOCKSIZE:
                                mouse = True
                                self.snake.lasthead = self.snake.head[0]
                                self.snake.head[0] = x.contents.value
                        else:
                            self.snake.lasthead = self.snake.head[0]
                            self.snake.head[0] = x.contents.value
                    else:
                        mouse = False
            if self.rows.row:
                if self.rows.row[0].pos > lim:
                    self.rows.mountrow(self.snake)
                    lim = random.randint(2 * gameinfo.BLOCKSIZE, 900) 
                random.seed(random.random())
                if random.randint(1, 500) == random.randint(1, 500) and self.rows.row[0].pos > gameinfo.BLOCKSIZE + gameinfo.BONUSRADIUS:
                    goody = ob.Goody(random.randint(1, 3))
                    self.g.append(goody)
            else:
                self.rows.mountrow(self.snake)
            if ischeck:
                if self.snake.l == 1:
                    self.snake.collect(6)
            if self.snake.head:
                if move:
                    if sdl2.SDL_GetTicks() - t_stamp > gameinfo.MIN_T_STAMP:
                        t_stamp = sdl2.SDL_GetTicks()
                        mul += 1
                    self.snake.lasthead = self.snake.head[0]
                    self.snake.move(move, mul)
                for r in self.rows.row:
                    if self.snake.PASS > r.pos > self.snake.head[1] - self.snake.RADIUS:
                        for bl in range(gameinfo.MAX_PER_ROW):
                            if gameinfo.BLOCKSTART_IMG[bl] < self.snake.head[0] < gameinfo.BLOCKEND_IMG[bl]:
                                if r.a[bl] > 0:
                                    self.snake.head[0] = self.snake.lasthead
                                    mouse = False
                                    break
                        break
                for h in self.g:
                    if h.pos > (self.snake.head[1] + self.snake.RADIUS) or h.pos < (self.snake.head[1] - self.snake.RADIUS):
                        continue
                    for c in range(len(h.co)):
                        if self.snake.head[0] - self.snake.RADIUS < h.co[c] < self.snake.head[0] + self.snake.RADIUS:
                            val = h.val[c]
                            h.co.remove(h.co[c])
                            h.val.remove(h.val[c])
                            self.snake.collect(val)
                            h.num -= 1
                            if h.num == 0:
                                self.g.remove(h)
                            break
            if (self.snake.score - d) > gameinfo.SCORE_DIFF:
                d = self.snake.score
                if delay_ == gameinfo.DELAY1:
                    self.snake.s += 1
                    delay_ = gameinfo.DELAY2
                elif delay_ == gameinfo.DELAY2:
                    delay_ = gameinfo.DELAY1
            delay = sdl2.SDL_GetTicks() - C
            if delay < delay_:
                sdl2.SDL_Delay(delay_ - delay)
            self.r.present()
        self.r.clear(gameinfo.COLOR_GRID["black"])
        self.r.present()
        while True:
            events = sdl.get_events()
            for e in events:
                if e.type == sdl2.SDL_QUIT:
                    return False
                elif e.type == sdl2.SDL_KEYDOWN:
                    if e.key.keysym.sym == sdl2.SDLK_q:
                        return False
                    else:
                        return True
                elif e.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    return True
        return True
    
    def __print_update_score(self, gamenumber):
        '''
        prints the score of current game on the terminal window
        also, compares the score with the highscore and
        updates accordingly
        prints the message according to the score in the game
        '''
        score = self.snake.score
        try:
            f = open("support/.highscore", "rb+")
        except FileNotFoundError:
            f = open("support/.highscore", "wb+")
        except:
            return
        if gamenumber: print("Game " + gamenumber.__str__() + ":", end = '')
        x = f.read()
        if x: 
            hs = int.from_bytes(x, 'big')
            if score <= hs:
                if not gamenumber: print("\tUpps!")
                print("\tscore : " + score.__str__())
                if not gamenumber: print("\t(Highscore : %d)" %hs)
            else:
                if not gamenumber: print("\tCongrats!! New Highscore!!!")
                if not gamenumber: print("\tscore : " + score.__str__())
                if gamenumber: print("\tscore : " + score.__str__() + " (New Highscore!)")
                f.seek(0)
                f.write(score.to_bytes(20, 'big'))
        else:
            f.write(score.to_bytes(20, 'big'))
            if not gamenumber: print("\tCongrats!! New Highscore!!!")
            if not gamenumber: print("\tscore : " + score.__str__())
            if gamenumber: print("\tscore : " + score.__str__() + " (New Highscore!)")
        f.close()

