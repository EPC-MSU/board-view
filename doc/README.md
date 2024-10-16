# boardview

## Описание модуля

* **doc** - папка с описанием модуля.
* **boardview** - папка с модулем.
    * **boardview.py** - файл с основным виджетом **BoardView** для рисования платы.
    * **descriptionitem.py** - файл с классом **DescriptionItem** для отрисовки названия или идеального рисунка элементы платы.
    * **elementitem.py** - файл с классом **ElementItem** для элемента платы.
    * **viewmode.py** - файл с перечислением режимов **ViewMode**, в которых может находиться сцена.
* **examples** - папка с примерами.
* **tests** - тесты.

## Классы

В **boardview** есть следующие классы:

- **BoardView** - класс виджета для рисования платы;
- **ElementItem** - класс для элемента платы;
- **DescriptionItem** - класс для отрисовки названия или идеального рисунка элемента платы.

#### Класс **ElementItem**

В классе **ElementItem** используются:

- **RectComponent** из модуля **PyQtExtendedScene** для отрисовки границ элемента;
- **PointComponent** из модуля **PyQtExtendedScene** для отрисовки пинов элемента;
- **DescriptionItem**.

У элементов **ElementItem** можно включить/выключить отрисовку названия элемента с помощью метода:

```python
element_item.show_element_description(True/False)
```

Если для элемента имеется svg изображение, то его можно добавить с помощью метода:

```python
element_item.set_element_description(svg_file, rotation)
```

- **svg_file** - путь до svg изображения;
- **rotation** - сколько раз нужно повернуть изображение против часовой стрелки на 90°.

## Режимы

Виджет **BoardView** может находиться в одном из режимов:

* **NORMAL** - обычный режим;
* **EDIT** - режим редактирования.
