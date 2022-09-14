# video2mk
Конвертер видео (конечно без звука) в образ для запуска на МК-90

[![Video](https://img.youtube.com/vi/Swxv3FU7puw/0.jpg)](https://www.youtube.com/watch?v=Swxv3FU7puw)

Использование:
```
usage: video2mk.py [-h] [-s S] [-e E] [-fps FPS] [-he] [-ahe [AHE [AHE ...]]]
                   [-ar {KEEP,FIT}] [-c CROP [CROP ...]] [-mac]
                   [-i {NEAREST,LINEAR,AREA,CUBIC,LANCZOS4}]
                   [-t {BINARY,OTSU,TRIANGLE,MEAN,GAUSSIAN,DITHER}]
                   [-to TRESH_OPT [TRESH_OPT ...]]
                   path_in path_out

positional arguments:
  path_in               path to source video
  path_out              path to result files (.bin or/and .mac)

optional arguments:
  -h, --help            show this help message and exit
  -s S                  first frame number
  -e E                  last frame number
  -fps FPS              change fps, 0 - save original
  -he                   histogram equalization
  -ahe [AHE [AHE ...]]  adaptive histogram equalization (clipLimit (1.0),
                        tileGridWidth (8), tileGridHeight (8)
  -ar {KEEP,FIT}        aspect ratio, keep original or fit to screen (default)
  -c CROP [CROP ...]    cropping the original frame in pixels (top, bottom,
                        left, righ)
  -mac                  provide the result as source code
  -i {NEAREST,LINEAR,AREA,CUBIC,LANCZOS4}
                        interpolation method for frame scaling
  -t {BINARY,OTSU,TRIANGLE,MEAN,GAUSSIAN,DITHER}
                        type of converting a grayscale image to binary
  -to TRESH_OPT [TRESH_OPT ...]
                        options for the selected converting type: for BINARY -
                        just threshold (0 - 255), default - 127; for MEAN or
                        GAUSSIAN - block size (3, 5, 7 ...) and constant
                        subtracted from the mean (integer) default - 21 5; for
                        DITHER - error divisor (positive) default - 32
```
Для примера, в приведенном выше видео, первый ролик был сконвертирован со следующими параметрами:
```
video2mk.py <source video> <result bin> -c 0 40 -s 11550 -e 12031 -t DITHER -to 48 -ahe 4 9 9
```

- ```<source video>``` - путь к исходному видео;
- ```<result bin>``` - путь для сохранения результата;
- ```-c 0 40``` - обрезать исходное видео снизу на 40 пикселей;
- ```-s 11550 -e 12031``` - начальный и конечный кадр отрывка для конвертации;
- ```-t DITHER -to 48``` - использовать дизеринг для формирования бинарного изображения, параметр -to определяет степень дизеринга (чем он больше, тем меньше "растекаемость" подмешиваемых пикселей);
- ```-ahe 4 9 9``` - использовать адаптивное выравнивание гистограммы с порогом ограничения контраста 4 и размером сетки 9x9 пикселей.

Результат можно смотреть на [эмуляторе](http://old-dos.ru/index.php?page=files&mode=files&do=show&id=8158) Piotr Piatek или на реальном железе, используя [PIMP](https://github.com/azya52/PIMP). Ролики меньше 10кБ теоретически можно запустить с оригинального СМП-10 (хотя, я не проверял).
