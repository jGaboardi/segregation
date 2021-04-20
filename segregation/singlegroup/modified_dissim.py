"""Modified Dissimilarity Segregation Index."""

__author__ = "Renan X. Cortes <renanc@ucr.edu>, Sergio J. Rey <sergio.rey@ucr.edu> and Elijah Knaap <elijah.knaap@ucr.edu>"

import numpy as np
import pandas as pd
import geopandas as gpd
from .dissim import _dissim
from .._base import (
    SingleGroupIndex,
    SpatialImplicitIndex,
)


def _modified_dissim(data, group_pop_var, total_pop_var, iterations=500):
    """Calculation of Modified Dissimilarity index.

    Parameters
    ----------
    data : pandas.DataFrame or geopandas.GeoDataFrame
        Dataframe or geodataframe if spatial index holding data for location of interest
    group_pop_var : string
        Variable containing the population count of the group of interest
    total_pop_var : string
        Variable in data that contains the total population count of the unit
    iterations : int
        The number of iterations the evaluate average classic dissimilarity under eveness.
        Default value is 500.

    Returns
    ----------
    statistic : float
                Modified Dissimilarity Index (Dissimilarity from Carrington and Troske (1997))
    data : pandas.DataFrame
        pandas DataFrame that contains the columns used to perform the estimate.

    Notes
    -----
    Based on Carrington, William J., and Kenneth R. Troske. "On measuring segregation in samples with small units." Journal of Business & Economic Statistics 15.4 (1997): 402-409.

    Reference: :cite:`carrington1997measuring`.

    """
    if type(iterations) is not int:
        raise TypeError("iterations must be an integer")

    if iterations < 2:
        raise TypeError("iterations must be greater than 1.")

    D = _dissim(data, group_pop_var, total_pop_var)[0]

    x = np.array(data[group_pop_var].astype(int))
    t = np.array(data[total_pop_var].astype(int))

    p_null = x.sum() / t.sum()

    Ds = np.empty(iterations)

    for i in np.array(range(iterations)):

        freq_sim = np.random.binomial(
            n=np.array([t.tolist()]),
            p=np.array([[p_null] * data.shape[0]]),
            size=(1, data.shape[0]),
        ).tolist()[0]
        data[group_pop_var] = freq_sim
        # data = data.assign(group_pop_var=freq_sim)
        aux = _dissim(data, group_pop_var, total_pop_var)[0]
        Ds[i] = aux

    D_star = Ds.mean()

    if D >= D_star:
        Dct = (D - D_star) / (1 - D_star)
    else:
        Dct = (D - D_star) / D_star

    if not isinstance(data, gpd.GeoDataFrame):
        core_data = data[[group_pop_var, total_pop_var]]

    else:
        core_data = data[[group_pop_var, total_pop_var, data.geometry.name]]

    return Dct, core_data


class ModifiedDissim(SingleGroupIndex, SpatialImplicitIndex):
    """Modified Dissimilarity Index.

    Parameters
    ----------
    data : pandas.DataFrame or geopandas.GeoDataFrame, required
        dataframe or geodataframe if spatial index holding data for location of interest
    group_pop_var : str, required
        name of column on dataframe holding population totals for focal group
    total_pop_var : str, required
        name of column on dataframe holding total overall population
    w : libpysal.weights.KernelW, optional
        lipysal spatial kernel weights object used to define an egohood
    network : pandana.Network
        pandana Network object representing the study area
    distance : int
        Maximum distance (in units of geodataframe CRS) to consider the extent of the egohood
    decay : str
        type of decay function to apply. Options include
    precompute : bool
        Whether to precompute the pandana Network object

    Attributes
    ----------
    statistic : float
                MinMax Index
    core_data : a pandas DataFrame
                A pandas DataFrame that contains the columns used to perform the estimate.

    Notes
    -----
    Based on Massey, Douglas S., and Nancy A. Denton. "The dimensions of residential segregation." Social forces 67.2 (1988): 281-315.

    Reference: :cite:`massey1988dimensions`.
    """

    def __init__(
        self,
        data,
        group_pop_var,
        total_pop_var,
        iterations=500,
        w=None,
        network=None,
        distance=None,
        decay=None,
        precompute=None,
        function="triangular",
    ):
        """Init."""

        SingleGroupIndex.__init__(self, data, group_pop_var, total_pop_var)
        if any([w, network, distance]):
            SpatialImplicitIndex.__init__(
                self, w, network, distance, decay, function, precompute
            )
        aux = _modified_dissim(
            self.data, self.group_pop_var, self.total_pop_var, iterations
        )

        self.statistic = aux[0]
        self.data = aux[1]
        self._function = _modified_dissim
