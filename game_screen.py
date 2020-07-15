

import numpy as np
import tkinter as tk


import tetrimino as ttr


class Game:
	size = [10, 20]
	speed_ms = 300

	def __init__(self, parent, scale):
		self.parent = parent
		self.scale = scale

		self.grid = np.zeros(self.size, dtype=bool)
		self.canvas = tk.Canvas(self.parent, width=self.size[0] * 32 * self.scale, height=self.size[1] * 32 * self.scale, bg='black', highlightthickness=0)
		self.canvas.pack()
		self.end = False

		self.static_blocks = np.empty(self.size, dtype=int)

		self.t = ttr.random_tetrimino(self.grid)
		self.t_drawn = self.draw_ttr(self.t)

		self.parent.bind('<Key>', self.callback)
		self.parent.after(self.speed_ms, self.loop)

	def callback(self, event):
		if self.end:
			return

		key = event.keysym
		if key == 'Up':
			self.t.rotate()
			self.redraw()
		elif key == 'Left':
			self.t.move('left')
			self.redraw()
		elif key == 'Right':
			self.t.move('right')
			self.redraw()
		elif key == 'Down':
			self.t.fall()
			self.redraw()
			if self.t.locked:
				self.new_ttr()
				if self.t.locked:
					self.end = True

	def square(self, pos, colour):
		return self.canvas.create_rectangle(pos[0]*32*self.scale, pos[1]*32*self.scale, pos[0]*32*self.scale+32*self.scale, pos[1]*32*self.scale+32*self.scale, fill=colour)

	def draw_ttr(self, ttr):
		drawn = []
		for pos in ttr.positions:
			drawn.append(self.square(pos, ttr.colour))
		return drawn

	def redraw(self):
		for part in self.t_drawn:
			self.canvas.delete(part)
		self.t_drawn = self.draw_ttr(self.t)

	def full_row(self):
		grid = np.copy(self.grid)
		grid = np.swapaxes(grid, 0, 1)
		for i, row in enumerate(grid):
			for item in row:
				if not item:
					break
			else:
				return i

	def delete_and_shift(self, row):
		for i in range(self.size[0]):
			if self.grid[i, row]:
				self.canvas.delete(self.static_blocks[i, row])
				self.static_blocks[i, row] = 99999
				self.grid[i, row] = False
		for y in range(row - 1, 0, -1):
			for x in range(self.size[0]):
				if self.grid[x, y]:
					obj_idx = self.static_blocks[x, y]
					self.canvas.move(obj_idx, 0, 32 * self.scale)
					self.static_blocks[x, y + 1] = obj_idx
					self.grid[x, y] = False
					self.grid[x, y + 1] = True

	def new_ttr(self):
		for pos, t in zip(self.t.positions, self.t_drawn):
			self.grid[tuple(pos)] = True
			self.static_blocks[tuple(pos)] = t
		self.t = ttr.random_tetrimino(self.grid)
		self.t_drawn = []

		row = self.full_row()
		while row is not None:
			self.delete_and_shift(row)
			row = self.full_row()

	def loop(self):
		if self.end:
			return

		self.t.fall()

		self.redraw()

		if self.t.locked:
			self.new_ttr()
			if self.t.locked:
				self.end = True
				return
			self.redraw()
			self.loop()
		elif not self.end:
			self.parent.after(self.speed_ms, self.loop)


if __name__ == '__main__':
	scale = 1.0
	root = tk.Tk()

	game = Game(root, scale)
	root.mainloop()
