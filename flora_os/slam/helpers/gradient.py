import numpy as np


def gradient (grid: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray]:
    '''
    Returns the x and y gradients of the occupany map `grid`, where `h` is the
    side length of each square 'cell' in the map.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.
        h (`float`):
            The side length of each square 'cell' in the occupancy map.

    Returns:
        gradients (`tuple[ndarray]`):
            A `tuple` containing two `ndarray` gradient matrices derived from
            `grid`, each with shape (`h`, `w`), where `h` is the map height and
            `w` is the map width.

            - **g_x** (`ndarray`): Gradient values along the x-axis. 
            - **g_y** (`ndarray`): Gradient values along the y-axis. 
    '''

    # Initialize output ndarrays for x and y gradients
    g_x = np.ndarray(grid.shape, np.float64)
    g_y = np.ndarray(grid.shape, np.float64)

    # Compute the gradient along the x-axis
    g_x[0, :] = (grid[1, :] - grid[0, :]) / h
    g_x[-1, :] = (grid[-1, :] - grid[-2, :]) / h
    g_x[1:-1, :] = (grid[2:, :] - grid[0:-2, :]) / (2 * h)

    # Compute the gradient along the y-axis
    g_y[:, 0] = (grid[:, 1] - grid[:, 0]) / h
    g_y[:, -1] = (grid[:, -1] - grid[:, -2]) / h
    g_y[:, 1:-1] = (grid[:, 2:] - grid[:, 0:-2]) / (2 * h)

    return g_x, g_y