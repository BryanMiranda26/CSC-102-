'''
class Room:
    def __init__(self, name):
        self.name = name
        self.description = ""

        # room exits
        self.exits = []  # list of exit names like ["north", "east"]
        self.exit_locations = []  # list of Room objects the exits lead to

        # room actions
        self.actions = []  # list of actions available
        self.action_results = []  # results of each action

    # ----- Add exit -----
    def add_exit(self, exit_name, room):
        """Add an exit and the room it leads to"""
        self.exits.append(exit_name)
        self.exit_locations.append(room)

    # ----- Add action -----
    def add_action(self, action_name, result):
        """Add an action and the result of that action"""
        self.actions.append(action_name)
        self.action_results.append(result)

    # ----- Getters -----
    @property
    def room_name(self):
        return self.name
    @room_name.setter
    def name(self, value):
        self.name = value

    @property
    def description(self):
        return self.description

    @description.setter
    def description(self, value):
        self.description = value

'''
from pygame.examples.cursors import image
#room class and inform

from tkinter import *
class Room:
    def __init__(self, name,image):
        self.name = name
        self.description = ""
        self._image = image
        self.exits = []
        self.exit_locations = []

        @property
        def name(self):
            return self.name

        @name.setter
        def name(self, value):
            self.name = value

        @property
        def description(self):
            return self.description

        @description.setter
        def description(self, value):
            self.description = value

        @property
        def image(self):
            return self._image

        @image.setter
        def image(self, value):
            self._image = value

        @property
        def exits(self):
            return self.exits

        @exits.setter
        def exits(self, value):
            self.exits = value

        @property
        def exit_locations(self):
            return self.exit_locations

        @exit_locations.setter
        def exit_locations(self, value):
            self.exit_locations = value


#proptires of the room

    name = property(lambda self: self.name)
    descrption = property(lambda self: self.description)
    image = property(lambda self: self.image)
    exits = property(lambda self: self.exits)
    exit_locations = property(lambda self: self.exit_locations)



    def add_exit(self, exit_name, room):
        """Add an exit and the room it leads to"""
        self.exits.append(exit_name)
        self.exit_locations.append(room)



#room descprtion and name
    def __str__(self):
        s = f"{self.name}\n"
        s += f"{self.description}\n"
        s += "Exits: "
# how they exit
        if len(self.exits) == 0:
            s += "None"
        else:
            s += ", ".join(self.exits)

        return s
## gmae info
class Game(Frame):
    def __init__(self, master):

        Frame.__init__(self, master)

        def createRoom(self):

            Game.room = []











