from libpysal.examples import load_example
import geopandas as gpd
import numpy as np
from segregation.multigroup import MultiDissim
from segregation.dynamics import compute_multiscalar_profile
import quilt3
import pandana as pdna


p = quilt3.Package.browse('osm/metro_networks_8k', "s3://spatial-ucr/")
p['40900.h5'].fetch()
net = pdna.Network.from_hdf5('40900.h5')

def test_multiscalar():
    s_map = gpd.read_file(load_example("Sacramento1").get_path("sacramentot2.shp"))
    df = s_map.to_crs(s_map.estimate_utm_crs())
    profile = compute_multiscalar_profile(
        gdf=df,
        segregation_index=MultiDissim,
        distances=[500, 1000, 1500, 2000],
        groups=["HISP", "BLACK", "WHITE"],
        index_type="multi_group",
    )
    np.testing.assert_array_almost_equal(
        profile.values, [0.42469982, 0.42465797, 0.41734378, 0.40082459, 0.37768411]
    )


def test_multiscalar_network():
    s_map = gpd.read_file(load_example("Sacramento1").get_path("sacramentot2.shp"))
    df = s_map.to_crs(s_map.estimate_utm_crs())
    profile = compute_multiscalar_profile(
        gdf=df,
        segregation_index=MultiDissim,
        distances=[500, 1000],
        groups=["HISP", "BLACK", "WHITE"],
        index_type="multi_group",
    )
    np.testing.assert_array_almost_equal(
        profile.values, [0.4247, 0.424658, 0.417344]
    )
