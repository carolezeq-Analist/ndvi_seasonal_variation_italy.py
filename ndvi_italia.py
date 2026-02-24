import rasterio
import numpy as np
import folium
import matplotlib.pyplot as plt
from PIL import Image

# ==========================
# 1️ LER RASTER COM MÁSCARA
# ==========================

raster_path = "delta_italia.tiff"

with rasterio.open(raster_path) as src:
    ndvi = src.read(1, masked=True)   # já ignora NoData
    bounds = src.bounds
    crs = src.crs



# ==========================
# 2️ DEFINIR ESCALA FIXA SIMÉTRICA
# (melhor prática para NDVI diferença)
# ==========================

# Definimos limite fixo técnico
vmin = -0.16
vmax = 0.28

# Garantir que valores não extrapolem
ndvi_clipped = np.clip(ndvi, vmin, vmax)

# Normalizar entre 0 e 1
ndvi_norm = (ndvi_clipped - vmin) / (vmax - vmin)


# 3️ APLICAR COLORMAP


colormap = plt.cm.RdBu_r  # azul branco vermelho / azul redução, vermelho aumento
colored = colormap(ndvi_norm)

# Converter para 8 bits RGB
colored_img = (colored[:, :, :3] * 255).astype(np.uint8)

# Tornar pixels mascarados transparentes
ndvi[ndvi == -9999] = np.nan  # garantir que NoData seja NaN
alpha = np.where(np.isnan(ndvi_norm), 0, 255).astype(np.uint8)
rgba = np.dstack((colored_img, alpha))


Image.fromarray(rgba).save(r"C:\\Users\\carol\\OneDrive\\Imagens\\PROJETOS\\pygis\\ndvi_diff_colored.png")


# 4️ CONFIGURAR BOUNDING BOX


min_lat = bounds.bottom
min_lon = bounds.left
max_lat = bounds.top
max_lon = bounds.right

center_lat = (min_lat + max_lat) / 2
center_lon = (min_lon + max_lon) / 2


# 5️ CRIAR WEBMAP


m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=16,
    tiles="CartoDB positron"
)

folium.raster_layers.ImageOverlay(
    image="ndvi_diff_colored.png",
    bounds=[[min_lat, min_lon], [max_lat, max_lon]],
    opacity=0.8,
    name="NDVI Seasonal Difference"
).add_to(m)

folium.LayerControl().add_to(m)


# 6️ PAINEL LATERAL EXPLICATIVO


html = """
<div style="
position: fixed;
top: 20px;
right: 20px;
width: 320px;
background-color: white;
padding: 15px;
z-index:9999;
box-shadow: 2px 2px 6px rgba(0,0,0,0.3);
font-size: 14px;
">

<h4>Seasonal NDVI Difference</h4>

<p><b>Red areas:</b> Increased vegetation vigor during peak season</p>
<p><b>White areas:</b> No change in vegetation vigor</p>
<p><b>Blue areas:</b> Reduced vegetation vigor</p>
<p><b>Scale:</b> Fixed between -0.16 and +0.28</p>

<hr>
<p><b>Satellite:</b> Sentinel-2</p>
<p><b>Index:</b> NDVI (High season - Low season)</p>
<p><b>Projection:</b> EPSG:4326</p>

</div>
"""

m.get_root().html.add_child(folium.Element(html))


# 7 SALVAR


m.save("index.html")

print("WebGIS gerado com sucesso!")