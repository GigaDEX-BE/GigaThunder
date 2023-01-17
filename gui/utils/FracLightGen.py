import numpy as np
import random

# params
base_time = 1
scale = 2
num_scales = 4
periods = [base_time*(scale**i) for i in range(num_scales)]
narrower = 0.10



# do some change when each thing mods
class FracLightGen:

    def __init__(self, price=60., floor=56., ceiling=72.):
        self.floor = floor
        self.ceiling = ceiling
        self.x = price
        self.is_up = [random.random() > 0 for i in range(len(periods))]
        self.i = 0

    def next(self):

        spread = self.ceiling - self.floor
        margin = spread * 0.2
        _floor = self.floor + margin
        _ceiling = self.ceiling - margin
        dist_from_bottom = (self.x - _floor) / (_ceiling - _floor)
        if dist_from_bottom > 0.5:
            up_to_down_prob = (dist_from_bottom - 0.5) * 2
            down_to_up_prob = 1 - up_to_down_prob
        else:
            down_to_up_prob = (0.5 - dist_from_bottom) * 2
            up_to_down_prob = 1 - down_to_up_prob

        self.i += 1
        for j, p in enumerate(periods):
            if self.i % p == 0:
                reversal_prob = up_to_down_prob if self.is_up[j] else down_to_up_prob
                if random.random() < reversal_prob:
                    self.is_up[j] = not self.is_up[j]
        for up, p in zip(self.is_up, periods):
            if up:
                self.x += (abs(np.random.normal(scale=narrower)) * p)
            else:
                self.x -= (abs(np.random.normal(scale=narrower)) * p)

        # bounce on limits
        if self.x < _floor:
            self.is_up[-1] = True
        if self.x > _ceiling:
            self.is_up[-1] = False

        return int(self.x)




