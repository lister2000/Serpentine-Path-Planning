import pygame
import random
import math
import sys

pygame.init()

# =====================================================
# 窗口
# =====================================================

screen = pygame.display.set_mode(
    (1200, 800),
    pygame.RESIZABLE
)

pygame.display.set_caption(
    "TSP Path Optimizer"
)

clock = pygame.time.Clock()

font = pygame.font.Font(None, 24)

# =====================================================
# 工具函数
# =====================================================

def dist(a, b):
    return math.hypot(
        a[0] - b[0],
        a[1] - b[1]
    )


def path_length(path):

    if len(path) < 2:
        return 0

    total = 0

    for i in range(len(path)-1):

        total += dist(
            path[i],
            path[i+1]
        )

    return total


# =====================================================
# 最近邻构建初始路径
# =====================================================

def nearest_neighbor(points):

    if not points:
        return []

    unused = points[:]

    path = [unused.pop(0)]

    while unused:

        current = path[-1]

        next_pt = min(
            unused,
            key=lambda p:
            dist(current, p)
        )

        path.append(next_pt)

        unused.remove(next_pt)

    return path


# =====================================================
# 2opt优化
# =====================================================

def two_opt(path):

    n = len(path)

    if n < 4:
        return path

    improved = True

    while improved:

        improved = False

        for i in range(n-3):

            for j in range(i+2, n-1):

                old_dist = (
                    dist(path[i], path[i+1])
                    +
                    dist(path[j], path[j+1])
                )

                new_dist = (
                    dist(path[i], path[j])
                    +
                    dist(path[i+1], path[j+1])
                )

                if new_dist < old_dist:

                    path[i+1:j+1] = reversed(
                        path[i+1:j+1]
                    )

                    improved = True

    return path


# =====================================================
# TSP求解
# =====================================================

def solve_tsp(points):

    if len(points) < 2:
        return []

    path = nearest_neighbor(points)

    before = path_length(path)

    path = two_opt(path)

    after = path_length(path)

    return path, before, after


# =====================================================
# 随机数据
# =====================================================

def random_points(n, W, H):

    pts = []

    for _ in range(n):

        pts.append(
            (
                random.randint(
                    80,
                    W-80
                ),

                random.randint(
                    100,
                    H-80
                )
            )
        )

    return pts


# =====================================================
# 按钮
# =====================================================

class Button:

    def __init__(
        self,
        x,
        y,
        w,
        h,
        text
    ):

        self.rect = pygame.Rect(
            x, y, w, h
        )

        self.text = text

    def draw(self, screen):

        mp = pygame.mouse.get_pos()

        color = (
            (90,180,255)
            if self.rect.collidepoint(mp)
            else
            (60,120,220)
        )

        pygame.draw.rect(
            screen,
            color,
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            screen,
            (255,255,255),
            self.rect,
            2,
            border_radius=8
        )

        txt = font.render(
            self.text,
            True,
            (255,255,255)
        )

        screen.blit(
            txt,
            txt.get_rect(
                center=
                self.rect.center
            )
        )


# =====================================================
# 主循环
# =====================================================

points = []

path = []

before_len = 0
after_len = 0

while True:

    W, H = screen.get_size()

    btn_solve = Button(
        20, 15, 120, 40, "SOLVE"
    )

    btn_random = Button(
        150, 15, 140, 40, "RANDOM"
    )

    btn_clear = Button(
        300, 15, 120, 40, "CLEAR"
    )

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:

            screen = pygame.display.set_mode(
                (
                    max(900, event.w),
                    max(600, event.h)
                ),
                pygame.RESIZABLE
            )

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if btn_solve.rect.collidepoint(
                        event.pos):

                    result = solve_tsp(
                        points
                    )

                    if result:

                        (
                            path,
                            before_len,
                            after_len
                        ) = result

                elif btn_random.rect.collidepoint(
                        event.pos):

                    points = random_points(
                        60,
                        W,
                        H
                    )

                    (
                        path,
                        before_len,
                        after_len
                    ) = solve_tsp(points)

                elif btn_clear.rect.collidepoint(
                        event.pos):

                    points = []
                    path = []

                else:

                    if event.pos[1] > 70:

                        points.append(
                            event.pos
                        )

                        path = []

    screen.fill((35,35,35))

    # 网格
    for x in range(0, W, 50):

        pygame.draw.line(
            screen,
            (50,50,50),
            (x,0),
            (x,H)
        )

    for y in range(0, H, 50):

        pygame.draw.line(
            screen,
            (50,50,50),
            (0,y),
            (W,y)
        )

    # 顶部工具栏
    pygame.draw.rect(
        screen,
        (25,25,25),
        (0,0,W,70)
    )

    btn_solve.draw(screen)
    btn_random.draw(screen)
    btn_clear.draw(screen)

    # 路径
    if len(path) > 1:

        pygame.draw.lines(
            screen,
            (255,180,0),
            False,
            path,
            3
        )

    # 点
    for i, p in enumerate(path):

        pygame.draw.circle(
            screen,
            (255,80,80),
            p,
            5
        )

        t = font.render(
            str(i+1),
            True,
            (255,255,255)
        )

        screen.blit(
            t,
            (
                p[0]+8,
                p[1]-8
            )
        )

    for p in points:

        pygame.draw.circle(
            screen,
            (210,210,210),
            p,
            4
        )

    txt = (
        f"Points:{len(points)}   "
        f"Initial:{before_len:.1f}   "
        f"Optimized:{after_len:.1f}"
    )

    screen.blit(
        font.render(
            txt,
            True,
            (255,255,100)
        ),
        (460,25)
    )

    help_text = (
        "Left Click:Add Point   "
        "SOLVE:TSP   "
        "RANDOM:60 Points"
    )

    screen.blit(
        font.render(
            help_text,
            True,
            (200,200,200)
        ),
        (20,H-30)
    )

    pygame.display.flip()

    clock.tick(60)