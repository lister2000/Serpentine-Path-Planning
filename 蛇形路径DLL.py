import pygame
import sys
import random
import clr
import System

# ================= C# DLL 加载 =================
DLL_PATH = r"C:\Users\Administrator\Desktop\Path_Extractor\SnakeSorter.dll"   # 改成你的实际路径
clr.AddReference(DLL_PATH)
from SorterLib  import SnakeSorter


def csharp_tsp_sort(points):
    """调用 C# DLL 排序，返回排序后的点列表。"""
    if not points or len(points) < 2:
        return list(points)
    n = len(points)
    arr = System.Array.CreateInstance(System.Double, n, 2)
    for i, (x, y) in enumerate(points):
        arr[i, 0] = float(x)
        arr[i, 1] = float(y)
    sorted_arr = SnakeSorter.Sort(arr)
    if sorted_arr is None:
        return list(points)
    return [(float(sorted_arr[i, 0]), float(sorted_arr[i, 1])) for i in range(n)]


# ================= pygame 界面 =================
pygame.init()
screen = pygame.display.set_mode((1200, 800), pygame.RESIZABLE)
pygame.display.set_caption("TSP via C# DLL")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)


class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text

    def draw(self, screen):
        mp = pygame.mouse.get_pos()
        col = (90, 180, 255) if self.rect.collidepoint(mp) else (60, 120, 220)
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
        txt = font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


def main():
    global screen
    points = []
    path = []
    err_msg = ""

    btn_run = Button(20, 15, 120, 40, "RUN (DLL)")
    btn_rand = Button(150, 15, 120, 40, "RANDOM")
    btn_clear = Button(280, 15, 120, 40, "CLEAR")

    running = True
    while running:
        W, H = screen.get_size()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (max(900, event.w), max(600, event.h)), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_run.hit(event.pos):
                    try:
                        path = csharp_tsp_sort(points)
                        err_msg = ""
                    except Exception as e:
                        err_msg = f"DLL error: {e}"
                        path = []
                elif btn_rand.hit(event.pos):
                    points = [(random.randint(80, W - 80),
                               random.randint(100, H - 80)) for _ in range(60)]
                    path = []
                elif btn_clear.hit(event.pos):
                    points, path = [], []
                else:
                    if event.pos[1] > 70:
                        points.append(event.pos)
                        path = []

        screen.fill((35, 35, 35))

        for x in range(0, W, 50):
            pygame.draw.line(screen, (50, 50, 50), (x, 0), (x, H))
        for y in range(0, H, 50):
            pygame.draw.line(screen, (50, 50, 50), (0, y), (W, y))

        pygame.draw.rect(screen, (25, 25, 25), (0, 0, W, 70))
        btn_run.draw(screen)
        btn_rand.draw(screen)
        btn_clear.draw(screen)

        if len(path) > 1:
            pygame.draw.lines(screen, (255, 180, 0), False, path, 3)

        for i, p in enumerate(path):
            pygame.draw.circle(screen, (255, 80, 80), (int(p[0]), int(p[1])), 5)
            t = font.render(str(i + 1), True, (255, 255, 255))
            screen.blit(t, (int(p[0]) + 8, int(p[1]) - 8))

        for p in points:
            pygame.draw.circle(screen, (210, 210, 210), p, 4)

        info = f"Points: {len(points)}"
        screen.blit(font.render(info, True, (255, 255, 100)), (420, 25))
        if err_msg:
            screen.blit(font.render(err_msg, True, (255, 80, 80)), (20, H - 30))
        else:
            help_t = "Click: add | RUN(DLL): sort via C# | RANDOM | CLEAR"
            screen.blit(font.render(help_t, True, (200, 200, 200)), (20, H - 30))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()