

'''
# Numerical Mechanisms
from pydp.algorithms.numerical_mechanisms import NumericalMechanism
from pydp.algorithms.numerical_mechanisms import LaplaceMechanism
from pydp.algorithms.numerical_mechanisms import GaussianMechanism


import statistics 
import numpy as np
import matplotlib.pyplot as plt
'''



import pydp 


class DPStats:

	def __init__(self, epsilon, delta):
		self.epsilon = epsilon
		self.delta = delta


	def BoundedMean(self, data):
		model = pydp.algorithms.laplacian.BoundedMean(self.epsilon, self.delta, data.min(), data.max())
		return model.quick_result(list(data))   # data.mean()

	def BoundedSum(self, data):
		model = pydp.algorithms.laplacian.BoundedSum(self.epsilon, self.delta, data.min(), data.max())
		return model.quick_result(list(data))   # data.sum()

	def BoundedStandardDeviation(self, data):
		model = pydp.algorithms.laplacian.BoundedStandardDeviation(self.epsilon, self.delta, data.min(), data.max())
		return model.quick_result(list(data))   # data.std()

	def BoundedVariance(self, data):
		model = pydp.algorithms.laplacian.BoundedVariance(self.epsilon, self.delta, data.min(), data.max())
		return model.quick_result(list(data))   # data.var()

	def Min(self, data):
		model = pydp.algorithms.laplacian.Min(self.epsilon, self.delta, data.min(), data.max())
		return model.quick_result(list(data))   # data.min()

	def Max(self, data):
		model = pydp.algorithms.laplacian.Max(self.epsilon, self.delta, data.min(), data.max())
		return model.quick_result(list(data))   # data.max()

	def Median(self, data):
		model = pydp.algorithms.laplacian.Median(self.epsilon, self.delta, data.min(), data.max())
		return model.quick_result(list(data))   # data.median()

	def Count(self, data):
		model = pydp.algorithms.laplacian.Count(self.epsilon)
		return model.quick_result(list(data))   # data.count()


	# [TODO] Implement Percentile
	# def Percentile(self, data, percentile):
	# 	model = pydp.algorithms.laplacian.Percentile(self.epsilon, percentile, data.min(), data.max())
	# 	return model.quick_result(list(data))


