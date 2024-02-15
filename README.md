# Mapa choropleth bivariado

## Description
Ejercicio para generar un mapa choropleth que represente la interacción entre dos variables.

<image style="height:50%; width:50%" src="./resources/mapa-bivariado.png"></image>

## Fuentes
El folder `./data/` contiene un archivo ZIP por descomprimir:
* `enaho01a-2019-300.dta`: microdatos INEI, 2019, módulo 3 (educación).
* `sumaria-2019.dta`: microdatos INEI, 2019, módulo 34 (sumaria).
* `shapefile/`: folder con archivo shapefile de provincias para Perú.

Code snippets: Eduardo Graells-Garrido ([fuente](https://github.com/zorzalerrante/mapas_censo_2017)).

## Ejecución
### Primera parte: Stata
Se requiere ejecutar el archivo `./scripts/main.do` en Stata haciendo el reemplazo correspondiente sobre la variable `cwd` del script. Este genera el archivo fuente para la creación del gráfico mediante Python.

### Segunda parte: Python
Realiza transformaciones básicas sobre el archivo output del paso anterior y exporta el mapa en un archivo JPG.
```bash
pip3 install -r requirements.txt
python ./scripts/main.py
```

La ejecución de scripts ha sido validada a la fecha: February 15th, 2024.
