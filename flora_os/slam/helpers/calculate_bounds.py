import numpy as np

from ..config import Config


def calculate_bounds (grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    exp_grid = np.clip(np.exp(grid), 0.0, 1.0)
    exp_grid = exp_grid.astype(np.int32).astype(np.float64)
    r = (Config.SEL_KERNEL_SIZE - 1) // 2
    sel_n_cell = round(Config.SEL_DISTANCE / Config.SCALE)
    kernel = np.ones(
        (Config.SEL_KERNEL_SIZE, Config.SEL_KERNEL_SIZE),
        np.float64
    ) / (Config.SEL_KERNEL_SIZE**2)
    conv = np.zeros_like(grid)

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if (i - r + 1) > 0 and (j - r + 1) > 0 and \
                    (i + r + 1) <= Config.SIZE_W and \
                    (j + r + 1) <= Config.SIZE_H:
                block = exp_grid[i-r:i + r + 1, j - r:j + r + 1]
            elif (i - r + 1) <= 0 and (j - r + 1) <= 0 and \
                    (i + r + 1) <= Config.SIZE_W and \
                    (j + r + 1) <= Config.SIZE_H:
                block = exp_grid[i:i + 2 * r + 1, j:j + 2 * r + 1]
            elif (i - r + 1) > 0 and (j - r + 1) <= 0 and \
                    (i + r + 1) > Config.SIZE_W and \
                    (j + r + 1) <= Config.SIZE_H:
                block = exp_grid[i - 2 * r:i + 1, j:j + 2 * r + 1]
            elif (i - r + 1) > 0 and (j - r + 1) > 0 and \
                    (i + r + 1) > Config.SIZE_W and \
                    (j + r + 1) > Config.SIZE_H:
                block = exp_grid[i - 2 * r:i + 1, j - 2 * r:j + 1]
            elif (i - r + 1) <= 0 and (j - r + 1) > 0 and \
                    (i + r + 1) <= Config.SIZE_W and \
                    (j + r + 1) <= Config.SIZE_H:
                block = exp_grid[i:i + 2 * r + 1, j - r:j + r + 1]
            elif (i - r + 1) > 0 and (j - r + 1) > 0 and \
                    (i + r + 1) > Config.SIZE_W and \
                    (j + r + 1) <= Config.SIZE_H:
                block = exp_grid[i - 2 * r:i + 1, j - r:j + r + 1]
            elif (i - r + 1) > 0 and (j - r + 1) <= 0 and \
                    (i + r + 1) <= Config.SIZE_W and \
                    (j + r + 1) <= Config.SIZE_H:
                block = exp_grid[i - r:i + r + 1, j:j + 2 * r + 1]
            elif (i - r + 1) > 0 and (j - r + 1) > 0 and \
                    (i + r + 1) <= Config.SIZE_W and \
                    (j + r + 1) > Config.SIZE_H:
                block = exp_grid[i - r:i + r + 1, j - 2 * r:j + 1]
            elif (i - r + 1) <= 0 and (j - r + 1) > 0 and \
                    (i + r + 1) <= Config.SIZE_W and \
                    (j + r + 1) > Config.SIZE_H:
                block = exp_grid[i:i + 2 * r + 1, j - 2 * r:j + 1]
            else:
                print(f'missing some elements, the index is {i}, {j}')
                continue

            conv[i, j] = np.sum(kernel * block)

    edge = np.zeros_like(conv)
    edge[(conv > 0.0) & (conv < 1.0)] = 1
    id_all = np.argwhere(edge == 1)
    id_row, id_col = id_all[:, 0], id_all[:, 1]
    id_row_t = id_row - sel_n_cell
    id_col_l = id_col - sel_n_cell

    temp_sel_id = []
    for i in range(2 * sel_n_cell + 1):
        for j in range(2 * sel_n_cell + 1):
            temp_sel_id.append(
                np.column_stack((id_row_t + i, id_col_l + j))
            )

    temp_sel_id = np.vstack(temp_sel_id)
    uniq_sel_id = np.unique(temp_sel_id, axis=0)

    var_id = []
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            var_id.append(uniq_sel_id + [dx, dy])

    var_id = np.vstack(var_id)

    var_id_r = var_id.copy()
    var_id_r[:, 1] += 1

    var_id_b = var_id.copy()
    var_id_b[:, 0] += 1

    var_id_b_r = var_id.copy()
    var_id_b_r[:, 0] += 1
    var_id_b_r[:, 1] += 1

    var_id_all = np.vstack((var_id, var_id_r, var_id_b, var_id_b_r))
    uniq_var_id = np.unique(var_id_all, axis=0)

    return uniq_sel_id, uniq_var_id