# Polygon to Cats
Скрипт для конвертации пакета из [Polygon](https://polygon.codeforces.com/) в формат [CATS](https://imcs.dvfu.ru/cats/).

![GitHub top language](https://img.shields.io/github/languages/top/Baderik/Polygon2Cats)
![GitHub](https://img.shields.io/github/license/Baderik/Polygon2Cats)

## Установка и запуск
У вас должен быть установлен Python 3.8 или выше.

1. Клонирование репозитория 

```git clone https://github.com/Baderik/Polygon2Cats.git```

2. Запуск скрипта

  ```python3 Polygon2Cats/main.py```

3. После запуска проверить *.xml* файл.

## Документация
* Передача исходного пакета:
  1. Как аргумент скрипта
    
  ```python3 main.py PACKAGE_PATH```

  2. Как входные ответ на запрос программы
  
    ```
    python3 main.py
    >> Please, Enter path to polygon package dir or zip
    >> PACKAGE_PATH
    ```
  * ```PACKAGE_PATH``` путь либо до директории с распакованным пакетом, либо до *.zip* файла с этим пакетом.
  * ```PACKAGE_PATH``` ищется в *config/search_dirs*. По стандарту:
  1. Абсолютный путь
  2. Локальный путь относительно python.exe.
  3. Локальный путь относительно *Polygon2Cats* директории.
  4. Локальный путь относительно *Polygon2Cats/polygon*.

* Изменить в *config.py* можно:
  * Path до сохранения, разархивирования, поиска файлов и директорий.
  * Название *.xml* файла в итоговом пакете.
  * Уровень Логирования.