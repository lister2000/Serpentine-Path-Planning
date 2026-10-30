import pygame
import math
import random
import sys

pygame.init()

# =====================================================
# 配置
# =====================================================

MIN_W = 900
MIN_H = 650

screen = pygame.display.set_mode(
    (1100, 800),
    pygame.RESIZABLE
)

pygame.display.set_caption(
    "Snake Path Optimizer"
)

clock = pygame.time.Clock()

font = pygame.font.Font(None, 24)
font_big = pygame.font.Font(None, 28)

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

    return sum(
        dist(path[i], path[i + 1])
        for i in range(len(path) - 1)
    )


# =====================================================
# 分行
# =====================================================

def split_rows(points, gap_factor=1.5):

    if not points:
        return []

    pts = sorted(points, key=lambda p: p[1])

    ys = [p[1] for p in pts]

    gaps = [
        ys[i + 1] - ys[i]
        for i in range(len(ys) - 1)
    ]

    positive = [
        g for g in gaps
        if g > 1
    ]

    if not positive:
        return [pts]

    med = sorted(positive)[
        len(positive) // 2
    ]

    threshold = max(
        med * gap_factor,
        5
    )

    rows = [[pts[0]]]

    for i in range(1, len(pts)):

        if ys[i] - ys[i - 1] > threshold:
            rows.append([pts[i]])
        else:
            rows[-1].append(pts[i])

    return rows


# =====================================================
# 行方向优化
# =====================================================

def choose_row_direction(rows):

    if not rows:
        return []

    result = []

    first = sorted(
        rows[0],
        key=lambda p: p[0]
    )

    result.extend(first)

    tail = first[-1]

    for row in rows[1:]:

        lr = sorted(row,
                    key=lambda p: p[0])

        rl = lr[::-1]

        d1 = dist(tail, lr[0])
        d2 = dist(tail, rl[0])

        chosen = lr if d1 <= d2 else rl

        result.extend(chosen)

        tail = chosen[-1]

    return result


# =====================================================
# 相交检测
# =====================================================

def seg_intersect(a, b, c, d):

    def ccw(A, B, C):
        return (
            (C[1]-A[1])*(B[0]-A[0])
            >
            (B[1]-A[1])*(C[0]-A[0])
        )

    return (
        ccw(a, c, d)
        !=
        ccw(b, c, d)
        and
        ccw(a, b, c)
        !=
        ccw(a, b, d)
    )


def count_intersections(path):

    cnt = 0

    n = len(path)

    for i in range(n - 1):
        for j in range(i + 2, n - 1):

            if seg_intersect(
                path[i],
                path[i+1],
                path[j],
                path[j+1]
            ):
                cnt += 1

    return cnt


# =====================================================
# 2-OPT
# =====================================================

def two_opt(path):

    n = len(path)

    if n < 4:
        return path

    improved = True

    while improved:

        improved = False

        for i in range(n - 3):

            for j in range(i + 2, n - 1):

                old_len = (
                    dist(path[i], path[i+1])
                    +
                    dist(path[j], path[j+1])
                )

                new_len = (
                    dist(path[i], path[j])
                    +
                    dist(path[i+1], path[j+1])
                )

                if new_len < old_len:

                    path[i+1:j+1] = reversed(
                        path[i+1:j+1]
                    )

                    improved = True

    return path


# =====================================================
# 蛇形路径
# =====================================================

def build_snake_path(points):

    rows = split_rows(points)

    path = choose_row_direction(rows)

    before = path_length(path)

    path = two_opt(path)

    after = path_length(path)

    return path, before, after


# =====================================================
# 示例数据
# =====================================================

def make_demo():

    pts = []

    for r in range(6):

        for c in range(8):

            x = (
                120
                + c * 100
                + random.randint(-15, 15)
            )

            y = (
                120
                + r * 90
                + random.randint(-15, 15)
            )

            pts.append((x, y))

    random.shuffle(pts)

    return pts


# =====================================================
# 按钮
# =====================================================

class Button:

    def __init__(self, x, y, w, h, text):

        self.rect = pygame.Rect(
            x, y, w, h
        )

        self.text = text

    def draw(self, screen):

        mp = pygame.mouse.get_pos()

        col = (
            (80, 170, 255)
            if self.rect.collidepoint(mp)
            else
            (50, 120, 210)
        )

        pygame.draw.rect(
            screen,
            col,
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

        txt = font_big.render(
            self.text,
            True,
            (255,255,255)
        )

        screen.blit(
            txt,
            txt.get_rect(
                center=self.rect.center
            )
        )


# =====================================================
# 主程序
# =====================================================

points = []
path = []

before_len = 0
after_len = 0

while True:

    W, H = screen.get_size()

    btn_sort = Button(20, 15, 120, 40, "SORT")
    btn_demo = Button(150, 15, 120, 40, "DEMO")
    btn_rand = Button(280, 15, 120, 40, "RANDOM")
    btn_clear = Button(410, 15, 120, 40, "CLEAR")

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.VIDEORESIZE:

            screen = pygame.display.set_mode(
                (
                    max(MIN_W, event.w),
                    max(MIN_H, event.h)
                ),
                pygame.RESIZABLE
            )

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                if btn_sort.rect.collidepoint(event.pos):

                    path, before_len, after_len = (
                        build_snake_path(points)
                    )

                elif btn_demo.rect.collidepoint(event.pos):

                    points = make_demo()

                    path, before_len, after_len = (
                        build_snake_path(points)
                    )

                elif btn_rand.rect.collidepoint(event.pos):

                    points = [

                        (
                            random.randint(
                                80,
                                W-80
                            ),

                            random.randint(
                                120,
                                H-80
                            )

                        )

                        for _ in range(50)
                    ]

                    path, before_len, after_len = (
                        build_snake_path(points)
                    )

                elif btn_clear.rect.collidepoint(event.pos):

                    points = []
                    path = []

                else:

                    if event.pos[1] > 70:

                        points.append(
                            event.pos
                        )

                        path = []

    screen.fill((32, 32, 32))

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

    btn_sort.draw(screen)
    btn_demo.draw(screen)
    btn_rand.draw(screen)
    btn_clear.draw(screen)

    # 行线
    for row in split_rows(points):

        yy = sum(
            p[1] for p in row
        ) / len(row)

        pygame.draw.line(
            screen,
            (70,70,100),
            (0,yy),
            (W,yy)
        )

    # 路径
    if len(path) > 1:

        pygame.draw.lines(
            screen,
            (255,160,0),
            False,
            path,
            3
        )

    # 点和编号
    for i, p in enumerate(path):

        pygame.draw.circle(
            screen,
            (255,80,80),
            p,
            6
        )

        screen.blit(
            font.render(
                str(i+1),
                True,
                (255,255,255)
            ),
            (
                p[0]+8,
                p[1]-10
            )
        )

    for p in points:

        pygame.draw.circle(
            screen,
            (200,200,200),
            p,
            4
        )

    # 状态栏
    status = (
        f"Points:{len(points)}    "
        f"Before:{before_len:.1f}    "
        f"After:{after_len:.1f}    "
        f"Cross:{count_intersections(path)}"
    )

    screen.blit(
        font.render(
            status,
            True,
            (255,255,100)
        ),
        (560, 25)
    )

    pygame.display.flip()
    clock.tick(60)