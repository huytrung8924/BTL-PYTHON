import pygame
import pickle
from os import path
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init() # khởi tạo

clock = pygame.time.Clock() # hàm kiểm soát tốc độ khung hình
fps = 60

screen_width = 800 # chiều rộng màn hình
screen_height = 800 # chiều cao màn hình

screen = pygame.display.set_mode((screen_width,screen_height)) #hàm tạo cửa sổ game
pygame.display.set_caption('NHÓM 1')# tạo chú thích cho cửa sổ

# tạo font chữ
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)

# tạo màu chữ
purple = (128, 0, 128)
blue = (0, 0, 255)

# các biến
tile_size = 40
game_over = 0
main_menu = True
level = 1
max_levels = 6
score = 0

#tải ảnh
bg_img = pygame.image.load('img/bg.png')
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')
coin_img = pygame.image.load('img/coinGold.png')
coin_img = pygame.transform.scale(coin_img , (20,20))

# tải âm thanh
#âm thanh nhạc nền
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
#âm thanh nhận coin
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
#âm thanh khi nhảy
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
#âm thanh khi chết
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

#hàm vẽ chữ lên màn hình
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col) # tạo ảnh từ dòng chữ
    screen.blit(img, (x, y))

# hàm reset level
def reset_level(level):
    player.reset(80, screen_height - 100)
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()
    coin_group.empty()

    # load và tạo map mới
    if path.exists(f'level{level}_data'):
        pickle_in = open(f'level{level}_data', 'rb')  # mở file nhị phân
        world_data = pickle.load(pickle_in)  # đọc file nhị phân
    world = World(world_data)

    return world

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False # kiem tra nut co duoc nhan k
        #lấy vị trí chuột
        pos=pygame.mouse.get_pos()
        #kiểm tra điều kiện di chuột và nhấp chuột
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:# nếu nhấn chuột trái
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image,self.rect) # vẽ nút

        return action

class Player():
    def __init__(self,x,y):
        self.reset(x,y)

    def update(self,game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5 #sau 5 khung hình ảnh mới đổi 1 lần
        col_thresh = 20
        if game_over == 0:
            # nhấn phím
            key = pygame.key.get_pressed() # hàm kiểm tra phím nào đang được nhấn
            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
                jump_fx.play()
                self.vel_y = -14
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # xu ly anh dong
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # thêm trọng lực
            self.vel_y += 1
            if self.vel_y > 12:
                self.vel_y = 12
            dy += self.vel_y

            # kiem tra va chạm
            self.in_air = True  # gia dinh rang dang o khong trung
            for tile in world.tile_list:
                # kiem tra theo huong x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height): # hàm kiểm tra 2 hình chữ nhật có va chạm k
                    dx = 0
                # kiem tra theo huong y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    if self.vel_y < 0: # neu dang di len
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                    elif self.vel_y >= 0: # neu dang roi xuong
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.in_air = False

            # kiem tra va cham voi ke dich
            if pygame.sprite.spritecollide(self,blob_group,False):
                game_over = -1
                game_over_fx.play()
            if pygame.sprite.spritecollide(self,lava_group,False):
                game_over = -1
                game_over_fx.play()
            if pygame.sprite.spritecollide(self,exit_group,False):
                game_over = 1


            # kiểm tra va chạm với platform
            for platform in platform_group:
                # kểm tra theo hướng x
                if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # kiểm tra theo hướng y
                if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # kiểm tra phía dưới platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0
                        dy = platform.rect.bottom - self.rect.top
                    # kiểm tra phía trên platform
                    if abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False
                        dy = 0
                    # di chuyển sang một bên với nền tảng
                    if platform.move_x != 0:
                        self.rect.x += platform.move_direction

            # cap nhat toa do nhan vat
            self.rect.x += dx
            self.rect.y += dy

        # hinh anh khi nhan vat chet
        elif game_over == -1:
            self.image = self.dead_image
            if self.death_y < 200:
                self.death_y +=5
                self.rect.y -=5

        # ve nhan vat len man hinh
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return game_over

    def reset(self, x, y):
        self.images_right = [] #lưu danh sách ảnh khi di chuyển sang phải
        self.images_left = []
        self.index = 0
        self.counter = 0 # số khung hình nhân vật đi
        for num in range(1,5):
            img_right = pygame.image.load(f'img/guy{num}.png')
            img_right = pygame.transform.scale(img_right, (30, 60))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_right.append(img_right)
            self.images_left.append(img_left)
        self.dead_image = pygame.image.load('img/ghost.png')
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width() # chiều rông nhân vật
        self.height = self.image.get_height() # Chiều cao nhân vật
        self.vel_y = 0 # vận tốc khi nhảy (để xử lý nhảy và trọng lực)
        self.jumped = False #kiểm tra xem nhảy hay chưa
        self.direction = 0 #xác định hướng ảnh
        self.death_y = 0 # khoảng cách bay khi chết
        self.in_air = False # kiểm tra xem có đang ở không trung

class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('img/dirt.png')
        grass_img = pygame.image.load('img/grass.png')

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))# đảm bảo hình ảnh bằng với các ô đã chia nhỏ
                    img_rect = img.get_rect()# tạo 1 hình chữ nhật bao quanh hình ảnh
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)# hình ảnh và tọa độ
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 20)
                    blob_group.add(blob)
                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)
                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size+ 20)
                    lava_group .add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size -20)
                    exit_group .add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1]) # duyệt qua từng ô và hiển thị lên màn hình
            #pygame.draw.rect(screen, (255, 255, 255), tile[1], 1)# vẽ 1 hcn lên màn hình
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image_left = pygame.image.load('img/slimeWalk1.png')
        self.image_right = pygame.transform.flip(self.image_left, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1 #hướng di chuyển
        self.move_counter = 0 # đếm số lần di chuyển

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if self.move_direction > 0:
            self.image = self.image_right
        else:
            self.image = self.image_left
        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= -1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, move_x, move_y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/platform.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0 # đếm số lần đã di chuyển
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/lava.png')
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/coinGold.png')
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('img/exit.png')
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
player= Player(80,screen_height -100)

#  tạo một nhóm (group) sprite
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()

# tạo đồng xu để hiển thị điểm

# load và tạo map mới
if path.exists(f'level{level}_data'):
    pickle_in = open(f'level{level}_data', 'rb') #mở file nhị phân
    world_data = pickle.load(pickle_in) # đọc file nhị phân
world = World(world_data)

#tạo nút
restart_button = Button(screen_width // 2 - 100, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 -100 , screen_height // 2, start_img)
exit_button = Button(screen_width // 2 -100, screen_height // 2+200, exit_img)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg_img, (0,0)) # hiển thị lên màn hình với tọa độ 0,0
    if main_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            main_menu = False
    else:
        world.draw()
        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)

        game_over = player.update(game_over) #cập nhật trạng thái game hiện tại

        # nếu game vẫn hoạt động
        if game_over == 0:
            screen.blit(coin_img, (10,10))
            blob_group.update()
            platform_group.update()
            # nếu người chơi đã thu thập coin
            if pygame.sprite.spritecollide(player,coin_group,True):
                score += 1
                coin_fx.play()
            draw_text('X ' + str(score), font_score, purple, tile_size , 5)

        # nếu thua
        if game_over == -1 and player.death_y < 200:
            draw_text('GAME OVER!', font, blue, (screen_width // 2) - 180, screen_height // 2)
        elif game_over == -1 and player.death_y >= 200:
            screen.blit(bg_img, (0, 0))
            if restart_button.draw():
                level = 1
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0

        # nếu đã hoàn thành level hiện tại
        if game_over == 1:
            # chuyển sang level tiếp theo
            level+=1
            if level <= max_levels:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:# nếu hoàn thành trò chơi
                screen.blit(bg_img, (0, 0))
                draw_text('YOU WIN', font, blue, (screen_width // 2) - 130, screen_height // 2)
                if restart_button.draw(): # nếu nhấn nút khới động lại
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0


    for event in pygame.event.get():# hàm thu thập sự kiện
        if event.type == pygame.QUIT:# thoát game khi ấn X
            run = False

    pygame.display.update()# cập nhật nội dung lên màn hình

pygame.quit()