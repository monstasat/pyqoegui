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

DEFAULT_VALUES1 = {'vloss': 2, 'aloss': 2,
                   'black_cont_en': True, 'black_cont': 90,
                   'black_peak_en': True, 'black_peak': 100,
                   'luma_cont_en': True, 'luma_cont': 20,
                   'luma_peak_en': True, 'luma_peak': 17,
                   'black_time': 2, 'black_pixel': 16,
                   'freeze_cont_en': True, 'freeze_cont': 90,
                   'freeze_peak_en': True, 'freeze_peak': 100,
                   'diff_cont_en': True, 'diff_cont': 0.1,
                   'diff_peak_en': True, 'diff_peak': 0.02,
                   'freeze_time': 2, 'pixel_diff': 0,
                   'blocky_cont_en': True, 'blocky_cont': 3,
                   'blocky_peak_en': True, 'blocky_peak': 6,
                   'blocky_time': 1,
                   'silence_cont_en': True, 'silence_cont': -35,
                   'silence_peak_en': True, 'silence_peak': -45,
                   'silence_time': 10,
                   'loudness_cont_en': True, 'loudness_cont': -21.9,
                   'loudness_peak_en': True, 'loudness_peak': -15,
                   'loudness_time': 2}

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

