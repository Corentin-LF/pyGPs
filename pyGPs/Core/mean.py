#================================================================================
#    Marion Neumann [marion dot neumann at uni-bonn dot de]
#    Daniel Marthaler [dan dot marthaler at gmail dot com]
#    Shan Huang [shan dot huang at iais dot fraunhofer dot de]
#    Kristian Kersting [kristian dot kersting at cs dot tu-dortmund dot de]
#
#    This file is part of pyGPs.
#    The software package is released under the BSD 2-Clause (FreeBSD) License.
#
#    Copyright (c) by
#    Marion Neumann, Daniel Marthaler, Shan Huang & Kristian Kersting, 18/02/2014
#================================================================================

# mean functions to be use by Gaussian process functions. There are two
# different kinds of mean functions: simple and composite:
#
# simple mean functions:
#
#   Zero      - zero mean function
#   One       - one mean function
#   Const     - constant mean function
#   Linear    - linear mean function
#
# composite mean functions:
#
#   ScaleOfMean     - scaled version of a mean function
#   PowerOfMean     - power of a mean function
#   ProductOfMean   - products of mean functions
#   SumOfMean       - sums of mean functions
#
#
# This is a object-oriented python implementation of gpml functionality
# (Copyright (c) by Carl Edward Rasmussen and Hannes Nickisch, 2011-02-18).
# based on the functional-version of python implementation
# (Copyright (c) by Marion Neumann and Daniel Marthaler, 20/05/2013)
#
#
# Copyright (c) by Marion Neumann and Shan Huang, Sep.2013

import numpy as np
#import math


class Mean(object):
    '''
    The base function for mean function
    '''
    def __init__(self):
        super(Mean, self).__init__()
        self.hyp = []
        self.para = []
        self.initial = []
        self.scaled = []

    def __repr__(self):
        strvalue = str(type(self))+': to get the mean vector or mean derviatives use: \n' + \
            'model.meanfunc.getMean()\n' + 'model.meanfunc.getDerMatrix()'
        return strvalue

    # overloading
    def __add__(self, mean):
        '''
        Overloading + operator.

        :param mean: mean function
        :return: an instance of SumOfMean
        '''
        return SumOfMean(self, mean)

    # overloading
    def __mul__(self, other):
        '''
        Overloading * operator.
        Using * for both multiplication with scalar and product of means
        depending on the type of the two objects.

        :param other: mean function as product or int/float as scalar
        :return: an instance of ScaleOfMean or ProductOfMean
        '''
        if isinstance(other, int) or isinstance(other, float):
            return ScaleOfMean(self, other)
        elif isinstance(other, Mean):
            return ProductOfMean(self, other)
        else:
            print "only numbers and Means are allowed for *"

    # overloading
    __rmul__ = __mul__

    # overloading
    def __pow__(self, number):
        '''
        Overloading ** operator.

        :param int number: power of the mean function
        :return: an instance of PowerOfMean
        '''
        if isinstance(number, int) and number > 0:
            return PowerOfMean(self, number)
        else:
            print "only non-zero integers are supported for **"

    def getMean(self, x=None):
        '''
        Get the mean vector based on the inputs.

        :param x: training data
        '''
        pass

    def getDerMatrix(self, x=None, der=None):
        '''
        Compute derivatives wrt. hyperparameters.

        :param x: training inputs
        :param int der: index of hyperparameter whose derivative to be computed

        :return: the corresponding derivative matrix
        '''
        pass


class CompositeMean(Mean):
    def _setHyp(self, hyp):
        assert len(hyp) == len(self._hyp)
        len1 = len(self.mean1.hyp)
        self._hyp = hyp
        self.mean1.hyp = self._hyp[:len1]
        self.mean2.hyp = self._hyp[len1:]

    def _getHyp(self):
        return self._hyp
    hyp = property(_getHyp, _setHyp)

    def _setInitial(self, initial):
        assert len(initial) == len(self._initial)
        len1 = len(self.mean1.initial)
        self._initial = initial
        self.mean1.initial = self._initial[:len1]
        self.mean2.initial = self._initial[len1:]

    def _getInitial(self):
        return self._initial
    initial = property(_getInitial, _setInitial)

    def _setScaled(self, scaled):
        assert len(scaled) == len(self._scaled)
        len1 = len(self.mean1.scaled)
        self._scaled = scaled
        self.mean1.scaled = self._scaled[:len1]
        self.mean2.scaled = self._scaled[len1:]

    def _getScaled(self):
        return self._scaled
    scaled = property(_getScaled, _setScaled)


class ProductOfMean(CompositeMean):
    '''Product of two mean fucntions.'''
    def __init__(self, mean1, mean2):
        self.mean1 = mean1
        self.mean2 = mean2
        if mean1.hyp and mean2.hyp:
            self._hyp = mean1.hyp + mean2.hyp
        elif not mean1.hyp:
            self._hyp = mean2.hyp
        elif not mean2.hyp:
            self._hyp = mean1.hyp

    def getMean(self, x=None):
        A = self.mean1.getMean(x) * self.mean2.getMean(x)
        return A

    def getDerMatrix(self, x=None, der=None):
        if der < len(self.mean1.hyp):
            A = self.mean1.getDerMatrix(x, der) * self.mean2.getMean(x)
        elif der < len(self.hyp):
            der2 = der - len(self.mean1.hyp)
            A = self.mean2.getDerMatrix(x, der2) * self.mean1.getMean(x)
        else:
            raise Exception("Error: der out of range for meanProduct")
        return A


class SumOfMean(CompositeMean):
    '''Sum of two mean functions.'''
    def __init__(self, mean1, mean2):
        self.mean1 = mean1
        self.mean2 = mean2
        if mean1.hyp and mean2.hyp:
            self._hyp = mean1.hyp + mean2.hyp
            self._initial = mean1.initial + mean2.initial
            self._scaled = mean1.scaled + mean2.scaled
        elif not mean1.hyp:
            self._hyp = mean2.hyp
            self._initial = mean2.initial
            self._scaled = mean2.scaled
        elif not mean2.hyp:
            self._hyp = mean1.hyp
            self._initial = mean1.initial
            self._scaled = mean1.scaled

    def getMean(self, x=None):
        A = self.mean1.getMean(x) + self.mean2.getMean(x)
        return A

    def getDerMatrix(self, x=None, der=None):
        if der < len(self.mean1.hyp):
            A = self.mean1.getDerMatrix(x, der)
        elif der < len(self.hyp):
            der2 = der - len(self.mean1.hyp)
            A = self.mean2.getDerMatrix(x, der2)
        else:
            raise Exception("Error: der out of range for meanSum")
        return A


class ScaleOfMean(CompositeMean):
    '''Scale of a mean function.'''
    def __init__(self, mean, scalar):
        self.mean = mean
        if mean.hyp:
            self._hyp = [scalar] + mean.hyp
            self._initial = mean.initial
            self._scaled = mean.scaled
        else:
            self._hyp = [scalar]
            self._initial = []
            self._scaled = []

    def getMean(self, x=None):
        c = self.hyp[0]                          # scale parameter
        A = c * self.mean.getMean(x)             # accumulate means
        return A

    def getDerMatrix(self, x=None, der=None):
        c = self.hyp[0]                          # scale parameter
        if der == 0:                             # compute derivative w.r.t. c
            A = self.mean.getMean(x)
        else:
            A = c * self.mean.getDerMatrix(x, der-1)
        return A


class PowerOfMean(CompositeMean):
    '''Power of a mean fucntion.'''
    def __init__(self, mean, d):
        self.mean = mean
        if mean.hyp:
            self._hyp = [d] + mean.hyp
            self._initial = [-1] + mean.initial
            self._scaled = [] + mean.scaled
        else:
            self._hyp = [d]
            self._initial = []
            self._scaled = []

    def getMean(self, x=None):
        d = np.abs(np.floor(self.hyp[0]))
        d = max(d, 1)
        A = self.mean.getMean(x) ** d              # accumulate means
        return A

    def getDerMatrix(self, x=None, der=None):
        d = np.abs(np.floor(self.hyp[0]))
        d = max(d, 1)
        if der == 0:                             # compute derivative w.r.t. c
            a = self.mean.getMean(x)
            A = a**d * np.log(a)
        else:
            A = d * self.mean.getMean(x) ** (d-1) * self.mean.getDerMatrix(x, der-1)
        return A


class Zero(Mean):
    '''Zero mean.'''
    def __init__(self):
        self.hyp = []
        self.scaled = []
        self.name = '0'

    def getMean(self, x=None):
        n, D = x.shape
        A = np.zeros((n, 1))
        return A

    def getDerMatrix(self, x=None, der=None):
        n, D = x.shape
        A = np.zeros((n, 1))
        return A


class One(Mean):
    ''' One mean.'''
    def __init__(self):
        self.hyp = []
        self.name = '1'
        self.scaled = []

    def getMean(self, x=None):
        n, D = x.shape
        A = np.ones((n, 1))
        return A

    def getDerMatrix(self, x=None, der=None):
        n, D = x.shape
        A = np.zeros((n, 1))
        return A


class Const(Mean):
    '''
    Constant mean function. hyp = [c]

    :param c: constant value for mean
    '''

    def __init__(self, c=5.):
        self.hyp = [c]
        self.initial = [-1]  # output scale
        self.scaled = []

    def getMean(self, x=None):
        n, D = x.shape
        A = self.hyp[0] * np.ones((n, 1))
        return A

    def getDerMatrix(self, x=None, der=None):
        n, D = x.shape
        if der == 0:                  # compute derivative vector wrt c
            A = np.ones((n, 1))
        else:
            A = np.zeros((n, 1))
        return A


class Linear(Mean):
    '''
    Linear mean function. self.hyp = alpha_list

    :param D: dimension of training data. Set if you want default alpha, which is 0.5 for each dimension.
    :alpha_list: scalar alpha for each dimension
    '''

    def __init__(self, D=None, alpha_list=None):
        if alpha_list is None:
            if D is None:
                self.hyp = [0.5]
                self.initial = [0]  # Scale of input variable
            else:
                self.hyp = [0.5 for i in xrange(D)]
                self.initial = [i for i in range(D)]  # Scale of appropriate input
        else:
            self.hyp = alpha_list
            self.initial = [i for i in range(D)]  # Scale of appropriate input

        self.scaled = []

    def getMean(self, x=None):
        n, D = x.shape
        c = np.array(self.hyp)
        c = np.reshape(c, (len(c), 1))
        A = np.dot(x, c)
        return A

    def getDerMatrix(self, x=None, der=None):
        n, D = x.shape
        c = np.array(self.hyp)
        c = np.reshape(c, (len(c), 1))
        if isinstance(der, int) and der < D:     # compute derivative vector wrt meanparameters
            A = np.reshape(x[:, der], (len(x[:, der]), 1) )
        else:
            A = np.zeros((n, 1))
        return A


if __name__ == '__main__':
    pass
