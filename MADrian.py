import random

from datetime import datetime

import numpy
import pyglet

from pyglet.gl import *

ZOOM = 9
SQUARE_SIZE = 13*ZOOM
LINE_WIDTH = 0*ZOOM
GRID_COLOR = (0, 0, 0, 255)
OFFSET = SQUARE_SIZE+LINE_WIDTH
MIN_LINES = 3*ZOOM
MAX_LINES = 7*ZOOM


def get_gridsize():
    return 11*LINE_WIDTH+10*SQUARE_SIZE


def get_winsize():
    return (2*(get_gridsize())+OFFSET, get_gridsize())


def get_grid_data(size):
    height = size[0]
    width = size[1]
    return ('v2f',
           (0, 0, 0, height,
            0, height, width, height,
            width, height, width, 0,
            width, 0, 0, 0,
            ))


def cell_value(cells, x, y):
    try:
        return cells[x][y]
    except:
        return 0


def get_virgin_cells(x=10, y=10):
    return numpy.zeros((x, y), numpy.int)


def get_seed_cells(x=10, y=10):
    return numpy.random.random_integers(0, 1, size=(x, y))


def count_neighbours(cells, x, y):
    neighbours = cell_value(cells, x-1, y-1) \
                            + cell_value(cells, x, y-1) \
                            + cell_value(cells, x+1, y-1) \
                            + cell_value(cells, x-1, y) \
                            + cell_value(cells, x+1, y) \
                            + cell_value(cells, x-1, y+1) \
                            + cell_value(cells, x, y+1) \
                            + cell_value(cells, x+1, y+1)
    return neighbours


def conway_routine(cells):
    shape = len(cells), len(cells[0])

    nbours = numpy.zeros(shape, numpy.int)
    for x in range(shape[0]):
        for y in range(shape[1]):
            nbours[x][y] = count_neighbours(cells, x, y)

    newcells = numpy.zeros(shape, numpy.int)
    for x in range(shape[0]):
        for y in range(shape[1]):
            if nbours[x][y] == 3:
                newcells[x][y] = 1
            elif nbours[x][y] == 2 and cells[x][y] == 1:
                newcells[x][y] = 1

    return newcells


def mad_vertexes(x, y, offset=0):
    gridsize = get_gridsize()
    if random.getrandbits(1):
        if random.getrandbits(1):
            return ('v2f', (x*OFFSET+SQUARE_SIZE+offset, y*OFFSET,
                            x*OFFSET+SQUARE_SIZE+offset, y*OFFSET+gridsize,
                            x*OFFSET+SQUARE_SIZE+ZOOM+offset, y*OFFSET+gridsize,
                            x*OFFSET+SQUARE_SIZE+ZOOM+offset, y*OFFSET,
                            ))
        else:
            return ('v2f', (x*OFFSET+SQUARE_SIZE+offset, y*OFFSET,
                            x*OFFSET+SQUARE_SIZE+offset, 0,
                            x*OFFSET+SQUARE_SIZE+ZOOM+offset, 0,
                            x*OFFSET+SQUARE_SIZE+ZOOM+offset, y*OFFSET,
                            ))
    else:
        if random.getrandbits(1):
            return ('v2f', (x*OFFSET+SQUARE_SIZE+offset, y*OFFSET,
                            x*OFFSET+SQUARE_SIZE+gridsize+offset, y*OFFSET,
                            x*OFFSET+SQUARE_SIZE+gridsize+offset, y*OFFSET+ZOOM,
                            x*OFFSET+SQUARE_SIZE+offset, y*OFFSET+ZOOM,
                            ))
        else:
            return ('v2f', (x*OFFSET+SQUARE_SIZE+offset, y*OFFSET,
                            0, y*OFFSET,
                            0, y*OFFSET+ZOOM,
                            x*OFFSET+SQUARE_SIZE+offset, y*OFFSET+ZOOM,
                            ))


class AntedeluvianWindow(pyglet.window.Window):
    def __init__(self):
        winsize = get_winsize()
        super(AntedeluvianWindow, self).__init__(winsize[0], winsize[1],
                                                 style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS,
                                                 resizable=False,
                                                 )
        self.set_location(-winsize[0]//(ZOOM*2), -winsize[1]//(ZOOM*2))

        self.cells_data = get_virgin_cells()
        self.cells_batch = pyglet.graphics.Batch()

        self.tcells_data = get_virgin_cells()
        self.tcells_batch = pyglet.graphics.Batch()

        self.ncells_data = get_virgin_cells()
        self.ncells_batch = pyglet.graphics.Batch()

        self.qcells_data = get_virgin_cells()
        self.qcells_batch = pyglet.graphics.Batch()

        self.lines_data = list()
        self.lines_batch = pyglet.graphics.Batch()

    def update_caption(self):
        ints = int(''.join([str(k) for k in self.cells_data.flatten()]) \
                   + ''.join([str(k) for k in self.tcells_data.flatten()]) \
                   + ''.join([str(k) for k in self.ncells_data.flatten()]) \
                   + ''.join([str(k) for k in self.qcells_data.flatten()]),
                   2)
        self.set_caption('{}'.format(ints))

    def gen_cells_batch(self, cells_data, color, offset=0):
        cells_batch = pyglet.graphics.Batch()
        for y in range(10):
            for x in range(10):
                if cells_data[y][x] == 1:
                    cells_batch.add(4,
                                    pyglet.gl.GL_QUADS, None,
                                   ('v2f', (x*OFFSET+LINE_WIDTH+offset, y*OFFSET+LINE_WIDTH,
                                            x*OFFSET+LINE_WIDTH+SQUARE_SIZE+offset, y*OFFSET+LINE_WIDTH,
                                            x*OFFSET+LINE_WIDTH+SQUARE_SIZE+offset, y*OFFSET+LINE_WIDTH+SQUARE_SIZE,
                                            x*OFFSET+LINE_WIDTH+offset, y*OFFSET+LINE_WIDTH+SQUARE_SIZE,
                                            )),
                                   ('c4B', (color*4)),
                                   )
        return cells_batch

    def regen_cells_batches(self):
        self.cells_batch = self.gen_cells_batch(self.cells_data,
                                                color=(255, 255, 0, 255))
        self.tcells_batch = self.gen_cells_batch(self.tcells_data,
                                                 color=(0, 0, 0, 255),
                                                 offset=get_gridsize())
        self.ncells_batch = self.gen_cells_batch(self.ncells_data,
                                                 color=(255, 0, 0, 255),
                                                 offset=int(get_gridsize()/2))
        self.qcells_batch = self.gen_cells_batch(self.qcells_data,
                                                 color=(0, 0, 255, 255),
                                                 offset=int(get_gridsize()/2))

    def cells_data_update(self, cells_data):
        virgin = get_virgin_cells(len(cells_data[0]), len(cells_data))
        if numpy.array_equal(virgin, cells_data):
            cells_data = get_seed_cells()
        else:
            old_cells = cells_data
            cells_data = conway_routine(cells_data)
            if numpy.array_equal(old_cells, cells_data):
                cells_data = virgin
        return cells_data
        
    def cells_update(self):
        self.cells_data = self.cells_data_update(self.cells_data)
        self.tcells_data = self.cells_data_update(self.tcells_data)
        self.ncells_data = self.cells_data_update(self.ncells_data)
        self.qcells_data = self.cells_data_update(self.qcells_data)

        self.regen_cells_batches()

    def lines_data_update(self, lines_data):
        gridsize = get_gridsize()
        if len(self.lines_data) > MIN_LINES:
            for k in range(ZOOM):
                lines_data.pop()

        for y in range(10):
            for x in range(10):
                if self.ncells_data[y][x] == 1 and self.cells_data[y][x] == 1:
                    lines_data.append(mad_vertexes(x, y))

                if self.ncells_data[y][x] == 1 and self.tcells_data[y][x] == 1:
                    lines_data.append(mad_vertexes(x, y, offset=gridsize))

                if count_neighbours(self.ncells_data, x, y)>3 and count_neighbours(self.cells_data, x, y)>3:
                    lines_data.append(mad_vertexes(x, y))

                if count_neighbours(self.ncells_data, x, y)>3 and count_neighbours(self.tcells_data, x, y)>3:
                    lines_data.append(mad_vertexes(x, y, offset=gridsize))
                    
                if self.qcells_data[y][x] == 1 and self.cells_data[y][x] == 1:
                    lines_data.append(mad_vertexes(x, y))

                if self.qcells_data[y][x] == 1 and self.tcells_data[y][x] == 1:
                    lines_data.append(mad_vertexes(x, y, offset=gridsize))

                if count_neighbours(self.qcells_data, x, y)>3 and count_neighbours(self.cells_data, x, y)>3:
                    lines_data.append(mad_vertexes(x, y))

                if count_neighbours(self.qcells_data, x, y)>3 and count_neighbours(self.tcells_data, x, y)>3:
                    lines_data.append(mad_vertexes(x, y, offset=gridsize))

        if len(self.lines_data) > MAX_LINES:
            lines_data = random.choices(self.lines_data, k=MAX_LINES)

        return lines_data

    def gen_lines_batch(self, color=GRID_COLOR):
        batch = pyglet.graphics.Batch()
        for k in self.lines_data:
            batch.add(4, pyglet.gl.GL_QUADS, None, k, ('c4B', (color*4)))

        return batch

    def lines_update(self):
        self.lines_data = self.lines_data_update(self.lines_data)
        self.lines_batch = self.gen_lines_batch()

    def art_update(self, dt):
        self.cells_update()
        self.lines_update()

    def reinit(self, dt, cells):
        if cells == 'cells':
            self.cells_data = get_virgin_cells()
        elif cells == 'tcells':
            self.tcells_data = get_virgin_cells()
        elif cells == 'ncells':
            self.ncells_data = get_virgin_cells()
        elif cells == 'qcells':
            self.qcells_data = get_virgin_cells()

    def on_draw(self):
        self.update_caption()
        pyglet.gl.glClearColor(1, 1, 1, 1)
        self.clear()
        self.qcells_batch.draw()
        self.cells_batch.draw()
        self.ncells_batch.draw()
        self.tcells_batch.draw()
        self.lines_batch.draw()


if __name__ == '__main__':
    random.seed(datetime.now())
    window = AntedeluvianWindow()
    pyglet.clock.schedule_interval(window.art_update, 0.3)
    pyglet.clock.schedule_interval(window.reinit, 15, cells='cells')
    pyglet.clock.schedule_interval(window.reinit, 20, cells='tcells')
    pyglet.clock.schedule_interval(window.reinit, 5, cells='ncells')
    pyglet.clock.schedule_interval(window.reinit, 10, cells='qcells')
    pyglet.app.run()
