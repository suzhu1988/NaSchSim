import pyglet
import time
from random import randint, choice
from pyglet.graphics import *

roadlength = 300        #number of tiles on the road
maxcars = 30
breaktime = 0.1         #number of seconds to wait after each cycle
slowprob = 33           #probability of velocity reduction

config = gl.Config(double_buffer=True)
window = pyglet.window.Window(1280, 20, config = config) #window size
w,h = window.get_size()
tw, th = w/roadlength, h
road = []
lock = thread.allocate_lock()


class Color(object):
    ACC = (0, 255.0, 0)
    DRIVE = (0, 0, 255.0)
    SLOW = (255.0, 255.0, 0)
    BREAK = (255.0, 0, 0)


class Car(object):
    cars = []
    def __init__(   self, pos = 0, cur_speed = 0, max_speed = 6,
                    color = Color.ACC):
        self.pos = pos
        self.cur_speed = cur_speed
        self.max_speed = max_speed
        self.color = Color.ACC
        self.moved = False
        self.id = len(cars)
        Car.cars.append(self)

    def __repr__(self):
        return "Car"+str(self.id)

class Slow(Car):
    def __init__(self):
        super(Slow, self).__init__(cur_speed = 0, max_speed = 4)

@window.event
def on_draw():
    lock.acquire()
    gl.glClear(GL_COLOR_BUFFER_BIT)
    batch = Batch()
    for i, c in enumerate(road):
        if c is None:
            continue
        p1 = tw*i, 0
        p2 = p1[0]+tw, p1[1]
        p3 = p1[0]+tw, p1[1]+th
        p4 = p1[0], p1[1]+th

        vertex_list = batch.add(
            4, pyglet.gl.GL_QUADS, None,
            ('v2f', (p1+p2+p3+p4)),
            ('c3f', (c.color+c.color+c.color+c.color))
        )
    batch.draw()
    lock.release()

def run(bloat):
    lock.acquire()
    for car in Car.cars:
        car.moved = False
    cycle()
    if road[0] is None and len(Car.cars) < maxcars:
        road[0] = choice([Car, Slow])()
    lock.release()
    time.sleep(breaktime)

def cycle():
    for car in road:
        if car is None or car.moved:
            continue
        else:
            car.moved = True

        if car.cur_speed < car.max_speed:
            car.cur_speed += 1
            car.color = Color.ACC
        else:
            car.color = Color.DRIVE

        upcoming = enumerate(road[car.pos+1:car.pos+car.cur_speed+1])
        for d, field in upcoming:
            if field is not None:
                car.cur_speed = d
                car.color = Color.BREAK

        if car.cur_speed > 0 and randint(0,100) < slowprob:
            car.cur_speed -= 1
            car.color = Color.SLOW

        road[car.pos] = None
        car.pos += car.cur_speed
        if car.pos > len(road)-1:
            Car.cars.remove(car)
        else:
            road[car.pos] = car



if __name__ == "__main__":
    cars = [Car, Slow]
    for i in range(roadlength):
        road.append(None)

    pyglet.clock.schedule_interval(run, 1/10.0)
    pyglet.app.run()

