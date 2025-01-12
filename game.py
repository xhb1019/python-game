import pygame
import sys
import random
from openai import OpenAI
from typing import List, Dict

pygame.init()

def load_map(image_path, width, height):
    bg = pygame.image.load(image_path).convert()
    bg = pygame.transform.scale(bg, (width, height))
    return bg, bg.get_rect()

def find_non_colliding_position(rect, obstacle_group, bg_width, bg_height):
    while True:
        rect.center = (random.randint(50, bg_width - 50), random.randint(50, bg_height - 50))
        if not any(rect.colliderect(obstacle.rect) for obstacle in obstacle_group):
            break

def draw_dialog_box(win, text):
    # 设置字体和大小
    font = pygame.font.Font(None, 28)  # 减小字体大小

    # 以一定边距计算对话框的宽高
    margin = 20
    dialog_width = screen_width - 100
    wrapped_lines = wrap_text(text, font, dialog_width - margin)

    # 根据行数动态调整对话框高度
    dialog_height = min(len(wrapped_lines) * 30 + 70, 300)  # 每行30像素的高度，最多300像素
    dialog_box = pygame.Rect(50, screen_height - dialog_height - 50, dialog_width, dialog_height)

    # 创建一个透明的背景
    dialog_bg = pygame.Surface((dialog_box.width, dialog_box.height), pygame.SRCALPHA)
    dialog_bg.fill((255, 255, 255, 200))  # 设置透明度，200为半透明
    win.blit(dialog_bg, dialog_box.topleft)  # 绘制对话框背景

    # 绘制对话框边框
    pygame.draw.rect(win, black, dialog_box, 2)

    # 将文本渲染到对话框中，支持多行文本
    for i, line in enumerate(wrapped_lines):
        line_surface = font.render(line, True, black)
        win.blit(line_surface, (dialog_box.x + 10, dialog_box.y + 10 + i * 30))

    # 选项的位置和大小
    option_width = 80
    option_height = 40
    option_margin = 10

    options_y_offset = dialog_box.y + dialog_box.height - option_height - option_margin

    # 否选项的位置
    no_option = pygame.Rect(dialog_box.x + dialog_box.width - option_width - option_margin, 
                            options_y_offset, option_width, option_height)
    pygame.draw.rect(win, black, no_option, 2)  # 绘制否选项边框
    no_text = font.render("No", True, black)
    win.blit(no_text, (no_option.x + 10, no_option.y + 5))

    # 是选项的位置
    yes_option = pygame.Rect(no_option.x - option_width - option_margin, 
                             options_y_offset, option_width, option_height)
    pygame.draw.rect(win, black, yes_option, 2)
    yes_text = font.render("Yes", True, black)
    win.blit(yes_text, (yes_option.x + 10, yes_option.y + 5))

    return yes_option, no_option

def draw_interaction_box(win, user_text, npc_text):
    # 设置字体和大小
    font = pygame.font.Font(None, 36)

    # 对话框的位置和大小
    dialog_width = screen_width - 100
    user_wrapped_lines = wrap_text(user_text, font, dialog_width - 40)
    npc_wrapped_lines = wrap_text(npc_text, font, dialog_width - 40)

    # 计算对话框高度
    dialog_height = (len(user_wrapped_lines) + len(npc_wrapped_lines)) * 30 + 70  # 每行30像素的高度
    dialog_box = pygame.Rect(50, screen_height - dialog_height - 50, dialog_width, dialog_height)

    # 创建一个透明的背景
    dialog_bg = pygame.Surface((dialog_box.width, dialog_box.height), pygame.SRCALPHA)
    dialog_bg.fill((255, 255, 255, 128))  # 设置透明度，128为半透明
    win.blit(dialog_bg, dialog_box.topleft)  # 绘制对话框背景

    # 绘制对话框边框
    pygame.draw.rect(win, black, dialog_box, 2)

    # 将用户文本渲染到对话框中，支持多行文本
    user_text_y_offset = 10
    for i, line in enumerate(user_wrapped_lines):
        line_surface = font.render(line, True, black)
        win.blit(line_surface, (dialog_box.x + 10, dialog_box.y + user_text_y_offset + i * 30))

    # 将NPC的文本渲染到对话框中，支持多行文本
    npc_text_y_offset = user_text_y_offset + len(user_wrapped_lines) * 30 + 20  # 20像素的间隔
    for i, line in enumerate(npc_wrapped_lines):
        line_surface = font.render(line, True, black)
        win.blit(line_surface, (dialog_box.x + 10, dialog_box.y + npc_text_y_offset + i * 30))

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    while len(words) > 0:
        line = ''
        while len(words) > 0 and font.size(line + words[0])[0] <= max_width:
            line += words.pop(0) + ' '
        lines.append(line.rstrip())
    return lines

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.move(self.camera.topleft)

    def update(self, target):
        x = -target.x + int(screen_width / 2)
        y = -target.y + int(screen_height / 2)

        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - screen_width), x)
        y = max(-(self.height - screen_height), y)

        self.camera = pygame.Rect(x, y, self.width, self.height)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()  # 加载指定的图片
        self.image = pygame.transform.scale(self.image, (width, height))  # 调整图片尺寸
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# 新增宝箱类
class TreasureChest(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(".\\assets\\npc\\baoxiang.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.collected = False  # 新增属性，标识宝箱是否已被收集

def generate_dialog(context: str) -> str:
    # 添加用户消息到messages列表
    messages.append({"role": "user", "content": context})
    # 获取AI回复
    response = client.chat.completions.create(
        model="llama3.2",
        messages=messages,
    )
    assistant_reply = response.choices[0].message.content
    # 将助手回复添加到消息历史
    messages.append({"role": "assistant", "content": assistant_reply})
    return assistant_reply

def distance(rect1, rect2):
    return abs(rect1.x - rect2.x) + abs(rect1.y - rect2.y)

# 新增传送门类
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(".\\assets\\background\\portal.png").convert_alpha()  # 加载指定的图片
        self.image = pygame.transform.scale(self.image, (width, height))  # 调整图片尺寸
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# 新增BOSS类
class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# 初始化Pygame
fullscreen = False
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)  # 初始全屏
pygame.display.set_caption('Game Interface')

# 初始化音乐混合器
pygame.mixer.init()

# 第一个场景的背景音乐
pygame.mixer.music.load('.\\assets\\bgm\\city.mp3')  # 替换为你的音乐文件路径
pygame.mixer.music.play(-1)

# 颜色设置
white = (255, 255, 255)
black = (0, 0, 0)
grey = (128, 128, 128)

# AI客户端初始化
client = OpenAI(
    base_url='http://10.15.88.73:5024/v1',
    api_key='ollama',  # required but ignored
)

messages: List[Dict] = [
    {"role": "system",
     "content": "Tell me(the player) that I need to collect energy by opening treasure chests to defeat the BOSS,and player should collect 6 energy by opening treasure chests to defeat the BOSS.Your answer should be less than 30 words."}
]

# 第一个场景的背景和NPC
bg1, bg_rect1 = load_map('.\\assets\\background\\wild.png', screen_width * 2, screen_height * 2)
BG_WIDTH1, BG_HEIGHT1 = bg_rect1.width, bg_rect1.height

player = pygame.image.load('.\\assets\\player\\5.png').convert_alpha()
player = pygame.transform.scale(player, (50, 50))
player_rect = player.get_rect()

# 第一个场景的两个NPC
monster1 = pygame.image.load('.\\assets\\npc\\npc.png').convert_alpha()
monster1 = pygame.transform.scale(monster1, (50, 50))
monster_rect1 = monster1.get_rect()

monster2 = pygame.image.load('.\\assets\\unused\\skeleton.png').convert_alpha()
monster2 = pygame.transform.scale(monster2, (50, 50))
monster_rect2 = monster2.get_rect()

# 创建障碍物组
obstacle_group1 = pygame.sprite.Group()

# 随机生成障碍物
for _ in range(10):
    obstacle_rect = pygame.Rect(0, 0, 50, 50)  # 创建一个临时的rect对象
    find_non_colliding_position(obstacle_rect, obstacle_group1, BG_WIDTH1, BG_HEIGHT1)
    obstacle = Obstacle(obstacle_rect.x, obstacle_rect.y, obstacle_rect.width, obstacle_rect.height, '.\\assets\\tiles\\tree.png')
    obstacle_group1.add(obstacle)

# 确保玩家初始位置不与任何障碍物重叠
find_non_colliding_position(player_rect, obstacle_group1, BG_WIDTH1, BG_HEIGHT1)

# 确保NPC位置不与任何障碍物重叠
find_non_colliding_position(monster_rect1, obstacle_group1, BG_WIDTH1, BG_HEIGHT1)
find_non_colliding_position(monster_rect2, obstacle_group1, BG_WIDTH1, BG_HEIGHT1)

# 创建宝箱组
treasure_chest_group = pygame.sprite.Group()

# 随机生成宝箱
for _ in range(5):  # 生成5个宝箱，可以根据需要调整数量
    chest_rect = pygame.Rect(0, 0, 30, 30)  # 宝箱大小调小为30x30
    find_non_colliding_position(chest_rect, obstacle_group1, BG_WIDTH1, BG_HEIGHT1)
    chest = TreasureChest(chest_rect.x, chest_rect.y, chest_rect.width, chest_rect.height, '.\\assets\\tiles\\treasure_chest.png')
    treasure_chest_group.add(chest)

# 生成传送门
portal = Portal(400, 400, 70, 70, '.\\assets\\tiles\\portal.png')  # 传送门大小调大为70x70
find_non_colliding_position(portal.rect, obstacle_group1, BG_WIDTH1, BG_HEIGHT1)

# 生成BOSS
boss = Boss(400, 400, 80, 80, '.\\assets\\npc\\boss.png')  # BOSS大小调大为80x80
find_non_colliding_position(boss.rect, obstacle_group1, BG_WIDTH1, BG_HEIGHT1)

speed = 5

fps = 30
clock = pygame.time.Clock()

camera = Camera(BG_WIDTH1, BG_HEIGHT1)  # 创建相机对象

running = True
current_scene = 1  # 新增变量，用于跟踪当前场景
show_dialog = False
dialog_text = ""
show_hint = True
npc_discovered = False
has_contacted_npc = False
detection_distance = 100

yes_option = pygame.Rect(0, 0, 0, 0)
no_option = pygame.Rect(0, 0, 0, 0)

user_input_box = pygame.Rect(50, 50, screen_width - 100, 50)
user_input_text = ''
user_input_active = False

npc_response_text = ''

# 新增能量值变量
energy = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if show_dialog and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if yes_option.collidepoint(mouse_pos):
                show_dialog = False
                user_input_active = True
            elif no_option.collidepoint(mouse_pos):
                show_dialog = False

        if user_input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                npc_response_text = generate_dialog(user_input_text)
                user_input_text = ''
                user_input_active = False  # 发送消息后关闭输入框
            elif event.key == pygame.K_BACKSPACE:
                user_input_text = user_input_text[:-1]
            else:
                user_input_text += event.unicode

        # 新增空格键退出游戏
        if show_dialog and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = False

        # 新增F11键切换全屏模式
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((screen_width, screen_height))
                # 重新设置相机对象以适应新窗口大小
                if current_scene == 1:
                    camera = Camera(BG_WIDTH1, BG_HEIGHT1)
                elif current_scene == 2:
                    camera = Camera(BG_WIDTH2, BG_HEIGHT2)

    keys = pygame.key.get_pressed()

    # 保存玩家的原始位置
    original_x = player_rect.x
    original_y = player_rect.y

    # 更新玩家位置
    if keys[pygame.K_w]:
        player_rect.y -= speed
    if keys[pygame.K_s]:
        player_rect.y += speed
    if keys[pygame.K_a]:
        player_rect.x -= speed
    if keys[pygame.K_d]:
        player_rect.x += speed

    # 检测玩家是否碰到障碍物
    for obstacle in obstacle_group1:
        if player_rect.colliderect(obstacle.rect):
            player_rect.x = original_x
            player_rect.y = original_y
            break

    # 检测玩家是否接近NPC并在检测距离内
    if current_scene == 1:
        if (pygame.Rect.colliderect(player_rect, monster_rect1) or pygame.Rect.colliderect(player_rect, monster_rect2)
                or (npc_discovered and (
                    distance(player_rect, monster_rect1) < detection_distance
                    or distance(player_rect, monster_rect2) < detection_distance))):
            has_contacted_npc = True
            npc_discovered = True
        else:
            has_contacted_npc = False
            show_dialog = False  # 玩家离NPC足够远时关闭对话框
            show_hint = True
            user_input_active = False  # 玩家离NPC足够远时关闭输入框

    if has_contacted_npc and not user_input_active:
        if not show_dialog:  # 只有当对话框没有显示时才生成对话文本
            show_dialog = True
            dialog_text = generate_dialog(f"Do you want to talk to the NPC?")
        has_contacted_npc = False  # 重置has_contacted_npc，防止对话框一直被刷新

    # 检测传送门碰撞
    if player_rect.colliderect(portal.rect):
        # 切换到另一个地图
        current_scene = 2  # 假设2是另一个地图的标识
        # 重置玩家位置到新地图
        player_rect.topleft = (screen_width // 2, screen_height // 2)
        # 加载新地图
        bg2, bg_rect2 = load_map('.\\assets\\background\\1.png', screen_width * 2, screen_height * 2)
        BG_WIDTH2, BG_HEIGHT2 = bg_rect2.width, bg_rect2.height
        # 重新创建相机对象以适应新地图
        camera = Camera(BG_WIDTH2, BG_HEIGHT2)
        # 重新生成障碍物组（根据需要）
        obstacle_group2 = pygame.sprite.Group()
        for _ in range(10):  # 生成10个障碍物，可以根据需要调整数量
            obstacle_rect = pygame.Rect(0, 0, 50, 50)  # 创建一个临时的rect对象
            find_non_colliding_position(obstacle_rect, obstacle_group2, BG_WIDTH2, BG_HEIGHT2)
            obstacle = Obstacle(obstacle_rect.x, obstacle_rect.y, obstacle_rect.width, obstacle_rect.height, '.\\assets\\tiles\\tree.png')
            obstacle_group2.add(obstacle)
        # 更新音乐（如果需要）
        pygame.mixer.music.load('.\\assets\\bgm\\boss.mp3')  # 替换为你的音乐文件路径
        pygame.mixer.music.play(-1)
        # 重置对话和提示
        show_dialog = False
        dialog_text = ""
        show_hint = True
        npc_discovered = False
        has_contacted_npc = False

    # 更新相机位置
    camera.update(player_rect)

    # 填充窗口背景，防止画面拖影
    screen.fill(white)

    # 根据当前场景绘制背景、玩家和NPC
    if current_scene == 1:
        screen.blit(bg1, camera.apply(pygame.Rect(0, 0, BG_WIDTH1, BG_HEIGHT1)))
        screen.blit(player, camera.apply(player_rect))
        screen.blit(monster1, camera.apply(monster_rect1))
        screen.blit(monster2, camera.apply(monster_rect2))
        # 绘制传送门
        screen.blit(portal.image, camera.apply(portal.rect))
    elif current_scene == 2:
        screen.blit(bg2, camera.apply(pygame.Rect(0, 0, BG_WIDTH2, BG_HEIGHT2)))
        screen.blit(player, camera.apply(player_rect))
        # 绘制BOSS
        screen.blit(boss.image, camera.apply(boss.rect))

    # 绘制障碍物
    if current_scene == 1:
        for obstacle in obstacle_group1:
            screen.blit(obstacle.image, camera.apply(obstacle.rect))
    elif current_scene == 2:
        for obstacle in obstacle_group2:
            screen.blit(obstacle.image, camera.apply(obstacle.rect))

    # 绘制宝箱
    if current_scene == 1:
        for chest in treasure_chest_group:
            screen.blit(chest.image, camera.apply(chest.rect))
            if player_rect.colliderect(chest.rect) and not chest.collected:
                chest.collected = True
                energy += random.randint(1, 2)  # 随机增加1或2点能量值

    # 检测玩家与BOSS碰撞
    if current_scene == 2 and player_rect.colliderect(boss.rect):
        if energy < 7:
            dialog_text = "You lose"
            show_dialog = True
        else:
            dialog_text = "You win"
            show_dialog = True
        yes_option, no_option = draw_dialog_box(screen, dialog_text)
        # 玩家与BOSS碰撞后，无论输赢，游戏不立即退出
        # running = False

    # 如果需要显示对话框，则调用绘制对话框的函数
    if show_dialog:
        yes_option, no_option = draw_dialog_box(screen, dialog_text)
        # 绘制空格键提示信息
        space_text = pygame.font.Font(None, 28).render("Press SPACE to exit", True, black)
        screen.blit(space_text, (screen_width - space_text.get_width() - 10, screen_height - space_text.get_height() - 10))
    elif user_input_active:
        # 绘制输入框
        pygame.draw.rect(screen, grey if user_input_active else black, user_input_box, 2)
        text_surface = pygame.font.Font(None, 36).render(user_input_text, True, black)
        screen.blit(text_surface, (user_input_box.x + 10, user_input_box.y + 10))

        # 绘制NPC回复框
        draw_interaction_box(screen, "You: " + user_input_text, "NPC: " + npc_response_text)

    # 绘制能量值
    energy_text = pygame.font.Font(None, 36).render(f"Energy: {energy}", True, black)
    screen.blit(energy_text, (screen_width - energy_text.get_width() - 10, 10))

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
sys.exit()
