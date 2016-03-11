# indexes of store
# video
VIDEO_LOSS = 0
BLACK_ERR = 2
BLACK_WARN = 3
LUMA_WARN = 4
BLACK_PIXEL = 5
FREEZE_ERR = 6
FREEZE_WARN = 7
DIFF_WARN = 8
PIXEL_DIFF = 9
BLOCK_ERR = 10
BLOCK_WARN = 11
# audio
AUDIO_LOSS = 1
OVERLOAD_ERR = 12
OVERLOAD_WARN = 13
SILENCE_ERR = 14
SILENCE_WARN = 15


DEFAULT_VALUES = [['Пропадание видео, секунд',
                   'error',   2.0,   0,  3600, 2],
                  ['Пропадание аудио, секунд',
                   'error',   2.0,   0,  3600, 2],
                  ['Количество чёрных пикселей, %',
                   'error',   99.5,  0,  100,  75],
                  ['Количество чёрных пикселей, %',
                  'warning', 95.0,  0,  100,  75],
                  ['Уровень средней яркости',
                   'warning', 20.0,  16,  235,  75],
                  ['Уровень чёрного пиксела',
                   'parameter', 16,  16,  235,  0],
                  ['Количество идентичных пикселей, %',
                   'error',   99.5,  0,  100,  75],
                  ['Количество идентичных пикселей, %',
                   'warning', 95.0,  0,  100,  75],
                  ['Уровень средней разности',
                   'warning', 0.20,  0,  219,  75],
                  ['Допустимая разность между пикселами',
                   'parameter', 0,  0,  100,  0],
                  ['Блочность',
                   'error',   4.00,  0,  10,   5],
                  ['Блочность',
                   'warning', 3.00,  0,  10,   1],
                  ['Уровень громкости, LUFS',
                 'error',   -22.0, -59, -5,  1],
                  ['Уровень громкости, LUFS',
                   'warning', -22.5, -59, -5,  1],
                  ['Уровень громкости, LUFS',
                   'error',   -34.0, -59, -5,  1],
                  ['Уровень громкости, LUFS',
                   'warning', -33.0, -59, -5,  1]]

