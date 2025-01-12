import pygame
import sys
import subprocess  # 添加subprocess模块以运行外部文件

# 初始化Pygame和混音器
pygame.init()
pygame.mixer.init()

# 设置屏幕尺寸
width, height = 800, 600
screen_info = pygame.display.Info()
width, height = screen_info.current_w, screen_info.current_h
win = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
pygame.display.set_caption('菜单界面')

# 定义颜色
white = (255, 255, 255)
black = (0, 0, 0)

# 设置字体
try:
    font = pygame.font.Font(None, 36)
except Exception as e:
    print(f"无法加载字体: {e}")
    font = pygame.font.SysFont(None, 36)  # 使用系统默认字体

# 加载背景图片
try:
    menu_background = pygame.image.load('.\\assets\\background\\menu.png').convert()
except pygame.error as e:
    print(f"无法加载背景图片: {e}")
    # 设置一个默认背景色，防止程序崩溃
    menu_background = pygame.Surface((width, height))
    menu_background.fill(black)

# 调整背景图片尺寸以适应屏幕
menu_background = pygame.transform.scale(menu_background, (width, height))

# 加载背景音乐
try:
    pygame.mixer.music.load('.\\assets\\bgm\\wild.mp3')
except pygame.error as e:
    print(f"无法加载背景音乐: {e}")

# 开始播放背景音乐，-1表示循环播放
try:
    pygame.mixer.music.play(-1)
except Exception as e:
    print(f"无法播放背景音乐: {e}")

# 游戏主循环标志
running = True
menu_active = True

def draw_menu():
    win.blit(menu_background, (0, 0))  # 使用背景图片填充屏幕
    # 绘制菜单标题
    title = font.render('welcome to my game!', True, white)
    win.blit(title, (width // 2 - title.get_width() // 2, height // 2 - title.get_height() // 2 - 50))
    # 绘制提示信息
    instructions = font.render('press enter to start the game', True, white)
    win.blit(instructions, (width // 2 - instructions.get_width() // 2, height // 2 + 20))

def run_game():
    # 停止背景音乐
    pygame.mixer.music.stop()
    # 使用subprocess模块运行game.py文件
    subprocess.run(['python', 'game.py'])
    # 游戏结束后返回菜单
    global menu_active
    menu_active = True
    pygame.mixer.music.play(-1)  # 重新播放背景音乐

# 游戏主循环
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if menu_active and event.key == pygame.K_RETURN:
                run_game()  # 调用run_game函数运行game.py

    if menu_active:
        draw_menu()

    pygame.display.flip()

# 退出Pygame
pygame.quit()
sys.exit()
