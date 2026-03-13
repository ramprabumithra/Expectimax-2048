import sys
import pygame
from game_engine import *
from ai_player import *
# THIS IS THE UI, USES PYGAME TO RENDER AND HANDLE INPUT.
tile = 95
pad = 10
fps = 60
# Colour scheme replicates original game using hax codes, customisable.
bg = "#FDFBF2"
board_color = "#B3A393"
empty = "#EEE2CE"
text_dark = "#120C00"
text_light = "#FAF9F9"
btn_color = "#F65E3D"
tiles = {
2:"#EEE4DA",4:"#EEE2CE",8:"#F3AD72",16:"#F8976A",
32:"#F7836D",64:"#F76147",128:"#ECCD72",256:"#ECCB60",
512:"#EAC84A",1024:"#ECC441",2048:"#EBC12D"
}

def hx(c):
    return pygame.Color(c)

size_px = pad + size*(tile+pad)
header = tile + pad*4
window_w = size_px + pad*2
window_h = header + size_px + pad

def draw(screen, board, score, best, fonts):
    title, small, tile_font, btn_font = fonts
    screen.fill(hx(bg))
    title_rect = pygame.Rect(pad,pad,tile,tile)
    pygame.draw.rect(screen,hx("#edc22e"),title_rect)
    t = title.render("2048",True,hx(text_light))
    screen.blit(t,t.get_rect(center=title_rect.center))
    box_w = tile
    box_h = pad*4
    score_box = pygame.Rect(window_w-pad-box_w,pad,box_w,box_h)
    best_box = pygame.Rect(window_w-pad-box_w*2-pad,pad,box_w,box_h)
    pygame.draw.rect(screen,hx(text_dark),score_box)
    pygame.draw.rect(screen,hx(text_dark),best_box)
    score_label = small.render("SCORE",True,hx(text_light))
    score_val = small.render(str(score),True,hx(text_light))
    screen.blit(score_label, score_label.get_rect(center=(score_box.centerx, score_box.y+10)))
    screen.blit(score_val, score_val.get_rect(center=(score_box.centerx, score_box.y+28)))
    best_label = small.render("BEST",True,hx(text_light))
    best_val = small.render(str(best),True,hx(text_light))
    screen.blit(best_label, best_label.get_rect(center=(best_box.centerx, best_box.y+10)))
    screen.blit(best_val, best_val.get_rect(center=(best_box.centerx, best_box.y+28)))
    btn_w = box_w
    btn_h = pad*4
    new_btn = pygame.Rect(best_box.x,score_box.bottom+pad,btn_w,btn_h)
    undo_btn = pygame.Rect(score_box.x,score_box.bottom+pad,btn_w,btn_h)
    pygame.draw.rect(screen,hx(btn_color),new_btn)
    pygame.draw.rect(screen,hx(btn_color),undo_btn)
    screen.blit(btn_font.render("NEW",True,hx(text_light)),btn_font.render("NEW",True,hx(text_light)).get_rect(center=new_btn.center))
    screen.blit(btn_font.render("UNDO",True,hx(text_light)),btn_font.render("UNDO",True,hx(text_light)).get_rect(center=undo_btn.center))
    text = small.render("Join the numbers and get to the 2048 tile!",True,hx(text_dark))
    screen.blit(text, text.get_rect(center=(window_w//2, title_rect.bottom+pad*0.5+10)))
    board_x = (window_w - size_px)//2
    board_rect = pygame.Rect(board_x,header,size_px,size_px)
    pygame.draw.rect(screen,hx(board_color),board_rect)
    # Rendering the board and tiles.
    for row in range(size):
        for col in range(size):
            x = board_x + pad + col*(tile+pad)
            y = header + pad + row*(tile+pad)
            rect = pygame.Rect(x,y,tile,tile)
            val = board[row][col]
            pygame.draw.rect(screen,hx(empty),rect)
            if val:
                shadow = rect.move(2,2)
                pygame.draw.rect(screen,hx("#999999"),shadow)
                pygame.draw.rect(screen,hx(tiles.get(val,"#3c3a32")),rect)
                txt = tile_font.render(str(val),True,hx(text_dark if val<8 else text_light))
                screen.blit(txt,txt.get_rect(center=rect.center))
    return new_btn, undo_btn

def main():
    pygame.init()
    screen = pygame.display.set_mode((window_w,window_h))
    pygame.display.set_caption("2048")
    clock = pygame.time.Clock()
    font_path = "ClearSans-Bold.ttf"
    title = pygame.font.Font(font_path,35)
    small = pygame.font.Font(font_path,18)
    tile_font = pygame.font.Font(font_path,36)
    btn_font = pygame.font.Font(font_path,20)
    fonts = (title,small,tile_font,btn_font)
    board = new_board()
    board = rand_tile_val(board)
    board = rand_tile_val(board)
    score = 0
    best = 0
    # Storing the best score in text file.
    best_path = "best_2048.txt"
    try:
        with open(best_path, "r") as f:
            best = int(f.read().strip() or 0)
    except Exception:
        best = 0
    undo = []
    cfg = conf2048()
    ai = False
    running = True
    while running:
        # Handles buttons, user inputs and AI.
        clock.tick(fps)
        new_btn, undo_btn = draw(screen,board,score,best,fonts)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if new_btn.collidepoint(e.pos):
                    board = new_board()
                    board = rand_tile_val(board)
                    board = rand_tile_val(board)
                    score = 0
                    undo = []
                if undo_btn.collidepoint(e.pos) and undo:
                    board,score = undo.pop()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                if e.key == pygame.K_r:
                    board = new_board()
                    board = rand_tile_val(board)
                    board = rand_tile_val(board)
                    score = 0
                    undo = []
                if e.key == pygame.K_u and undo:
                    board,score = undo.pop()
                if e.key == pygame.K_a:
                    ai = not ai
                move = None
                if e.key == pygame.K_LEFT: move="L"
                if e.key == pygame.K_RIGHT: move="R"
                if e.key == pygame.K_UP: move="U"
                if e.key == pygame.K_DOWN: move="D"
                if move:
                    nb,gain,changed = apply_move(board,move)
                    if changed:
                        undo.append(([r[:] for r in board],score))
                        board = nb
                        score += gain
                        old_best = best
                        best = max(best, score)
                        if best != old_best:
                            try:
                                with open(best_path, "w") as f:
                                    f.write(str(best))
                            except Exception:
                                pass
                        board = rand_tile_val(board)
        if ai and can_move(board):
            m = best_move(board,cfg)
            if m:
                nb,gain,changed = apply_move(board,m)
                if changed:
                    undo.append(([r[:] for r in board],score))
                    board = nb
                    score += gain
                    old_best = best
                    best = max(best, score)
                    if best != old_best:
                        try:
                            with open(best_path, "w") as f:
                                f.write(str(best))
                        except Exception:
                            pass
                    board = rand_tile_val(board)
        if not can_move(board):
            overlay = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            over_font = pygame.font.Font(font_path, 80)
            over = over_font.render("GAME OVER", True, (255, 255, 255))
            over_rect = over.get_rect(center=(window_w // 2, window_h // 2))
            screen.blit(over, over_rect)
        pygame.display.flip()

    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()