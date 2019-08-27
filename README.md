# MK90

Для разработки я использовал связку из кросс-ассемблера [macro-11](http://retrocmp.com/tools/macro-11-on-windows), [линкера](https://github.com/AK6DN/obj2bin), текстового редактора [Sublime](https://www.sublimetext.com/) и [эмулятора](http://www.pisi.com.pl/piotr433/mk90emue.htm)

## [T.Rex](https://github.com/azya52/MK90/blob/master/trex/)
[![Video](https://img.youtube.com/vi/ivxIEHNXE9s/0.jpg)](https://www.youtube.com/watch?v=ivxIEHNXE9s)

**[Образ СМП](https://github.com/azya52/MK90/blob/master/TRex/smp0.bin)**, для запуска на эмуляторе может потребоваться увеличить скорость эмуляции (параметр CpuSpeed).

**[Исходный код](https://github.com/azya52/MK90/blob/master/TRex/trex.mac)**, на ассемблере MACRO-11

## [Веселая Птичка](https://github.com/azya52/MK90/tree/master/funnybird)
[![Video](https://www.youtube.com/watch?v=GlUCAnwnc_E/0.jpg)](https://www.youtube.com/watch?v=GlUCAnwnc_E)

**[Образ СМП](https://github.com/azya52/MK90/tree/master/funnybird/smp0.bin)**, на эмуляторе не будет работать должным образом. Для нормального контраста, батарейки/аккумуляторы не должны быть сильно разряженными.

**[Исходный код](https://github.com/azya52/MK90/tree/master/funnybird/fb.mac)**, на ассемблере MACRO-11

## [Grayscale](https://github.com/azya52/MK90/blob/master/grayscale/)

<img src="/grayscale/space_ex.jpg?raw=true">

<img src="/grayscale/ex.jpg?raw=true">

Эксперимент с выводом изображений в оттенках серого. Без видимого мерцания получается отображать до 6 оттенков включая белый, на 7 уже появляется немного заметное мерцание. Корректно работает только на реальном устройстве.

**[img2smp](https://github.com/azya52/MK90/blob/master/grayscale/img2smp.py)**, Python скрипт для конвертации индексированного png (120x64 до 10 оттенков) сразу в образ смп.

**[img2mac](https://github.com/azya52/MK90/blob/master/grayscale/img2mac.py)**, то же, но выдает исходный код готовый для вставки в grayscaleIO.mac.

**[grayscaleIO.mac](https://github.com/azya52/MK90/blob/master/grayscale/grayscaleIO.mac)**, код просмотрщика.

**[space6c.bin](https://github.com/azya52/MK90/blob/master/grayscale/space6c.mac), [lena6c.bin](https://github.com/azya52/MK90/blob/master/grayscale/lena6c.mac)**, готовые смп-образы с примерами.
