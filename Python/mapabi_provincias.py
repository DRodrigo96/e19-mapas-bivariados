
# Author: David Sánchez

# %% REQUIREMENTS
import numpy as np
import pandas as pd
import geopandas as gpd
import spectra
import mapclassify
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import seaborn as sns

# %% DATOS CASOS DE ANEMIA POR DISTRITO
dfProvincial = pd.read_csv('data/BdDProvincial.csv', delimiter=';', header=0)
dfProvincial.rename(columns={'prov': 'UBIGEO'}, inplace=True)
dfProvincial['UBIGEO'] = dfProvincial['UBIGEO'].astype(str)

# Replace UBIGEO-PROVINCIAS
from usr_functions import replace_ubi_rl
dfProvincial['UBIGEO'] = dfProvincial.apply(replace_ubi_rl, col='UBIGEO', axis=1)
dfProvincial.set_index('UBIGEO', inplace=True)

# %% INFORMACION PARA MAPA-SHAPEFILE
stgo = gpd.read_file('data/shapefile/PROVINCIAS.shp')
stgo.rename({'IDPROV': 'UBIGEO'}, axis='columns', inplace=True)

# Replace UBIGEO-SHAPEFILE
from usr_functions import replace_ubi_rr
stgo['UBIGEO'] = stgo.apply(replace_ubi_rr, col='UBIGEO', axis=1)
stgo.set_index('UBIGEO', inplace=True)

# %% DATAFRAMES JOIN
dfGeoref = stgo.join(dfProvincial)

# Se asumirá valor promedio de a_edu y ingM_fampc de la región 16 en missing.
mean_aedu_dep16 = dfGeoref[dfGeoref['IDDPTO'] == '16']['a_edu'].mean()
mean_ingM_dep16 = dfGeoref[dfGeoref['IDDPTO'] == '16']['ingM_fampc'].mean()

dfGeoref.fillna(
    {'a_edu': mean_aedu_dep16, 'ingM_fampc': mean_ingM_dep16}, 
    inplace=True
    )

# %% PALETA DE COLORES
colors = [
     '#be64ac',  
     '#dfb0d6', 
     '#e8e8e8', 
     '#ace4e4',  
     '#5ac8c8'
]

n_categories = 3
full_palette = sns.color_palette(colors, n_colors=(n_categories-1)*2 + 1)

# Paleta primera
cmap_x = full_palette[n_categories-1:]
# Paleta segunda
cmap_y = list(reversed(full_palette))[n_categories-1:]

# %% INTERVALOS
# Años de educación
# Intervalos por algoritmo Fisher-Jenks
edu_bin = mapclassify.FisherJenks(dfGeoref['a_edu'], k=n_categories)

# Ingreso familiar per cápita
# Intervalos
ingM_bin = mapclassify.FisherJenks(dfGeoref['ingM_fampc'], k=n_categories)

# %% COMBINACIÓN DE PALETAS DE COLORES
cmap_xy = []
bivariate_palette = {}

for j in range(n_categories):
    for i in range(n_categories):

        x = spectra.rgb(*cmap_x[i][0:3])
        y = spectra.rgb(*cmap_y[j][0:3])

        if i == j and i == 0:
            cmap_xy.append(x.darken(1.5).rgb)
        elif i == 0:
            cmap_xy.append(y.rgb)
        elif j == 0:
            cmap_xy.append(x.rgb)
        else: 
            blended = x.blend(y, ratio=0.5)
            if i == j:
                blended = blended.saturate(7.5*(i+1))
            else:
                blended = blended.saturate(4.5*(i+1))
            cmap_xy.append(blended.rgb)
        
        bivariate_palette[(i, j)] = rgb2hex(cmap_xy[-1])

cmap_xy = np.array(cmap_xy).reshape(n_categories, n_categories, 3)

# %% MAPAS CHOROPLETH BIVARIADO
# Mapa
fig, ax = plt.subplots(1, 1, figsize=(12, 12))

for i in range(n_categories):
    for j in range(n_categories):
        areas_in_this_category = set(np.where(edu_bin.yb == i)[0]) & set(np.where(ingM_bin.yb == j)[0])
        dfGeoref.iloc[list(areas_in_this_category)].plot(
            color=bivariate_palette[(i, j)], 
            ax=ax, 
            edgecolor='none'
        )
ax.set_axis_off()

# Leyenda
a = fig.add_axes([.3, .2, .1, .1], facecolor='y')
a.imshow(cmap_xy, origin='lower')
a.set_xlabel('Educación $\\rightarrow$', fontsize='small')
a.set_ylabel('Ingreso $\\rightarrow$', fontsize='small')
a.set_xticks([]), a.set_yticks([])
sns.despine(ax=a)

# Saving
fig = plt.gcf() 
fig.set_size_inches(10,10)  
plt.savefig('mapa-bivariado.png', dpi=700, bbox_inches='tight', facecolor='white', transparent=False)
# %%
