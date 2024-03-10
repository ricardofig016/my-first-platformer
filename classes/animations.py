class Animation:
    def __init__(self, images, img_duration=5, loop=True) -> None:
        self.images = images
        self.img_duration = img_duration
        self.loop = loop
        self.done = False
        self.frame = 0  # refers to frames of the game

    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)

    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True

    def img(self):
        return self.images[int(self.frame / self.img_duration)]
