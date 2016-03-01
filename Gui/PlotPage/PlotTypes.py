# list of available video plots
# parameter name,
# parameter unit,
# parameter range,
# parameter major type,
# parameter measured data index
PLOT_TYPES = (
    ("Количество идентичных пикселей", '%%', [0, 100], 'video', 0),
    ("Количество чёрных пикселей", '%%', [0, 100], 'video', 1),
    ("Уровень блочности", '', [0, 10], 'video', 2),
    ("Средняя яркость кадра", '', [0, 255], 'video', 3),
    ("Среднее различие между кадрами", '', [0, 255], 'video', 4),
    ("Моментальная громкость", 'LUFS', [-40, -14], 'audio', 0),
    ("Кратковременная громкость", 'LUFS', [-40, -14], 'audio', 1))
