import time


class Setting(object):
    GameName = 'Riichi Mahjong Game'
    WinW = 1280
    WinH = 800
    win_w_h_half = (WinW - WinH) // 2 + 50
    FPS = 30
    cmd_FPS = 60

    gameCircles = 2
    gameStartScore = 25000
    gameOpposites =['bot1', 'bot2', 'bot3']
    gamePlayer = 'lyf'

    bgImg = './resource/image/background.png'
    tileImgPath = './resource/image/tile/'
    facedownImg = 'face-down.png'

    font = './resource/Fonts/simhei.ttf'
    smallFontSize = 15
    normalFontSize = 20
    bigFontSize = 30
    hugeFontSize = 50

    # hand name
    handNameLeft = 98
    handNameTop = 3
    nickRightTop = 50

    dealerWind = 30
    playerScore = 40

    # distance and length
    concealed_left = 50
    concealed_bottom = 30
    concealedBottom = 50

    discarded_left = 50
    discarded_bottom = 170
    discarded_step = 30
    discarded_line_limit = 6

    exposed_left = 50
    exposed_bottom = 110

    info = 150
    current_jump = 10

    sprite_base = './resource/sprite/'
    waiting_img = {
        'chow': 'chow.png',
        'pong': 'pong.png',
        'kong': 'kong.png',
        'listen': 'listen.png',
        'cancel': 'cancel.png',
        'hu': 'hu.png',
        'ignore': 'ignore.png',
        'riichi': 'listen.png'
    }

    btn_img = {
        'start': 'btn_start.png',
        'end': 'btn_end.png',
    }
    waiting_img_span = 10

    bonus_text_left = 80
    bonus_text_bottom = 220
    bonus_text_img_span = 10

    score_board_left = 300
    score_board_bottom = 300
    score_board_player_x_span = 100

    score_board_concealed_left = 300
    score_board_concealed_bottom = 100

    score_board_exposed_left = 300
    score_board_exposed_bottom = 200
    score_board_exposed_x_span = 42

    score_board_score_y_span = 50
    score_board_score_x_span = 150
    score_board_score_width = 250

    score_bonus_text_left = 1000
    score_bonus_text_bottom = 100
    score_libonus_text_bottom = 200

    score_fushu_bottom = 400

    save_file_path = '/resource/savings'
    save_file_name = './resource/savings/' + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())

    saving_start_h = 90
    saving_h_span = 60