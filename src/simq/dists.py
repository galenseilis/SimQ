from abc import ABC, abstractmethod
import numpy as np

# Abstract base class for distributions
class Distribution(ABC):
    @abstractmethod
    def sample(self, queue):
        pass


# Exponential distribution class
class Exponential(Distribution):
    def __init__(self, rate):
        self.rate = rate

    def sample(self, queue):
        return np.random.exponential(1 / self.rate)


# Normal distribution class
class Normal(Distribution):
    def __init__(self, mean, stddev):
        self.mean = mean
        self.stddev = stddev

    def sample(self, queue):
        return np.random.normal(self.mean, self.stddev)
