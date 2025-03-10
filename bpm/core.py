import numpy as np

# Global factors; these might be computed more dynamically in a full implementation.
laplacian_factor = None
index_factor = None

def compute_dE_dz(E_slice, n_r2_slice, dx, n0, sigma_x, k0):
    """
    Compute the derivative dE/dz using the BPM equation:
    
      ∂E/∂z = (i/(2 k0 n0)) (∂^2 E/∂x^2) + i (k0/(2 n0)) [n_r^2 - n0^2] E - sigma(x) E
    """
    # Finite-difference Laplacian in x
    laplacian_E = (np.roll(E_slice, 1, axis=0) - 2 * E_slice + np.roll(E_slice, -1, axis=0)) / dx**2
    laplacian_term = (1j / (2 * k0 * n0)) * laplacian_E
    index_term = 1j * (k0 / (2 * n0)) * (n_r2_slice - n0**2) * E_slice
    damping_term = - sigma_x * E_slice
    return laplacian_term + index_term + damping_term

def run_bpm(E, n_r2, x, z, dx, dz, n0, sigma_x, wavelength):
    """
    Run the BPM propagation using an RK4 integrator.
    
    Parameters:
      E: initial field (2D array, shape (len(x), len(z)); only E[:,0] is used)
      n_r2: refractive index squared distribution (2D array, shape (len(x), len(z)))
      x, z: transverse and propagation coordinates
      dx, dz: grid spacings in x and z
      n0: background refractive index
      sigma_x: 1D array for PML damping in x
      wavelength: wavelength in um
    
    Returns:
      E: propagated field (2D array)
    """
    k0 = 2 * np.pi / wavelength
    Nz = len(z)
    for zi in range(1, Nz):
        E_prev = E[:, zi-1]
        n_r2_slice = n_r2[:, zi-1]
        k1 = dz * compute_dE_dz(E_prev, n_r2_slice, dx, n0, sigma_x, k0)
        k2 = dz * compute_dE_dz(E_prev + k1/2, n_r2_slice, dx, n0, sigma_x, k0)
        k3 = dz * compute_dE_dz(E_prev + k2/2, n_r2_slice, dx, n0, sigma_x, k0)
        k4 = dz * compute_dE_dz(E_prev + k3, n_r2_slice, dx, n0, sigma_x, k0)
        E[:, zi] = E_prev + (k1 + 2*k2 + 2*k3 + k4) / 6
    return E
