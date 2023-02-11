class Setting(object):
    GameName = 'Riichi Mahjong Game'
    WinW = 1280
    WinH = 800
    win_w_h_half = (WinW - WinH) // 2 + 50
    FPS = 5

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
    hugeFontSize = 40

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


