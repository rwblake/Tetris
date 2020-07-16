"""contains Game class for tetris window"""


import numpy as np
import tkinter as tk


import tetrimino as ttr


class Game:
	"""handles the game window where the game is played and coordinates
	the game"""

	size = [10, 20]  # tetris window size in blocks
	speed_ms = 300  # time between falling blocks
	scoring = {0: 0, 1: 100, 2: 400, 3: 900, 4:2000}
	grid_size = 32  # pixels to 1 block (multiplied by self.scale)

	def __init__(self, parent, scale):
		"""create tkinter canvas objects for game"""

		self.parent = parent
		self.scale = scale

		self.canvas = tk.Canvas(self.parent, width=self.size[0] * self.grid_size * self.scale, height=self.size[1] * self.grid_size * self.scale, bg='black', highlightthickness=0)
		self.canvas.pack()
		self.score_text = self.canvas.create_text(self.size[0]*32*self.scale, 0, anchor='ne', text='', fill='white')

	def start(self):
		"""reset variables, bind keys and start game loop"""

		self.end = False
		self.score = 0
		self.soft_lines = 0

		self.grid = np.zeros(self.size, dtype=bool)
		self.static_blocks = np.empty(self.size, dtype=int)
		self.squares = 0
		self.t = ttr.Tetrimino.random(self.grid)
		self.t_drawn = self.draw_ttr(self.t)

		self.parent.bind('<Key>', self.callback)
		self.parent.after(self.speed_ms, self.loop)

	def callback(self, event):
		"""handles keypresses when bound"""

		if self.end:
			self.parent.unbind('All')
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
			self.soft_lines += 1
			if self.t.locked:
				self.new_ttr()
				if self.t.locked:
					self.end = True
		elif key == 'space':
			while not self.t.locked:
				self.t.fall()
				self.soft_lines += 1
			self.redraw()
			self.new_ttr()
			if self.t.locked:
				self.end = True

	def square(self, pos, colour):
		"""creates and returns a square on canvas"""

		return self.canvas.create_rectangle(pos[0]*self.grid_size*self.scale, pos[1]*self.grid_size*self.scale, pos[0]*self.grid_size*self.scale+self.grid_size*self.scale, pos[1]*self.grid_size*self.scale+self.grid_size*self.scale, fill=colour)

	def draw_ttr(self, ttr):
		"""creates and returns list of squares for drawn tetrimino"""

		drawn = []
		for pos in ttr.positions:
			drawn.append(self.square(pos, ttr.colour))
		return drawn

	def redraw(self):
		"""redraws current tetrimino to current position"""

		for part in self.t_drawn:
			self.canvas.delete(part)
		self.t_drawn = self.draw_ttr(self.t)

	def full_row(self):
		"""returns a row number if a row is filled"""

		grid = np.copy(self.grid)
		grid = np.swapaxes(grid, 0, 1)
		for i, row in enumerate(grid):
			for item in row:
				if not item:
					break
			else:
				return i

	def delete_and_shift(self, row):
		"""delete specified row and move rows above down by 1"""

		for i in range(self.size[0]):
			if self.grid[i, row]:
				self.canvas.delete(self.static_blocks[i, row])
				self.static_blocks[i, row] = 99999
				self.grid[i, row] = False
				self.squares -= 1
		for y in range(row - 1, 0, -1):  # loop over previous rows
			for x in range(self.size[0]):
				if self.grid[x, y]:
					obj_idx = self.static_blocks[x, y]
					self.canvas.move(obj_idx, 0, self.grid_size * self.scale)
					self.static_blocks[x, y + 1] = obj_idx
					self.grid[x, y] = False
					self.grid[x, y + 1] = True

	def new_ttr(self):
		"""delets previous tetrimino, and creates a new one"""

		# create new ttr
		for pos, t in zip(self.t.positions, self.t_drawn):
			self.grid[tuple(pos)] = True
			self.static_blocks[tuple(pos)] = t
			self.squares += 1
		self.t = ttr.Tetrimino.random(self.grid)
		self.t_drawn = []

		# check for filled rows and shift
		row = self.full_row()
		lines = 0
		while row is not None:  # if full row found
			self.delete_and_shift(row)
			lines += 1
			row = self.full_row()

		# scoring
		added_score = self.soft_lines + self.scoring[lines]
		if self.squares == 0:
			added_score *= 10
		self.score += added_score

		self.canvas.itemconfig(self.score_text, text=str(self.score))

	def loop(self):
		"""main game loop, run when blocks fall"""

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


def main():
	"""creates a simple tetris window and starts tkinter event loop"""

	scale = 1
	root = tk.Tk()

	game = Game(root, scale)
	game.start()
	root.mainloop()


if __name__ == '__main__':
	main()
