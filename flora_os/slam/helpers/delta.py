import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..config import Config


def delta (
            grid: npt.NDArray[np.float64],
            jp: sp.csc_matrix,
            jd: sp.csc_matrix,
            jo: sp.csc_matrix,
            err_s: npt.NDArray[np.float64],
            err_o: npt.NDArray[np.float64],
            i_o: sp.csc_matrix,
            weighted_hh: sp.csc_matrix,
            config: Config
        ) -> tuple[
            npt.NDArray[np.float64],
            npt.NDArray[np.float64],
            float,
            float
        ]:
    '''
    Returns parameter update deltas according to the current occupancy map
    `grid`; the Jacobian matrices `jp`, `jd`, and `jo`; the error vectors
    `err_s` and `err_o`; the observation information matrix `i_o`; and the
    weighted regularization Hessian `weighted_hh`.

    Parameters:
        grid (`ndarray`):
            A 2D `ndarray` of occupancy values with shape (`h`, `w`), where `h`
            is the map height and `w` is the map width.
        jp (`csc_matrix`):
            A `csc_matrix` containing the pose Jacobian with shape
            (`m`, 3 * `n`), where `m` is the number of constraints (the size of
            `err_s`) and `n` is the number of poses.
        jd (`csc_matrix`):
            A `csc_matrix` containing the disparity Jacobian with shape
            (`m`, `w` * `h`), where `m` is the number of constraints (the size
            of `err_s`), `w` is the map width, and `h` is the map height.
        jo (`csc_matrix`):
            A `csc_matrix` containing the observation Jacobian with shape
            (3 * (`n` - 1), 3 * `n`), where `n` is the number of poses.
        err_s (`ndarray`):
            A 1D `ndarray` of sensor error values with shape (`m`), where `m`
            is the number of sensor measurements.
        err_o (`ndarray`):
            A 1D `ndarray` of odometry error values with shape (3 * (`n` - 1)),
            where `n` is the number of poses.
        i_o (`csc_matrix`):
            A `csc_matrix` containing information/weight data for observations
            with shape (3 * (`n` - 1), 3 * (`n` - 1)), where `n` is the number
            of poses.
        weighted_hh (`csc_matrix`):
            A `csc_matrix` containing a weighted Hessian with shape
            (`w` * `h`, `w` * `h`), where `w` is the map width and `h` is the
            map height.
        config (`Config`):
            The configuration object to obtain setting selection values from.

    Returns:
        deltas (`tuple[ndarray, ndarray, float, float]`):
            A `tuple` containing two 1D `ndarray` parameter delta vectors for
            occupancy map and pose updates, the mean delta across all delta
            values, and the mean delta for pose updates.

            - **delta_d** (`ndarray`): A 1D `ndarray` of occupancy map
            parameter deltas with shape (`w` * `h`), where `w` is the map width
            and `h` is the map height.
            - **delta_p** (`ndarray`): A 1D `ndarray` of pose parameter deltas
            with shape (3 * `n`)), where `n` is the number of poses.
            - **mean_delta** (`float`): The mean delta across all parameters.
            - **mean_delta_p** (`float`): The mean delta across all pose
            parameters.
    '''
    
    # Slice Jacobian matrices
    jp_s = jp[:, 3:].tocsc()
    jo_s = jo[:, 3:].tocsc()
    
    # Construct Hessian blocks
    u = jp_s.T @ jp_s + Config.WEIGHT_O * (jo_s.T @ i_o @ jo_s)
    v = jd.T @ jd + weighted_hh
    w = jp_s.T @ jd

    # Compute gradient vectors (RHS of Conjugate Gradient)
    e_p = -jp_s.T @ err_s - Config.WEIGHT_O * (jo_s.T @ i_o @ err_o)
    xh = grid.ravel()
    e_d_e_h = -jd.T @ err_s - (weighted_hh @ xh)

    # Combine into a block system
    i_i = sp.bmat([[u, w], [w.T, v]], format='csc')
    e_e = np.concatenate((e_p, e_d_e_h))

    # Create Jacobi preconditioner
    diagonal = i_i.diagonal()
    diagonal[diagonal == 0] = 1.0
    m_inv = sp.diags(1.0 / diagonal)

    # Solve the system with the Conjugate Gradient method
    params = config.delta_solver_params(i_i.shape[0])
    delta, _ = spl.cg(i_i, e_e, m=m_inv, **params)

    # Split results
    num_p = jp_s.shape[1]
    delta_p = delta[:num_p]
    delta_d = delta[num_p:]

    # Compute RMS values
    mean_delta = np.sqrt(np.mean(delta**2))
    mean_delta_p = np.sqrt(np.mean(delta_p**2))

    return delta_d, delta_p, mean_delta, mean_delta_p