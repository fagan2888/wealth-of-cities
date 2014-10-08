import numpy as np
from scipy import optimize

import model
from test_model import get_initial_guess

# define the number of cities
num_cities = model.num_cities

# define parameters
f, beta, phi, tau = 1.0, 1.31, 1.0 / 1.31, 0.05
theta = np.repeat(10.0, num_cities)

initial_guess = get_initial_guess(num_cities, f, beta, phi, tau, theta)


def equilibrium_system(X, f, beta, phi, tau, theta):
    """
    System of non-linear equations defining the model equilibrium.

    Parameters
    ----------
    X : ndarray
    f : float
        Firms fixed cost of production.
    beta : float
        Scaling factor for aggregate labor supply in a city.
    phi : float
    tau : float
        Iceberg trade costs.
    theta : ndarray
        Elasticity of substitutio between varieties of the consumption good.

    Returns
    -------
    residual : ndarray
        Equilibrium values of the endogenous variables will make the residual
        zero everywhere.

    """
    P = np.append(np.ones(1.0), X[:num_cities-1])
    Y = X[num_cities-1:2 * num_cities-1]
    W = X[2 * num_cities-1:3 * num_cities-1]
    M = X[3 * num_cities-1:]
    residual = model.numeric_system(P, Y, W, M, f, beta, phi, tau, theta).ravel()
    return residual


def equilibrium_jacobian(X, f, beta, phi, tau, theta):
    """
    Jacobian matrix of partial derivatives for the system of non-linear
    equations defining the model equilibrium.

    Parameters
    ----------
    X : ndarray
    f : float
        Firms fixed cost of production.
    beta : float
        Scaling factor for aggregate labor supply in a city.
    phi : float
    tau : float
        Iceberg trade costs.
    theta : ndarray
        Elasticity of substitution between varieties of the consumption good.

    Returns
    -------
    jac : ndarray
        Jacobian matrix of partial derivatives.

    """
    P = np.append(np.ones(1.0), X[:num_cities-1])
    Y = X[num_cities-1:2 * num_cities-1]
    W = X[2 * num_cities-1:3 * num_cities-1]
    M = X[3 * num_cities-1:]

    jac = model.numeric_jacobian(P, Y, W, M, f, beta, phi, tau, theta)
    return jac


# solve for the model equilibrium
result = optimize.root(equilibrium_system,
                       x0=initial_guess,
                       args=(f, beta, phi, tau, theta),
                       #jac=equilibrium_jacobian,
                       method='hybr',
                       tol=1e-6,
                       #options={'disp': True}
                       )

print("Solution converged? {}".format(result.success))
print("Equilibrium nominal price levels:\n{}".format(result.x[:num_cities-1]))
print("Equilibrium nominal GDP:\n{}".format(result.x[num_cities-1:2 * num_cities-1]))
print("Equilibrium nominal wages:\n{}".format(result.x[2 * num_cities-1:3 * num_cities-1]))
print("Equilibrium number of firms:\n{}".format(result.x[3 * num_cities-1:]))
