import numpy as np
import numpy.typing as npt
import scipy.sparse as sp


def compute_jo (
            poses: npt.NDArray[np.float64],
            odometry: npt.NDArray[np.float64]
        ) -> tuple[
            npt.NDArray[np.float64],
            sp.csc_matrix
        ]:
    '''
    Returns a `tuple` of an `ndarray` containing the residual error vector for
    all pose transitions and a `csc_matrix` containing the odometry Jacobian.

    Parameters:
        poses (`ndarray`):
            A 2D `ndarray` of poses with shape (`n`, 3), where `n` is the
            number of poses, `x` values are stored in column 0, `y` values are
            stored in column 1, and `theta` values are stored in column 2.
        odometry (`ndarray`):
            A 2D `ndarray` of incremental odometry data with shape
            (`n` - 1, 3), where `n` is the number of poses, `d_x` values are
            stored in column 0, `d_y` values are stored in column 1, and
            `d_theta` values are stored in column 2.

    Returns:
        transition_data (`tuple[ndarray, csc_matrix]`):
            A `tuple` of an `ndarray` containing the residual error vector for
            all pose transitions and a `csc_matrix` containing the odometry
            Jacobian.

            - **err_o** (`ndarray`): A 1D `ndarray` containing residual
            odometry error data with shape (3 * `n` - 1), where `n` is the
            number of poses.
            - **jo** (`csc_matrix`): A `csc_matrix` containing the odometry
            Jacobian.
    '''

    n_poses = poses.shape[0]
    n_trans = n_poses - 1

    p_a = poses[:-1]
    p_b = poses[1:]
    u_meas = odometry[1:]
    
    # Compute pose increments from poses
    dx = p_b[:, 0] - p_a[:, 0]
    dy = p_b[:, 1] - p_a[:, 1]
    dt = (p_b[:, 2] - p_a[:, 2] + np.pi) % (2 * np.pi) - np.pi
    ct, st = np.cos(p_a[:, 2]), np.sin(p_a[:, 2])
    l_dx = ct * dx + st * dy
    l_dy = -st * dx + ct * dy

    # Compute err_o
    err_x = u_meas[:, 0] - l_dx
    err_y = u_meas[:, 1] - l_dy
    err_t = (u_meas[:, 2] - dt + np.pi) % (2 * np.pi) - np.pi
    err_o = np.stack([err_x, err_y, err_t], axis=1).ravel()

    # Compute Jacobian values
    jo_v = np.stack(
        [
            np.stack(
                [-ct, -st, -st * dx + ct * dy, ct, st, np.zeros(n_trans)],
                axis = 1
            ),
            np.stack(
                [st, -ct, -ct * dx - st * dy, -st, ct, np.zeros(n_trans)],
                axis = 1
            ),
            np.stack(
                [
                    np.zeros(n_trans),
                    np.zeros(n_trans),
                    -np.ones(n_trans),
                    np.zeros(n_trans),
                    np.zeros(n_trans),
                    np.ones(n_trans)
                ],
                axis = 1
            )
        ],
        axis = 1
    ).ravel()

    # Create Jacobian indices
    jo_i = np.repeat(np.arange(n_trans * 3), 6)
    col_offsets = np.tile(np.arange(6), n_trans * 3).reshape(n_trans, 3, 6)
    pose_offsets = (np.arange(n_trans) * 3)[:, np.newaxis, np.newaxis]
    jo_j = (col_offsets + pose_offsets).ravel()

    # Construct Jacobian
    jo = sp.csc_matrix((jo_v, (jo_i, jo_j)), shape=(len(err_o), 3 * n_poses))

    return err_o, jo