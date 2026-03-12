import numpy as np


def gradient (grid: np.ndarray, h: float) -> tuple[np.ndarray, np.ndarray]:
    g_x = np.ndarray(grid.shape, np.float64)
    g_y = np.ndarray(grid.shape, np.float64)

    g_x[0, :] = (grid[1, :] - grid[0, :]) / h
    g_x[-1, :] = (grid[-1, :] - grid[-2, :]) / h
    g_x[1:-1, :] = (grid[2:, :] - grid[0:-2, :]) / (2 * h)

    g_y[:, 0] = (grid[:, 1] - grid[:, 0]) / h
    g_y[:, -1] = (grid[:, -1] - grid[:, -2]) / h
    g_y[:, 1:-1] = (grid[:, 2:] - grid[:, 0:-2]) / (2 * h)

    return g_x, g_y