import numpy as np
import numpy.typing as npt
import scipy.ndimage as sn

from ..config import Config


def calculate_bounds (
            grid: npt.NDArray[np.float64]
        ) -> tuple[npt.NDArray[np.int_], npt.NDArray[np.int_]]:
    '''
    Returns unique selection and variation indices of the bounds of `grid` by
    applying a 2D convolution.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.

    Returns:
        uniq_indices (`tuple[ndarray, ndarray]`):
            A `tuple` containing two 2D `ndarray` containing indices derived
            from a 2D convolution over `grid`.

            - **uniq_sel_ids** (`ndarray`): Unique selection indices derived
            directly from the 2D convolution over `grid` with shape (`n`, 2),
            where `n` is the number of unique selection index pairs, `i`
            indices are stored in column 0, and `j` indices are stored in
            column 1.
            - **uniq_var_ids** (`ndarray`): Unique variation indices derived
            from `uniq_sel_ids` with shape (`m`, 2), where `m` is the number of
            unique variation index pairs, `i` indices are stored in column 0,
            and `j` indices are stored in column 1.
    '''

    # Find edges
    explored = (grid != 0.0)
    bound_mask = sn.binary_dilation(explored) ^ explored

    # Find unique selection indices
    sel_n_cell = int(round(Config.SEL_DISTANCE / Config.SCALE))
    sel_mask = sn.binary_dilation(bound_mask, iterations=sel_n_cell)
    uniq_sel_ids = np.argwhere(sel_mask)

    # Find variation indices
    var_mask = sn.binary_dilation(sel_mask, iterations=2)
    uniq_var_ids = np.argwhere(var_mask)

    return uniq_sel_ids, uniq_var_ids