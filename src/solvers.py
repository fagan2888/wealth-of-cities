import numpy as np
from scipy import optimize
import sympy as sym

import models

# define variables
L, M, P, W, Y = sym.var('L, M, P, W, Y')

# define parameters
f, beta, phi, tau, theta = sym.var('f, beta, phi, tau, theta')


class InitialGuess(object):

    def __init__(self, model):
        """
        Create an instance of the InitialGuess class.

        Parameters
        ----------
        model : models.Model
            An instance of the models.Model class.

        """
        self.model = model

    @property
    def guess(self):
        """
        The initial guess for the model equilibrium.

        :getter: Return current initial guess.
        :type: numpy.ndarray

        """
        raise NotImplementedError


class IslandsGuess(InitialGuess):

    __city = None

    @property
    def city(self):
        """
        An instance of the SingleCityModel class.

        :getter: Return the current instance.
        :type: models.SingleCityModel

        """
        if self.__city is None:
            params = self.model.params
            physical_distances = self.model.physical_distances
            population = self.model.population

            # create an instance of the SingleCityModel
            self.__city = models.SingleCityModel(params,
                                                 physical_distances,
                                                 population)

        return self.__city

    @property
    def guess(self):
        """
        The initial guess for the model equilibrium.

        :getter: Return current initial guess.
        :type: numpy.ndarray

        """
        # initial guess for price levels
        P0 = np.repeat(1.0, self.model.N-1)

        # initial guess for nominal gdp, wages, and number of firms
        Y0 = np.empty(self.model.N)
        W0 = np.empty(self.model.N)
        M0 = np.empty(self.model.N)

        for h, population in enumerate(self.city.population[:self.model.N]):
            Y0[h] = self.city.compute_nominal_gdp(np.ones(1.0),
                                                  np.array([population]),
                                                  self.city.params)
            W0[h] = self.city.compute_nominal_wage(np.ones(1.0),
                                                   np.array([population]),
                                                   self.city.params)
            M0[h] = self.city.compute_number_firms(np.ones(1.0),
                                                   np.array([population]),
                                                   self.city.params)

        return np.hstack((P0, Y0, W0, M0))


class Solver(object):

    __numeric_jacobian = None
    __numeric_system = None

    _modules = [{'ImmutableMatrix': np.array}, "numpy"]

    def __init__(self, model):
        """
        Create and instance of the Solver class.

        Parameters
        ----------
        model : model.model
            Instance of the model.Model class that you wish to solve.

        """
        self.model = model

        # create an instance of the InitialGuess class
        self.initial_guess = IslandsGuess(model)

    def _clear_cache(self):
        """Clear all cached values."""
        self.__numeric_jacobian = None
        self.__numeric_system = None

    @property
    def _numeric_jacobian(self):
        """
        Vectorized function for numeric evaluation of model Jacobian.

        :getter: Return the current function.
        :type: function

        """
        if self.__numeric_jacobian is None:
            self.__numeric_jacobian = sym.lambdify(self.model._symbolic_args,
                                                   self.model._symbolic_jacobian,
                                                   self._modules)
        return self.__numeric_jacobian

    @property
    def _numeric_system(self):
        """
        Vectorized function for numeric evaluation of model equations.

        :getter: Return the current function.
        :type: function

        """
        if self.__numeric_system is None:
            self.__numeric_system = sym.lambdify(self.model._symbolic_args,
                                                 self.model._symbolic_system,
                                                 self._modules)
        return self.__numeric_system

    def system(self, X):
        """
        System of non-linear equations defining the model equilibrium.

        Parameters
        ----------
        X : numpy.ndarray
            Array containing values of the endogenous variables.

        Returns
        -------
        residual : numpy.ndarray
            Value of the model residual given current values of endogenous
            variables and parameters.

        """
        P = np.append(np.ones(1.0), X[:self.model.N-1])
        Y = X[self.model.N-1:2 * self.model.N-1]
        W = X[2 * self.model.N-1:3 * self.model.N-1]
        M = X[3 * self.model.N-1:]
        residual = self._numeric_system(P, Y, W, M, self.model.population, **self.model.params)
        return residual.ravel()

    def jacobian(self, X):
        """
        Jacobian matrix of partial derivatives for the system of non-linear
        equations defining the model equilibrium.

        Parameters
        ----------
        X : numpy.ndarray
            Array containing values of the endogenous variables.

        Returns
        -------
        jac : numpy.ndarray
            Jacobian matrix of partial derivatives.

        """
        P = np.append(np.ones(1.0), X[:self.model.N-1])
        Y = X[self.model.N-1:2 * self.model.N-1]
        W = X[2 * self.model.N-1:3 * self.model.N-1]
        M = X[3 * self.model.N-1:]

        jac = self._numeric_jacobian(P, Y, W, M, self.model.population, **self.model.params)

        return jac

    def solve(self, method='hybr', with_jacobian=True, **kwargs):
        """
        Solve the system of non-linear equations describing the equilibrium.

        Parameters
        ----------
        method : str (default='hybr')
            Valid method used to find the root of the non-linear system. See
            scipy.optimize.root for a complete list of valid methods.
        with_jacobian : boolean (default=True)
            Flag indicating whether to used the exact jacobian or a finite
            difference approximation of the exact jacobian.

        Returns
        -------
        result : scipy.optimize.OptimizeResult
            The solution represented as a OptimizeResult object. Important
            attributes are: x the solution array, success a Boolean flag
            indicating if the algorithm exited successfully and message which
            describes the cause of the termination.

        """
        if with_jacobian:
            jacobian = self.jacobian
        else:
            jacobian = False

        # solve for the model equilibrium
        result = optimize.root(self.system,
                               x0=self.initial_guess.guess,
                               jac=jacobian,
                               method=method,
                               **kwargs
                               )
        return result
