# main.py
# ==================================================
# settings
import warnings
warnings.filterwarnings('ignore')
# --------------------------------------------------
# standard
from typing import Any
# requirements
import numpy as np
import pandas as pd
import geopandas as gpd
import spectra
import mapclassify
import matplotlib.pyplot as plt
from matplotlib.colors import rgb2hex
import seaborn as sns
# --------------------------------------------------

# [NOTE] utilities
class Utils(object):
    
    @classmethod
    def replace_ubi_rl(cls, row: Any, col: str) -> str:
        length = len(y := row[col])
        if length == 5:
            return '0' + y
        elif length == 4:
            return '00' + y
        elif length == 3:
            return '000' + y
        elif length == 2:
            return '0000' + y
        elif length == 1:
            return '00000' + y
        else:
            return y
    
    @classmethod
    def replace_ubi_rr(cls, row: Any, col: str) -> str:
        length = len(y := row[col])
        if length == 5:
            return y + '0'
        elif length == 4:
            return y + '00'
        elif length == 3:
            return y + '000'
        elif length == 2:
            return y + '0000'
        elif length == 1:
            return y + '00000'
        else:
            return y

def main() -> None:
    # [NOTE] data provincial
    df_provincial = pd.read_csv('./temp/db_provincial.csv', delimiter=';', header=0)
    df_provincial.rename(columns={'prov': 'UBIGEO'}, inplace=True)
    
    df_provincial['UBIGEO'] = df_provincial['UBIGEO'].astype(str)
    df_provincial['UBIGEO'] = df_provincial.apply(Utils.replace_ubi_rl, col='UBIGEO', axis=1)
    df_provincial.set_index('UBIGEO', inplace=True)
    
    # [NOTE] shapefile data
    stgo = gpd.read_file('./data/shapefile/PROVINCIAS.shp')
    stgo.rename({'IDPROV': 'UBIGEO'}, axis='columns', inplace=True)
    
    stgo['UBIGEO'] = stgo.apply(Utils.replace_ubi_rr, col='UBIGEO', axis=1)
    stgo.set_index('UBIGEO', inplace=True)
    
    # [NOTE] joining
    df_georef = stgo.join(df_provincial)
    
    # [NOTE] Se asumirá valor promedio de `a_edu` y `ingm_fampc` de la región 16 en missing.
    mean_aedu_dep16 = df_georef[df_georef['IDDPTO'] == '16']['a_edu'].mean()
    mean_ingm_dep16 = df_georef[df_georef['IDDPTO'] == '16']['ingm_fampc'].mean()
    df_georef.fillna({'a_edu': mean_aedu_dep16, 'ingm_fampc': mean_ingm_dep16}, inplace=True)
    
    # [NOTE] coloring
    colors = ['#be64ac', '#dfb0d6', '#e8e8e8', '#ace4e4', '#5ac8c8']
    n_categories = 3
    full_palette = sns.color_palette(colors, n_colors=(n_categories-1)*2 + 1)
    
    cmap_x = full_palette[n_categories-1:]
    cmap_y = list(reversed(full_palette))[n_categories-1:]
    
    # [NOTE] intervals Fisher-Jenks
    edu_bin = mapclassify.FisherJenks(df_georef['a_edu'], k=n_categories)
    ingm_bin = mapclassify.FisherJenks(df_georef['ingm_fampc'], k=n_categories)
    
    # [NOTE] mixed colors palette
    cmap_xy, bivariate_palette = [], dict()
    
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
    
    # [NOTE] mapping
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    for i in range(n_categories):
        for j in range(n_categories):
            areas_in_category = set(np.where(edu_bin.yb == i)[0]) & set(np.where(ingm_bin.yb == j)[0])
            if df_georef.iloc[list(areas_in_category)].empty:
                continue
            df_georef.iloc[list(areas_in_category)].plot(
                color=bivariate_palette[(i, j)], ax=ax, edgecolor='none'
            )
    ax.set_axis_off()
    
    # [NOTE] legend
    a = fig.add_axes([.3, .2, .1, .1], facecolor='y')
    a.imshow(cmap_xy, origin='lower')
    a.set_xlabel('Educación $\\rightarrow$', fontsize='small')
    a.set_ylabel('Ingreso $\\rightarrow$', fontsize='small')
    a.set_xticks([]), a.set_yticks([])
    sns.despine(ax=a)
    
    # [NOTE] exporting
    fig = plt.gcf()
    fig.set_size_inches(10,10)
    plt.savefig(output := './temp/mapa-bivariado.png', dpi=700, bbox_inches='tight', facecolor='white', transparent=False)
    print('[INFO] image exported at: {}'.format(output))

if __name__ == '__main__':
    main()
