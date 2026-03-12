import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spl

from ..config import Config


def delta (
            grid: np.ndarray,
            jp: sp.csc_matrix,
            jd: sp.csc_matrix,
            jo: sp.csc_matrix,
            err_s: np.ndarray,
            err_o: np.ndarray,
            i_o: sp.csc_matrix,
            weighted_hh: sp.csc_matrix
        ) -> tuple[np.ndarray, np.ndarray, float, float]:
    
    jp_s = jp[:, 3:].tocsc()
    jo_s = jo[:, 3:].tocsc()

    u = jp_s.T @ jp_s + Config.WEIGHT_O * (jo_s.T @ i_o @ jo_s)
    v = jd.T @ jd + weighted_hh
    w = jp_s.T @ jd

    e_p = -jp_s.T @ err_s - Config.WEIGHT_O * (jo_s.T @ i_o @ err_o)
    e_d = -jd.T @ err_s
    xh = grid.T.flatten()
    e_h = -weighted_hh @ xh
    e_d_e_h = e_d + e_h

    i_i = sp.bmat([[u, w], [w.T, v]], 'csc')
    e_e = np.concatenate((e_p, e_d_e_h))

    max_iter = min(200, int(np.floor(np.sqrt(i_i.shape[0]))))

    delta, _ = spl.cg(i_i, e_e, tol=0.005, maxiter=max_iter)

    num_p = jp_s.shape[1]
    delta_p = delta[:num_p]
    delta_d = delta[num_p:]

    total_delta = np.dot(delta, delta)
    mean_delta = total_delta / delta.size

    total_delta_p = np.dot(delta_p, delta_p)
    mean_delta_p = total_delta_p / delta_p.size

    return delta_p, delta_d, mean_delta, mean_delta_p