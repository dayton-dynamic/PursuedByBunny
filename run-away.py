import math
import random

import ppb
import ppb.events as events

# bush: https://opengameart.org/content/simple-bush-2d


BOUND_HORIZ = 6.2
BOUND_VERT = 4.65 


def _rand_posneg_float_up_to(maxval):
    return (random.random() - 0.5) * (maxval * 2)

def _random_pos(horiz_bound, neg_bound):
    return ppb.Vector(_rand_posneg_float_up_to(horiz_bound),
        _rand_posneg_float_up_to(neg_bound))

def could_be_anywhere():
    return _random_pos(BOUND_HORIZ, BOUND_VERT)



class Knight(ppb.Sprite):
    speed = 1.2 
    MEANDER_SPEED = 0.01
    dead = False

    def __init__(self, *arg, **kwarg):
        result = super().__init__(*arg, **kwarg)
        self.position = _random_pos(1, 1)
        self.target = ppb.Vector(BOUND_HORIZ + 0.01, _rand_posneg_float_up_to(BOUND_VERT)  )
        return result

    def escaped(self, scene):
        scene.remove(self)
        for rabbit in scene.get(kind=Rabbit):
            rabbit.gives_up_on(self)

    def meander(self, panic_level=1):
        self.target = ppb.Vector(self.target.x, self.target.y + _rand_posneg_float_up_to(self.MEANDER_SPEED + panic_level))


    def on_update(self, event: events.Update, signal):
        if self.dead:
            return
        if (abs(self.position.x) >= BOUND_HORIZ) or (abs(self.position.y) > BOUND_VERT):
            self.escaped(event.scene)
        intent_vector = self.target - self.position
        if intent_vector:
            self.rotation = math.degrees(math.atan2(intent_vector.y, intent_vector.x)) # - 90
            if self.hits_obstacle(self.position, event.scene):
                speed = self.speed / 3.0 
            else:
                speed = self.speed
            self.position += intent_vector.scale(speed * event.time_delta)
        self.meander()

    def hits_obstacle(self, desired_position, scene):
        for shrubbery in scene.get(kind=Shrubbery):
            if (shrubbery.position - (self.position)).length < (shrubbery.size / 2):
                return True
        return False



class Shrubbery(ppb.Sprite):

    def __init__(self, *arg, **kwarg):
        result = super().__init__(*arg, **kwarg)
        self.position = could_be_anywhere() 
        return result

class ObstacleField:

    N_OBSTACLES = 20 

    def _rand_posneg_float_up_to(self, maxval):
        return (random.random() - 0.5) * (maxval * 2)

    def random_pos(self):
        return ppb.Vector( self._rand_posneg_float_up_to(BOUND_HORIZ),
            self._rand_posneg_float_up_to(BOUND_VERT))


    def __init__(self, scene):

        for n in range(self.N_OBSTACLES):
            scene.add(Shrubbery())



class Player(Knight):

    def on_mouse_motion(self, event: events.MouseMotion, signal):
        print(event.position)
        self.target = event.position

    def meander(self, panic_level=None):
        pass  


class Rabbit(ppb.Sprite):
    target = None 
    speed = 2
    position = (-3, 0)


    def pick_target(self, event):
        for sprite in event.scene.get(kind=Knight):
            if not sprite.dead:
                return sprite

    def gives_up_on(self, knight):
        if self.target == self:
            self.target = pick_target()


    def kill(self, event, knight):
        knight.dead = True 
        knight.image = ppb.Image('splat.png')
        self.target = self.pick_target(event)


    def on_update(self, event: events.Update, signal):
        if not self.target:
            self.target = self.pick_target(event)
            if not self.target:
                return  # everyone is dead

        intent_vector = self.target.position - self.position
        if intent_vector.length < (self.size * 0.5):
            self.kill(event, self.target)
            return
        if intent_vector:
            self.position += intent_vector.scale(self.speed * event.time_delta)
            self.rotation = math.degrees(math.atan2(intent_vector.y, intent_vector.x)) # - 90


def setup(scene):
    scene.add(Rabbit())
    scene.add(Player())
    for n in range(6):
        scene.add(Knight())
    field = ObstacleField(scene)


ppb.run(setup)
