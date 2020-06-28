#CODE BY ISA BOLLING
#Edited by Da'Shawn Larry
import os
os.environ["PYSDL2_DLL_PATH"] = os.path.dirname(os.path.abspath(__file__))
from sdl2 import *
from sdl2.sdlttf import *
import sdl2.ext
import ctypes
import math

#________________CLASSES______________________________#
class Background:
    def __init__(self, w, h, x, y, renderer):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.s_x = 0
        self.s_y = 0
        self.n = self.s_y
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "maps", ".bmp")
        self.image = SDL_LoadBMP(self.path.encode('utf-8'))
        self.bgSurface = SDL_CreateTextureFromSurface(renderer, self.image)
        SDL_FreeSurface(self.image)

    
    def Render(self, renderer):
        ScreenWipe(renderer)
        SDL_RenderCopy(renderer, self.bgSurface, None, None)

    def Quit(self):
        SDL_DestroyTexture(self.bgSurface)

class TextureCache:
    def __init__(self, renderer):
        self.renderer = renderer
        self._cache = dict()

    def LoadTexture(self, filepath):
        if filepath not in self._cache:
            surface = SDL_LoadBMP(filepath.encode('utf-8'))
            self._cache[filepath] = SDL_CreateTextureFromSurface(self.renderer, surface)
            SDL_FreeSurface(surface)
            SDL_SetTextureBlendMode(self._cache[filepath], SDL_BLENDMODE_BLEND)
        return self._cache[filepath]

class Scene:
    def __init__(self, b_cache):
        self.c = b_cache
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "Maps", ".mx")

    def CreateScene(self, cache, renderer, filepath, player, npc, solid):
    #This function loads the map created from the ".mx" file specified.
        global tile_name
        global tile_filepath

        if not filepath.endswith('.mx'):
            return 0

        file = open(filepath, 'r')
        tile_name = ''
        tile_filepath = ''
        for line in file:
            section = line.split('|')
            if (section[0] == '*'):
                subsect = section[1].split(':')
                tile_name = subsect[0]
                tile_filepath = subsect[1]

            elif (section[0] == '+'):
                tiles_information_list = section[1].split(',')
                for tile_info in tiles_information_list:
                    tile_xywh = tile_info.split('-')
                    if (len(tile_xywh) < 4):
                        pass
                    else:
                        x = int(tile_xywh[0])
                        y = int(tile_xywh[1])
                        w = int(tile_xywh[2])
                        h = int(tile_xywh[3])

                    if tile_name == 'player':
                        player.x = x
                        player.y = y
                    elif tile_name == 'npc':
                        if tile_name not in self.c:
                            self.c[tile_name] = [NPC(32, 32, x, y, renderer, 'townfolk1_f.bmp')]
                        else:
                            self.c[tile_name].append(NPC(32, 32, x, y, renderer, 'townfolk1_f.bmp'))
                    elif tile_name == 'npc2':
                        if tile_name not in self.c:
                            self.c[tile_name] = [NPC(32, 32, x, y, renderer, 'townfolk1_m.bmp')]
                        else:
                            self.c[tile_name].append(NPC(32, 32, x, y, renderer, 'townfolk1_m.bmp'))
                    elif tile_name == 'npc3':
                        if tile_name not in self.c:
                            self.c[tile_name] = [NPC(32, 32, x, y, renderer, 'warrior_f.bmp')]
                        else:
                            self.c[tile_name].append(NPC(32, 32, x, y, renderer, 'warrior_f.bmp'))
                    elif tile_name not in self.c:
                        self.c[tile_name] = [GameTile(cache, tile_filepath, x, y, w, h)]
                    else:
                        self.c[tile_name].append(GameTile(cache, tile_filepath, x, y, w, h))
                    
                    
        file.close()

        return self.c
        

class GameTile:
    def __init__(self, cache, filepath, x, y, w, h):
        self.c = cache
        self.name = filepath.split('.bmp')[0]
        self.texture = self.c.LoadTexture(filepath)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.rect = SDL_Rect(self.x, self.y, self.w, self.h)

    def Render(self, camera_pos = (0,0), alpha = 255):
        self.rect.x = (self.x - (self.w//2)) + camera_pos[0]
        self.rect.y = (self.y - (self.h//2)) + camera_pos[1]
        self.rect.w = self.w
        self.rect.h = self.h
        SDL_SetTextureAlphaMod(self.texture, alpha)
        SDL_RenderCopy(self.c.renderer, self.texture, None, self.rect)

    def SetPos(self, x, y):
        self.x = x
        self.y = y

    def GetPos(self):
        return (self.x, self.y)

    def GetInfo(self):
        return (self.x, self.y, self.w, self.h)

class Camera:
    def __init__(self, w, h, speed, p = None, cs = 40 ):
        self.x = 0
        self.y = 0
        self.speed = speed
        self.p = p
        self.last_pos = (p.x, p.y)
        self.cs = cs
        self._rect = SDL_Rect(self.cs // 2, self.cs // 2, w - self.cs, h - self.cs)

    def Show(self, renderer):
        SDL_SetRenderDrawColor(renderer, 0, 0, 255, 255)
        SDL_RenderDrawRect(renderer, self._rect)

    def Process(self):
        self.x -= self.p.x - self.last_pos[0]
        self.y -= self.p.y - self.last_pos[1]
        self.last_pos = (self.p.x, self.p.y)


class AnimatedCharacter:
    def __init__(self, w, h, x, y, renderer, character, camera_pos = (0, 0)):
        self.w = w                      #width
        self.h = h                      #height
        self.x = x                      #Character's x position
        self.y = y                      #Character's y position
        self.s_x = 0                    #Sprite map x
        self.s_y = 0                    #Sprite map y
        self.n = self.s_y
        self.Moving = False
        self.Animate = False
        self.A_Rate = 0
        self.dest_rect = SDL_Rect(self.x + camera_pos[0], self.y + camera_pos[1], 30, 32)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "sprites", character)
        self.image = SDL_LoadBMP(self.path.encode('utf-8'))
        self.texture = SDL_CreateTextureFromSurface(renderer, self.image)
        SDL_FreeSurface(self.image)

    def Render(self, renderer, camera_pos = (0, 0)):
        self.s_y = self.n
        self.src_rect = SDL_Rect(self.s_x, self.s_y, self.w, self.h)
        self.dest_rect = SDL_Rect(self.x + camera_pos[0], self.y + camera_pos[1], 30, 32)           #Scales the Sprite down to size
        SDL_RenderFillRect(renderer, self.dest_rect)
        SDL_RenderCopy(renderer, self.texture, self.src_rect, self.dest_rect)

    def Movement(self, state, direction):
        self.direction = direction
        if (state == True):
            self.Moving = True
            self.Animate = True
            if (direction == 'left'):
                self.x -= 2
            elif (direction == 'right'):
                self.x += 2
            elif (direction == 'down'):
                self.y += 2
            elif (direction == 'up'):
                self.y -= 2
        elif (state == False):
            self.Moving = False
            self.Animate = False
    def Animating(self):
        if self.Animate == True:
            self.A_Rate += 1

        #Animations for Movement and Actions
        if self.Moving == True:
            if self.A_Rate == 4:
                self.A_Rate = 0
                if self.direction == 'left':
                    self.n = 108
                    self.s_x += 32
                    if self.s_x >= 95:
                        self.s_x = 0
                if self.direction == 'right':
                    self.n = 36
                    self.s_x += 32
                    if self.s_x >= 95:
                        self.s_x = 0
                if self.direction == 'up':
                    self.n = 0
                    self.s_x += 32
                    if self.s_x >= 95:
                        self.s_x = 0
                if self.direction == 'down':
                    self.n = 72
                    self.s_x += 32
                    if self.s_x >= 95:
                        self.s_x = 0


    def Quit(self):
        SDL_DestroyTexture(self.texture)

class AnimatedButton:
    def __init__(self, w, h, x, y, renderer, button):
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.s_x = 0
        self.s_y = 0
        self.n = self.s_y
        self.Animate = True
        self.A_Rate = 0
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                            "resources", button)
        self.image = SDL_LoadBMP(self.path.encode('utf-8'))
        self.texture = SDL_CreateTextureFromSurface(renderer, self.image)
        SDL_FreeSurface(self.image)

    def Animating(self):
        if self.Animate == True:
            self.A_Rate += 1
            

        #Animations for Movement and Actions
        if self.Animate == True:
            if self.A_Rate == 4:
                self.A_Rate = 0
                if self.n == 0:
                    self.s_x += 20
                    if self.s_x >= 80:
                        self.s_x = 0

    def Render(self, renderer):
        self.s_y = self.n
        self.src_rect = SDL_Rect(self.s_x, self.s_y, self.w, self.h)
        self.dest_rect = SDL_Rect(self.x, self.y, 24, 27)
        SDL_RenderCopy(renderer, self.texture, self.src_rect, self.dest_rect)
    
    def Quit(self):
        SDL_DestroyTexture(self.texture)

class PausedMenu:
    def __init__(self, w, h, x, y, renderer, pmenu, menu):
        self.w = w
        self.h = h
        self.x = x
        self.y = y 
        self.menu = menu
        self.s_x = 0
        self.s_y = 0
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                            "resources", pmenu)
        self.image = SDL_LoadBMP(self.path.encode('utf-8'))
        self.texture = SDL_CreateTextureFromSurface(renderer, self.image)
        SDL_FreeSurface(self.image)

    def Render(self, renderer):
        self.src_rect = SDL_Rect(self.s_x, self.s_y, self.w, self.h)
        self.dest_rect = SDL_Rect(self.x, self.y, self.w, self.h + 200)
        SDL_RenderCopy(renderer, self.texture, self.src_rect, self.dest_rect)
        for items in self.menu:
            items.Render()


class NPC:
    def __init__(self, w, h, x, y, renderer, npc, camera_pos = (0, 0)):
        self.w = w                      #width
        self.h = h                      #height
        self.x = x                      #Character's x position
        self.y = y                      #Character's y position
        self.s_x = 32                   #Sprite map x        
        self.s_y = 74                   #Sprite map y
        self.n = self.s_y
        self.dest_rect = SDL_Rect(self.x + camera_pos[0], self.y + camera_pos[1], 30, 33)
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "npcs", npc)
        self.image = SDL_LoadBMP(self.path.encode('utf-8'))
        self.texture = SDL_CreateTextureFromSurface(renderer, self.image)
        SDL_FreeSurface(self.image)

    def Render(self, renderer, camera_pos=(0, 0)):
        self.s_y = self.n
        self.src_rect = SDL_Rect(self.s_x, self.s_y, self.w, self.h)
        self.dest_rect = SDL_Rect(self.x + camera_pos[0], self.y + camera_pos[1], 30, 33)
        SDL_RenderCopy(renderer, self.texture, self.src_rect, self.dest_rect)

    def Quit(self):
        SDL_DestroyTexture(self.texture)

class TextObject:
    fonts = dict()
    def __init__(self, renderer, text, width, height, font_name, color = (0, 0, 0), location = (0, 0), font_size = 36):
        self.r = renderer
        if len(font_name) > 1:
            TextObject.fonts[font_name[0]] = TTF_OpenFont(font_name[1], font_size)
        self.color = SDL_Color(color[0], color[1], color[2])
        self.surface = TTF_RenderText_Solid(TextObject.fonts[font_name[0]], text.encode('utf-8'), self.color)
        self.message = SDL_CreateTextureFromSurface(self.r, self.surface)
        SDL_FreeSurface(self.surface)
        self.rect = SDL_Rect(location[0], location[1], width, height)
        self.highlight = False
        SDL_SetTextureBlendMode(self.message, SDL_BLENDMODE_BLEND)

    def Render(self, x=None, y=None, alpha = 255):
        if self.highlight:
            SDL_SetRenderDrawColor(self.r, self.color.r, self.color.g, self.color.b, self.color.a)
            SDL_RenderDrawRect(self.r, self.rect)
        if x is None and y:
            self.rect.y = y
        elif x and y is None:
            self.rect.x = x
        elif x and y:
            self.rect.x = x
            self.rect.y = y
        SDL_SetTextureAlphaMod(self.message, alpha)
        SDL_RenderCopy(self.r, self.message, None, self.rect)

    def __del__(self):
        for keys in list(TextObject.fonts):
            font = TextObject.fonts.pop(keys, None)
            if font: TTF_CloseFont(font)
        SDL_DestroyTexture(self.message)

class Pointer:
    cursors = dict()

    def __init__(self):
        self.x = 0
        self.y = 0
        self.pointer = SDL_Rect(0, 0, 10, 10)
        self.clicking = False
        self.r_clicking = False

    def Compute(self, event):
        self.clicking = False
        self.r_clicking = False

        if (event.type == SDL_MOUSEBUTTONDOWN):
            if (event.button.button == SDL_BUTTON_LEFT):
                self.clicking = True

            if (event.button.button == SDL_BUTTON_RIGHT):
                self.r_clicking = True
        
        if (event.type == SDL_MOUSEBUTTONUP):
            if (event.button.button == SDL_BUTTON_LEFT):
                self.clicking = False
            
            if (event.button.button == SDL_BUTTON_RIGHT):
                self.r_clicking = False

        if (event.type == SDL_MOUSEMOTION):
            self.pointer.x = event.motion.x
            self.pointer.y = event.motion.y

        self.x = self.pointer.x
        self.y = self.pointer.y

    def Is_Touching_Rect(self, rect): #version for rectangles
        return SDL_HasIntersection(self.pointer, rect)

    def Is_Clicking_Rect(self, rect):
        return self.Is_Touching_Rect(rect) and self.clicking

    def Is_Touching(self, item):
        return self.Is_Touching_Rect(item.rect)

    def Is_Clicking(self, item):
        return self.Is_Touching(item) and self.clicking


    def Is_R_Clicking(self, item):
        return self.Is_Touching(item) and self.r_clicking

    def Set_Cursor(self, id):
        if id not in Pointer.cursors:
            Pointer.cursors[id] = SDL_CreateSystemCursor(id)
        SDL_SetCursor(Pointer.cursors[id])

    def __del__(self):
        for cursor in Pointer.cursors:
            SDL_FreeCursor(Pointer.cursors[cursor])

class Time:
    def __init__(self, game_time = 0, T_rate = 120, seconds = 0, minutes = 0, hour = 0):
        self.miliseconds = game_time
        self.seconds = seconds
        self.minutes = minutes
        self.hour = hour
        self.T_rate = T_rate

    def Process(self):
        if self.miliseconds % 1000 == 0:
            self.seconds += 1
            self.miliseconds = 0
        if self.seconds == 60:
            self.minutes += 1
            self.seconds = 0
        if self.minutes == 60:
            self.hour += 1
            self.minutes = 0
    
    def TPS(self):
        ticks = 0
        start_time_ms = int(SDL_GetTicks())
        elapsed_time_ms = int(SDL_GetTicks() - start_time_ms)
        SDL_Delay(1000//self.T_rate - elapsed_time_ms)
        seconds_per_frame = (SDL_GetTicks() - start_time_ms) / 1000
        if seconds_per_frame > 0:
            ticks = 1 // seconds_per_frame
        return start_time_ms, ticks



    

#________________FUNCTIONS____________________________#
def ScreenPresent(renderer):
    SDL_RenderPresent(renderer)

def ScreenWipe(renderer):
    SDL_RenderClear(renderer)

def WindowState(window, renderer, fs):
    if (fs == True):
        SDL_SetWindowFullscreen(window, SDL_WINDOW_FULLSCREEN)
    elif (fs == False):
        SDL_SetWindowFullscreen(window, 0)

def GetCharacters():
    resources = dict()
    for path in os.listdir('sprites'):
        c = path.split(".bmp")
        resources[c[0]] = path
    
    return resources

def CheckCollision(a, b, renderer):

    def showBorders(top, bottom, left, right):
        left.Render(alpha = 0)
        bottom.Render(alpha = 0)
        right.Render(alpha = 0)
        top.Render(alpha = 0)

    leftA = a.dest_rect.x
    rightA = a.dest_rect.x + a.dest_rect.w
    topA = a.dest_rect.y
    bottomA = a.dest_rect.y + a.dest_rect.h

    
    leftL = TextObject(renderer, "|", 1, 28, ['joystix', b'joystix.ttf'], color= (0, 0, 0), location=(leftA + 1, topA))
    bottomL = TextObject(renderer, "__", 32, 1, ['joystix'], color= (0, 0, 0), location=(leftA, bottomA + 1))
    rightL = TextObject(renderer, "|", 1, 28, ['joystix'], color= (0, 0, 0),location=(rightA - 1, topA))
    topL = TextObject(renderer, "__", 32, 1, ['joystix'], color= (0, 0, 0),location=(leftA, topA - 2))
    
    if SDL_HasIntersection(topL.rect, b.dest_rect):
        a.y = b.y + (b.h + 5)
        showBorders(topL, bottomL, leftL, rightL)
        return True
    elif SDL_HasIntersection(leftL.rect, b.dest_rect):
        a.x = b.x + (b.w - 3)
        showBorders(topL, bottomL, leftL, rightL)
        return True
    elif SDL_HasIntersection(bottomL.rect, b.dest_rect):
        a.y = b.y - (b.h + 7)
        showBorders(topL, bottomL, leftL, rightL)
        return True
    elif SDL_HasIntersection(rightL.rect, b.dest_rect):
        a.x = b.x - (b.w + 3)
        showBorders(topL, bottomL, leftL, rightL)
        return True
        


def CanInteract(a, b):

    d = math.sqrt(abs(a.dest_rect.x - b.dest_rect.x)**2 + abs(a.dest_rect.y - b.dest_rect.y)**2)    # Actual math distance formula to calculate distance between object and player
    if d <= 40:
        return True
    else:
        return False
    #if a.dest_rect.x < b.dest_rect.x:
     #   if (b.dest_rect.x - a.dest_rect.x) <= 30:
      #      return True
    #elif b.dest_rect.x < a.dest_rect.x:
     #   if (a.dest_rect.x - b.dest_rect.x) <= 30:
      #      return True
    #elif a.dest_rect.y < b.dest_rect.y:           
     #   if (b.dest_rect.y - a.dest_rect.y) <= 30:
      #      return True
    #elif b.dest_rect.y < a.dest_rect.y:
     #   if (a.dest_rect.y - b.dest_rect.y) <= 30:
      #      return True
    #else:
        #False    



def SaveData():
    pass


def main():
    SDL_Init(SDL_INIT_VIDEO)
    if (TTF_Init() == -1):
        print("TTF_Init: ", TTF_GetError())


    #__________________GLOBAL VARIABLES_________________________#
    running = True
    WIDTH = 640
    HEIGHT = 480
    TickRate = 120
    player = None
    paused = False
    Fullscreen = False
    gamestate = 'MENU'
    sprite_list = GetCharacters()
    characters = []
    character_selection = None
    character_selection_list = dict()
    menu_num = 0
    read_key = True

    #_______________Window and Renderer___________________#
    mouse = Pointer()
    SDL_SetHint(SDL_HINT_RENDER_DRIVER, b'opengl')
    window = SDL_CreateWindow(b"R_Dokutsu Monogatari", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED,
                     WIDTH, HEIGHT, 0)
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_PRESENTVSYNC)
    event = SDL_Event()
    SDL_SetRenderDrawBlendMode(renderer, SDL_BLENDMODE_BLEND)
    SDL_ShowCursor(SDL_ENABLE)

    #_______________Key Handling__________________________________________#
    #keys = {
        #"UP" : key[SDL_SCANCODE_UP],
       # "DOWN" : key[SDL_SCANCODE_DOWN],
      #  "P" : key[SDL_SCANCODE_P],
     #   "F12" : key[SDL_SCANCODE_F12]
    #}

    
    
    #________________OBJECTS______________________________#

    menu_items = {
        "New Game": TextObject(renderer, "New Game", 200, 50, ['joystix', b'joystix.ttf'], location=(240, 260)),
        "Load Game": TextObject(renderer, "Load Game", 200, 50, ['joystix'], location=(240, 320))
    }

    choice = {
        "Yes": TextObject(renderer, "Yes", 100, 50, ['joystix'], location=(200, 300)),
        "No": TextObject(renderer, "No", 100, 50, ['joystix'], location=(300, 300))
    }

    p_menu_items = [
        TextObject(renderer, "Inventory", 100, 25, ['joystix'], color=(255, 40, 40), location=(50, 152), font_size=(10)),
        TextObject(renderer, "Save", 100, 25, ['joystix'], color=(255, 40, 40), location=(50, 202), font_size=(10)),
        TextObject(renderer, "Options", 100, 25, ['joystix'], color=(255, 40, 40), location=(50, 252), font_size=(10))
    ]


    cache = TextureCache(renderer)

    xs = 0
    for c in sprite_list:
        character_selection_list[c] = TextObject(renderer, c, 100, 25, ['joystix'], location=(250, 260 - xs))
        xs += 25

    for c in sprite_list:
        characters.append(c)
    
    GameTime = Time()


    #______________GENERAL PROCESSING______________________#
    event = SDL_Event()
    while (running):
        direction = ''
        movement = False

        #EVENTS_____________________________________________#
        #___KeyEvents_______________________________________#
        key = SDL_GetKeyboardState(None)

        if (key[SDL_SCANCODE_LEFT]):
            if not paused:
                movement = True
                direction = 'left'

        if (key[SDL_SCANCODE_RIGHT]):
            if not paused:
                movement = True
                direction = 'right'

        if (key[SDL_SCANCODE_UP]):
            if not paused:
                movement = True
                direction = 'up'
            elif paused:
                if read_key == True:
                    menu_num -= 1
                    if menu_num < 0:
                        menu_num = len(p_menu_items)-1
                    read_key = False
                elif read_key == False:
                    pass

        if (key[SDL_SCANCODE_DOWN]):
            if not paused:
                movement = True
                direction = 'down'
            elif paused:
                if read_key == True:
                    menu_num += 1
                    if menu_num > len(p_menu_items) - 1:
                        menu_num = 0
                    read_key = False
                elif read_key == False:
                    pass
        
        if read_key == True:
            if (key[SDL_SCANCODE_P]):
                if not (paused):
                    paused = True
                    read_key = False
                elif paused:
                    paused = False
                    read_key = False


        if (key[SDL_SCANCODE_F12]):
            if Fullscreen == False:
                Fullscreen = True
            elif Fullscreen == True:
                Fullscreen = False

        if (key[SDL_SCANCODE_ESCAPE]):
            SDL_Quit()
            TTF_Quit()
            running = False
            
        # ________________________________________________#
        WindowState(window, renderer, Fullscreen)
        #___________________________________________________#
        while (SDL_PollEvent(ctypes.byref(event))):
            mouse.Compute(event)
            if (event.type == SDL_QUIT):
                SDL_DestroyRenderer(renderer)
                #background.Quit()
                SDL_DestroyWindow(window)
                running = False
                break

        #LOGIC__________________________________________________#
        if (gamestate == 'MENU'):
            for item in menu_items:
                if (mouse.Is_Touching(menu_items[item])):
                    menu_items[item].highlight = True
                else:
                    menu_items[item].highlight = False
                
                if (mouse.Is_Clicking(menu_items["New Game"])):
                    gamestate = 'CHARACTER SELECTION'

        if (gamestate == 'CHARACTER SELECTION'):
            for character in character_selection_list:
                if (mouse.Is_Touching(character_selection_list[character])):
                    character_selection_list[character].highlight = True
                else:
                    character_selection_list[character].highlight = False
                
                if (mouse.Is_Clicking(character_selection_list[character])):
                    character_selection = character
                    preview = AnimatedCharacter(32, 32, 200, HEIGHT - 50, renderer, sprite_list[character_selection])
            
            for c in choice:
                if (mouse.Is_Touching(choice[c])):
                    choice[c].highlight = True
                else:
                    choice[c].highlight = False
                
                if (mouse.Is_Clicking(choice[c])):
                    if c == "Yes":
                        player = AnimatedCharacter(32, 36, WIDTH//2, HEIGHT//2, renderer, sprite_list[character_selection])
                        gamestate = 'GAME'
                    else:
                        character_selection = None
                    camera = Camera(WIDTH, HEIGHT, speed = 3, p = player)
                    z_interact = AnimatedButton(20, 26, WIDTH//2, HEIGHT-50, renderer, 'Z_interact.bmp')
                    pmenu = PausedMenu(192, 192, 25, 50, renderer, 'ScrollMenu.bmp', p_menu_items)
                    scene = Scene(dict())
                    SceneOne = scene.CreateScene(cache, renderer, 'Maps/Game-1.mx', player, None, None)

        if (gamestate == 'GAME'):
            ticks = GameTime.TPS()
            GameTime.Process()

            if ticks[0] % 30 == 0:
                read_key = True

            if (player):
                player.Movement(movement, direction)
                player.Animating()
                camera.Process()
            
            #Collision Checks
            for objects in SceneOne:
                if objects == 'npc':
                    for stuff in SceneOne[objects]:
                        CheckCollision(player, stuff, renderer)

            #Interaction Checks
            for npc in SceneOne['npc']:
                if CanInteract(player, npc):
                    z_interact.Animating()
            
            #Pause Menu Logic
            if paused:
                for items in p_menu_items:
                    if p_menu_items[menu_num] == items:
                        p_menu_items[menu_num].highlight = True
                    else:
                        items.highlight = False
            

        #RENDERING______________________________________________#
        SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
        SDL_RenderClear(renderer)

        if (gamestate == 'MENU'):
            for item in menu_items:
                menu_items[item].Render()
        
        if (gamestate == 'CHARACTER SELECTION'):
            SDL_RenderClear(renderer)
            
            for c in character_selection_list:
                character_selection_list[c].Render()

            if (character_selection):
                preview.Render(renderer)
                preview.Movement(True, 'right')
                preview.Animating()
                if preview.x > WIDTH:
                    preview.x = -1
                for c in choice:
                    choice[c].Render()

        if (gamestate == 'GAME'):
            SDL_RenderClear(renderer)
            for tiles in SceneOne:
                for piece in SceneOne[tiles]:
                    if tiles == 'player':
                        piece.Render(renderer)
                    elif tiles == 'npc':
                        piece.Render(renderer, (camera.x, camera.y))
                    elif tiles == 'npc2':
                        piece.Render(renderer,(camera.x, camera.y))
                    elif tiles == 'npc3':
                        piece.Render(renderer, (camera.x, camera.y))
                    else:
                        piece.Render(camera_pos=(camera.x, camera.y))
                    
            camera.Show(renderer)
            player.Render(renderer, camera_pos=(camera.x, camera.y))

            for npc in SceneOne['npc']:
                if (CanInteract(player, npc)):     
                    z_interact.Render(renderer)

            if paused == True:
                pmenu.Render(renderer)
            
            #if paused == False:
                #print(GameTime.hour, ":", GameTime.minutes, ":", GameTime.seconds)
            


       # background.Render()
        SDL_RenderPresent(renderer)
        SDL_Delay(10)
        
    SDL_Quit()
    return 0
    #_____________
main()