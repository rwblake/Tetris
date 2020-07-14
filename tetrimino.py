

import numpy as np
import random


TETRIMINOES = {
	'square':  [2, np.array([[0, 0], [0, 1], [1, 0], [1, 1]]), 'yellow'],
	'line':    [4, np.array([[0, 3], [1, 3], [2, 3], [3, 3]]), 'cyan'],
	't':       [3, np.array([[0, 2], [1, 2], [2, 2], [1, 1]]), 'purple'],
	'left_l':  [3, np.array([[0, 2], [1, 2], [2, 2], [0, 1]]), 'blue'],
	'right_l': [3, np.array([[0, 2], [1, 2], [2, 2], [2, 1]]), 'orange'],
	'left_z':  [3, np.array([[0, 1], [1, 1], [1, 2], [2, 2]]), 'red'],
	'right_z': [3, np.array([[0, 2], [1, 2], [1, 1], [2, 1]]), 'green']
}


class Tetrimino:
	
	def __init__(self, size, shape, colour, grid):
		self.size = size
		self.shape = shape
		self.colour = colour
		self.grid = grid

		self.locked = False
		self.pos = np.array([4, 0])
		self.centre = np.array([self.pos[0] + self.size/2, self.pos[1] + self.size / 2])

	def occupied(self, shape):
		for point in shape:
			if self.grid[point]:
				return True
		else:
			return False

	def rotate(self):
		if self.locked:
			return

		rel_shape = [point - self.centre for point in self.shape]
		rot_mtx  = np.array([[0, 1], [-1, 0]])
		new_shape = np.dot(rel_shape, rot_mtx)

		shape = new_shape + self.centre + self.pos
		if not self.occupied(shape):
			self.shape = shape

	def fall(self):
		if self.locked:
			return

		shape = self.shape + np.array([0, 1]) + self.pos
		if self.occupied(shape):
			self.locked = True
		else:
			self.pos = self.pos + np.array([0, 1])

	def move(self, direction):
		if direction == 'left':
			delta = np.array([-1, 0])
		elif direction == 'right':
			delta = np.array([1, 0])
		else:
			raise ValueError(f'should be left or right, not {direction}')

		shape = self.shape + delta + self.pos
		if not self.occupied(shape):
			self.pos = self.pos + delta


def random_tetrimino(grid):
	args = random.choice(TETRIMINOES.values)
	args.append(grid)
	return Tetrimino(*args)
