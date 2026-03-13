import numpy as np
import numpy.typing as npt


def bilinear_interpolation (
            grid: np.ndarray,
            xy: npt.NDArray[np.float64]
        ) -> npt.NDArray[np.float64]:
    '''
    Returns an `ndarray` of interpolated occupancy values computed for
    xy-coordinates found in `xy` and the current occupancy map `grid`.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.
        xy (`ndarray`):
            A 2D `ndarray` of xy-coordinates with shape (`n`, 2), where `n` is
            the number of coordinate values, `x` values are stored in column 0,
            and `y` values are stored in column 1.

    Returns:
        interpolated (`ndarray`):
            A 1D `ndarray` of interpolated occupancy results with shape
            (`n`, 1), where `n` is the number of valid (not out-of-bounds)
            coordinates found in `xy`.
    '''

    # Get raw x and y coordinates
    x, y = xy[:, 0], xy[:, 1]

    # Get integer coordinates
    x_a = np.floor(x).astype(np.int32)
    x_b = x_a + 1
    y_a = np.floor(y).astype(np.int32)
    y_b = y_a + 1

    # Initialize the output array
    inter = np.ndarray(xy.shape[0], np.float64)

    # Mask to detect coordinates that are out-of-bounds
    mask = (x_a >= 0) & (x_b < grid.shape[1]) & \
            (y_a >= 0) & (y_b < grid.shape[0])

    # Find valid coordinates using the mask
    valid_x_a, valid_x_b = x_a[mask], x_b[mask]
    valid_y_a, valid_y_b = y_a[mask], y_b[mask]
    valid_x, valid_y = x[mask], y[mask]
    
    # Find cell corners
    q_a_a = grid[valid_y_a, valid_x_a]
    q_a_b = grid[valid_y_a, valid_x_b]
    q_b_a = grid[valid_y_b, valid_x_a]
    q_b_b = grid[valid_y_b, valid_x_b]

    # Compute x-coordinate interpolation weights
    w_a = (valid_x_b - valid_x) * q_a_a + (valid_x - valid_x_a) * q_a_b
    w_b = (valid_x_b - valid_x) * q_b_a + (valid_x - valid_x_a) * q_b_b

    # Compute interpolated values
    inter[mask] = (valid_y_b - valid_y) * w_a + (valid_y - valid_y_a) * w_b

    return inter