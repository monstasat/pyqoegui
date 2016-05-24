# list of available video plots
# parameter name,
# parameter unit,
# parameter range,
# parameter major type,
# parameter measured data index
PLOT_TYPES = (
    ("Доля идентичных пикселей", '%', [0, 100], 'video', 0),
    ("Доля чёрных пикселей", '%', [0, 100], 'video', 1),
    ("Доля заметных блоков", '%', [0, 100], 'video', 2),
    ("Средняя яркость кадра", '', [16, 235], 'video', 3),
    ("Среднее различие между кадрами", '', [0, 219], 'video', 4),
    ("Моментальная громкость", 'LUFS', [-59, -5], 'audio', 0),
    ("Кратковременная громкость", 'LUFS', [-59, -5], 'audio', 1))

