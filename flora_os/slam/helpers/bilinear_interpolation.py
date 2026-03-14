import numpy as np
import numpy.typing as npt


def bilinear_interpolation (
            grid: npt.NDArray[np.float64],
            xy: npt.NDArray[np.float64]
        ) -> tuple[
            npt.NDArray[np.float64],
            npt.NDArray[np.float64],
            npt.NDArray[np.int32],
            npt.NDArray[np.float64]
        ]:
    '''
    Returns a `tuple` of 4 `ndarray` containing the global interpolation
    results, an 'in-bounds' mask, cell corner indices, and cell corner weights
    respectively.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.
        xy (`ndarray`):
            A 2D `ndarray` of `xy`-coordinates with shape (`n`, 2), where `n`
            is the number of coordinate values, `x` values are stored in column
            0, and `y` values are stored in column 1.

    Returns:
        interpolation_result (`tuple[ndarray, ndarray, ndarray, ndarray]`):
            A `tuple` containing 4 `ndarray`; the first contains the global
            interpolation results, the second contains an 'in-bounds' mask over
            all `xy`-coordinates, the third contains cell corner indices, and
            the fourth contains cell corner weights.
        
            - **interpolated** (`ndarray`): A 1D `ndarray` of interpolated
            occupancy results with shape (`n`), where `n` is the number of
            coordinates in `xy`.
            - **mask** (`ndarray`): A 1D `ndarray` of `bool` indicating which
            indices of `xy` represent valid (not out-of-bounds) coordinates.
            - **indices** (`ndarray`): A  2D `ndarray` containing cell corner
            indices with shape (4, `m`), where `m` is the number of valid (not
            out-of-bounds) coordinates from `xy`.
            - **weights** (`ndarray`): A 2D `ndarray` containing cell corner
            weights with shape (4, `m`), where `m` is the number of valid (not
            out-of-bounds) coordinates from `xy`.
    '''

    h, w = grid.shape

    # Get raw x and y coordinates
    x, y = xy[:, 0], xy[:, 1]

    # Get integer coordinates
    x_a = np.floor(x).astype(np.int32)
    x_b = x_a + 1
    y_a = np.floor(y).astype(np.int32)
    y_b = y_a + 1

    # Mask to detect coordinates that are out-of-bounds
    mask = (x_a >= 0) & (x_b < w) & (y_a >= 0) & (y_b < h)
    
    # Fractional offsets for valid coordinates
    dx = x[mask] - x_a[mask]
    dy = y[mask] - y_a[mask]

    # Create output index and weight ndarrays
    m = np.sum(mask)
    indices = np.empty((4, m), dtype=np.int32)
    weights = np.empty((4, m), dtype=np.float64)

    # Find cell corner indices
    w = grid.shape[1]
    indices[0] = y_a[mask] * w + x_a[mask]
    indices[1] = y_a[mask] * w + x_b[mask]
    indices[2] = y_b[mask] * w + x_a[mask]
    indices[3] = y_b[mask] * w + x_b[mask]

    # Compute cell corner weights
    weights[0] = (1 - dx) * (1 - dy)
    weights[1] = dx * (1 - dy)
    weights[2] = (1 - dx) * dy
    weights[3] = dx * dy

    # Compute interpolated values
    flat = grid.ravel()
    interpolated = np.zeros(len(x), dtype=np.float64)
    interpolated[mask] = np.sum(flat[indices] * weights, axis=0)

    return interpolated, mask, indices, weights