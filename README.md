# Renombrador de PDFs por Lote

Una aplicación con interfaz gráfica que permite renombrar archivos PDF en lote basándose en un archivo Excel. Además, incluye funcionalidad para dividir un único PDF en múltiples archivos si es necesario.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Contribuciones](#contribuciones)

## Descripción

Este proyecto permite automatizar el proceso de renombrado de archivos PDF mediante una interfaz gráfica desarrollada en Tkinter. El renombrado se realiza utilizando datos extraídos de un archivo Excel, lo que permite generar nuevos nombres de forma dinámica y personalizada. Adicionalmente, el proyecto incluye una funcionalidad para dividir un único PDF en múltiples archivos según un número de páginas especificado.

## Características

- **Renombrado en Lote:** Cambia el nombre de múltiples archivos PDF de manera simultánea.
- **Uso de Archivo Excel:** Utiliza los datos de un Excel (.xls o .xlsx) para generar nombres personalizados.
- **Interfaz Gráfica:** GUI amigable con múltiples etapas para facilitar la selección de archivos y opciones.
- **PDF Splitter:** Si se detecta un único archivo PDF, permite dividirlo en partes según el número de páginas.
- **Drag and Drop:** Define el formato del nombre de archivo final mediante una interfaz de arrastrar y soltar.
- **Selector Paginado:** Permite elegir columnas del Excel de manera paginada y organizada.

## Requisitos

- Python 3.7 o superior.
- Las siguientes librerías de Python:
  - [pandas](https://pandas.pydata.org/)
  - [PyPDF2](https://pypi.org/project/PyPDF2/)
  - [natsort](https://pypi.org/project/natsort/)
  - Tkinter (incluido en la mayoría de las distribuciones de Python)

## Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/GDelpo/python_pdf_batch_renamer.git
   cd python_pdf_batch_renamer
   ```

2. (Opcional) Crea un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate  # En Windows
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

   *Si no cuentas con un archivo `requirements.txt`, asegúrate de instalar manualmente las dependencias mencionadas en [Requisitos](#requisitos).*

## Uso

1. Ejecuta la aplicación:

   ```bash
   python gui_batch_renamer.py
   ```

2. Sigue las instrucciones en la interfaz gráfica:
   - Selecciona la carpeta que contiene los archivos PDF.
   - Selecciona el archivo Excel que contiene los datos para renombrar.
   - Escoge las columnas deseadas mediante el selector paginado.
   - Define el formato del nombre final usando la interfaz de arrastrar y soltar.
   - Revisa el resumen y confirma para iniciar el proceso de renombrado.

## Estructura del Proyecto

```
|-- .gitignore
|-- excel_parser.py        # Funciones para leer el Excel y generar nombres formateados.
|-- file_manager.py        # Funciones para gestionar archivos y realizar el renombrado.
|-- gui_batch_renamer.py   # Interfaz principal que orquesta el proceso.
|-- gui_drag_and_drop.py   # Interfaz para definir el formato del nombre mediante drag and drop.
|-- gui_paginated_selection.py  # Selector paginado para elegir columnas del Excel.
|-- pdf_splitter.py        # Función para dividir archivos PDF en caso de necesitarlo.
```

## Contribuciones

Las contribuciones son bienvenidas. Si deseas colaborar, por favor:

1. Haz un fork del repositorio.
2. Crea una rama para tus cambios (`git checkout -b mejora-nueva-funcionalidad`).
3. Realiza tus modificaciones y confirma los cambios.
4. Envía un pull request describiendo los cambios propuestos.
