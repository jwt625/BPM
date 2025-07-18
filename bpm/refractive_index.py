from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


def generate_lens_n_r2(
    x: NDArray[np.float64],
    z: NDArray[np.float64],
    lens_diameter: float,
    lens_thickness: float,
    R1: float,
    R2: float,
    n_lens: float,
    n0: float,
    lens_center_z: float,
    x_lens: float,
) -> NDArray[np.float64]:
    """
    Generate the squared refractive index distribution for a spherical lens.
    """
    Nx = len(x)
    Nz = len(z)
    n_r2 = np.full((Nx, Nz), n0**2, dtype=np.float64)
    z1 = lens_center_z - lens_thickness / 2.0
    z2 = lens_center_z + lens_thickness / 2.0
    z_first = z1 + (R1 - np.sqrt(np.maximum(R1**2 - (x - x_lens) ** 2, 0)))
    z_second = z2 - (R2 - np.sqrt(np.maximum(R2**2 - (x - x_lens) ** 2, 0)))
    for ix in range(Nx):
        if abs(x[ix] - x_lens) > lens_diameter / 2:
            continue
        in_lens = (z >= z_first[ix]) & (z <= z_second[ix])
        n_r2[ix, in_lens] = n_lens**2
    return n_r2


def generate_waveguide_n_r2(
    x: NDArray[np.float64],
    z: NDArray[np.float64],
    l: float,
    L: float,
    w: float,
    n_WG: float,
    n0: float,
) -> NDArray[np.float64]:
    """
    Generate the squared refractive index distribution for an S-bend waveguide.

    Parameters:
    -----------
    x, z : array_like
        1D coordinate arrays
    l : float
        Lateral displacement (can be positive or negative)
    L : float
        Propagation length (must be positive)
    w : float
        Waveguide width (must be positive)
    n_WG : float
        Waveguide core refractive index (must be > n0)
    n0 : float
        Background refractive index (must be positive)

    Returns:
    --------
    n_r2 : ndarray
        2D array of squared refractive index distribution
    """
    # Input validation
    x = np.asarray(x)
    z = np.asarray(z)
    if x.ndim != 1 or z.ndim != 1:
        raise ValueError("x and z must be 1D arrays")
    if L <= 0:
        raise ValueError("Propagation length L must be positive")
    if w <= 0:
        raise ValueError("Waveguide width w must be positive")
    if n_WG <= n0:
        raise ValueError("Core index n_WG must be greater than background index n0")
    if n0 <= 0:
        raise ValueError("Background index n0 must be positive")

    Nx = len(x)
    Nz = len(z)
    n_r2 = np.full((Nx, Nz), n0**2, dtype=np.float64)
    x_c = (l / L) * z - (l / (2 * np.pi)) * np.sin((2 * np.pi / L) * z)
    x_c = np.clip(x_c, 0, l)
    for iz in range(Nz):
        lower_edge = x_c[iz] - w / 2.0
        upper_edge = x_c[iz] + w / 2.0
        in_wg = (x >= lower_edge) & (x <= upper_edge)
        n_r2[in_wg, iz] = n_WG**2
    return n_r2


def generate_MMI_n_r2(
    x: NDArray[np.float64],
    z: NDArray[np.float64],
    z_MMI_start: float,
    L_MMI: float,
    w_MMI: float,
    w_wg: float,
    d: float,
    n_WG: float,
    n_MMI: float,
    n0: float,
) -> NDArray[np.float64]:
    """
    Generate the squared refractive index distribution for an MMI-based splitter.
    """
    Nx = len(x)
    Nz = len(z)
    X, Z = np.meshgrid(x, z, indexing="ij")
    n_r2 = np.full((Nx, Nz), n0**2, dtype=np.float64)
    z_MMI_end = z_MMI_start + L_MMI
    mask_input = (z_MMI_start > Z) & (
        (np.abs(X + d / 2) <= w_wg / 2) | (np.abs(X - d / 2) <= w_wg / 2)
    )
    mask_MMI = (z_MMI_start <= Z) & (z_MMI_end >= Z) & (np.abs(X) <= w_MMI / 2)
    mask_output = (z_MMI_end < Z) & (
        (np.abs(X + d / 2) <= w_wg / 2) | (np.abs(X - d / 2) <= w_wg / 2)
    )
    n_r2[mask_input] = n_WG**2
    n_r2[mask_output] = n_WG**2
    n_r2[mask_MMI] = n_MMI**2
    return n_r2
