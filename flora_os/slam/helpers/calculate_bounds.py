import numpy as np
import numpy.typing as npt
import scipy.signal as ss

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
        uniq_indices (`tuple[ndarray]`):
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

    # Apply exponential transform and clip values
    exp_grid = np.clip(np.exp(grid), 0.0, 1.0)

    # Create the kernel and perform a 2D convolution
    r = (Config.SEL_KERNEL_SIZE - 1) // 2
    kernel = np.ones(
        (Config.SEL_KERNEL_SIZE, Config.SEL_KERNEL_SIZE),
        np.float64
    ) / (Config.SEL_KERNEL_SIZE**2)
    conv = ss.convolve2d(exp_grid, kernel, mode='same')
    
    # Find edge cells (convolution value between 0.0 and 1.0)
    edge_mask = (conv > 0.0) & (conv < 1.0)
    id_all = np.argwhere(edge_mask)

    # Compute cell selection indices
    sel_n_cell = round(Config.SEL_DISTANCE / Config.SCALE)
    id_row_t = id_all[:, 0][:, None] - sel_n_cell
    id_col_l = id_all[:, 1][:, None] - sel_n_cell

    # Generate all selection indices
    i_offsets = np.arange(2 * sel_n_cell + 1)
    j_offsets = np.arange(2 * sel_n_cell + 1)
    uniq_sel_ids = np.unique(
        np.stack(
            # TODO: maybe 'ij' indexing?
            np.meshgrid(id_row_t + i_offsets, id_col_l + j_offsets),
            axis=-1
        ).reshape(-1, 2),
        axis = 0
    )

    # Compute variation indices
    var_offsets = np.mgrid[-2:3, -2:3].T.reshape(-1, 2)
    uniq_var_ids = np.unique(
        (uniq_sel_ids[:, None, :] + var_offsets).reshape(-1, 2),
        axis=0
    )

    return uniq_sel_ids, uniq_var_ids