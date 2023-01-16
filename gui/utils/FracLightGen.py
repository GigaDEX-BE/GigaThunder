import numpy as np
import random

# params
base_time = 1
scale = 2
num_scales = 4
periods = [base_time*(scale**i) for i in range(num_scales)]
reversal_prob = 0.6


# do some change when each thing mods
class FracLightGen:

    def __init__(self, price=60., floor=56., ceiling=72.):
        self.floor = floor
        self.ceiling = ceiling
        self.x = price
        self.delta = np.random.normal()
        self.is_up = [random.random() > 0 for i in range(len(periods))]
        self.i = 0

    def next(self):
        self.i += 1
        self.x += self.delta
        for j, p in enumerate(periods):
            if self.i % p == 0:
                if random.random() < reversal_prob:
                    self.is_up[j] = not self.is_up[j]
        for up, p in zip(self.is_up, periods):
            if up:
                self.x += (abs(np.random.normal()) * p)
            else:
                self.x -= (abs(np.random.normal()) * p)

        # bounce on limits
        if self.x < self.floor:
            self.is_up[-1] = True
        if self.x > self.ceiling:
            self.is_up[-1] = False

        return int(self.x)




