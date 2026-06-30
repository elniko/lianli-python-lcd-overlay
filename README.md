# LCD Overlay

Модуль для отображения данных сенсоров (CPU, GPU, RAM, FAN) поверх видео на LCD экране Lian Li 8.8" Universal Screen.

## Структура проекта

```
lcd-overlay/
├── lcd_overlay/           # Основной модуль
│   ├── __init__.py
│   ├── colors.py          # Парсинг цветов и градиентов
│   ├── config.py          # Загрузка/сохранение конфигурации
│   ├── sensors.py        # Сбор данных сенсоров
│   ├── renderer.py       # Отрисовка колец и прогресс-баров
│   ├── overlay.py        # Сборка оверлеев
│   ├── stream.py         # H264 стриминг и отправка на LCD
│   └── configs/
│       └── default.json  # Конфигурация по умолчанию
├── Linx/                  # Библиотека для работы с LCD
│   └── linx.py
└── run_overlay.py        # Точка входа
```

## Установка

1. Убедитесь что установлены зависимости:
```bash
pip3 install pillow psutil pynvml --break-system-packages
```

2. Подключите экран Lian Li 8.8" Universal Screen через USB

## Запуск

```bash
cd /home/nicolas/lcd-overlay
sudo python3 run_overlay.py
```

С кастомным конфигом:
```bash
sudo python3 run_overlay.py -c /path/to/config.json
```

## Конфигурация

Конфиг файл в формате JSON. Расположение по умолчанию: `lcd_overlay/configs/default.json`

### Пример конфига

```json
{
  "video": "/path/to/video.h264",
  "background": "/path/to/background.png",
  "positions": {
    "cpu": 30,
    "gpu": 335,
    "ram_fan": 645
  },
  "colors": {
    "cpu_ring": {
      "background": "#ffffff",
      "border": "#331933",
      "separator": "#000000",
      "fill": "green_red"
    },
    "gpu_ring": {
      "background": "#ffffff",
      "border": "#331933",
      "separator": "#000000",
      "fill": "cyan_magenta"
    },
    "ram_ring": {
      "background": "#ffffff",
      "border": "#331933",
      "separator": "#000000",
      "fill": "cyan_magenta"
    },
    "cpu_temp": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "#000000",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "gpu_temp": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "#000000",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "cpu_clock": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "#000000",
      "style": "solid",
      "fill": "#ff00fe"
    },
    "gpu_clock": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "#000000",
      "style": "solid",
      "fill": "#ff00fe"
    },
    "cpu_fan": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "#000000",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "gpu_fan": {
      "background": "transparent",
      "border": "#ffffff",
      "separator": "#000000",
      "style": "segmented",
      "fill": "cyan_magenta"
    },
    "text": {
      "title": "#ffffff",
      "data": "#ffffff"
    },
    "separator": "#331933"
  }
}
```

### Параметры конфигурации

| Параметр | Тип | Описание |
|----------|-----|---------|
| `video` | string | Путь к H264 файлу. Пустая строка = только оверлей |
| `background` | string | Путь к PNG фону. Пустая строка = прозрачный (с видео) или чёрный (без видео) |

### Positions (позиции оверлеев)

| Параметр | Тип | Описание |
|----------|-----|---------|
| `cpu` | int | Вертикальная позиция CPU монитора (по умолчанию: 30) |
| `gpu` | int | Вертикальная позиция GPU монитора (по умолчанию: 335) |
| `ram_fan` | int | Вертикальная позиция RAM/FAN секции (по умолчанию: 645) |

### Colors (цвета)

#### Ring (кольцевые диаграммы)

Каждая ring секция (`cpu_ring`, `gpu_ring`, `ram_ring`) содержит:
- `background` - цвет фона сегментов (#ffffff)
- `border` - цвет внешней рамки (#331933)
- `separator` - цвет разделительных линий (#000000)
- `fill` - заливка (gradient или solid цвет)

#### Progress bars

Каждый progress bar (`cpu_temp`, `gpu_temp`, `cpu_clock`, `gpu_clock`, `cpu_fan`, `gpu_fan`) содержит:
- `background` - цвет фона за баром (transparent = прозрачный)
- `border` - цвет рамки вокруг бара
- `separator` - цвет промежутка между сегментами
- `style` - `segmented` (с разделителями) или `solid` (сплошной)
- `fill` - заливка (gradient или solid цвет)

### Fill (заливка)

Параметр `fill` унифицирован для всех элементов и принимает:

**Gradient пресеты:**
- `"cyan_magenta"` - cyan → blue → purple → magenta (6 цветов)
- `"green_red"` - зелёный → жёлтый → оранжевый → красный (5 цветов)

**Solid цвет (hex):**
- `"#ff00fe"`
- `"#00ff00"`

**Custom gradient:**
```json
"fill": ["#00c8f8", "#ff00fe", "#00ff00"]
```

### Цветовые форматы

Поддерживаются:
- Hex: `"#ff0000"`, `"#ff0000ff"`
- Имена: `"white"`, `"black"`, `"red"`, `"green"`, `"blue"`, `"cyan"`, `"magenta"`, `"yellow"`, `"orange"`
- Прозрачный: `"transparent"`

## Режимы работы

1. **Video + overlay** - видео играет на фоне, оверлеи поверх
2. **Overlay only** - только оверлеи на чёрном фоне (video: "")

## Сенсоры

### CPU
- Load % - кольцевая диаграмма
- Temperature °C - прогресс-бар
- Clock MHz - прогресс-бар

### GPU (требует NVML)
- Load % - кольцевая диаграмма
- Temperature °C - прогресс-бар
- Clock MHz - прогресс-бар
- Fan RPM - прогресс-бар

### RAM
- Usage % - кольцевая диаграмма

### FAN
- CPU FAN RPM - прогресс-бар
- GPU FAN RPM - прогресс-бар

## Демонстрация

```bash
# Запуск с настройками по умолчанию
sudo python3 run_overlay.py

# Overlay-only режим (без видео)
# В конфиге: "video": ""

# С кастомным конфигом
sudo python3 run_overlay.py -c /path/to/my_config.json
```
