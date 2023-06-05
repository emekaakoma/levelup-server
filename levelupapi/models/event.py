from django.db import models

class Event(models.Model):
    description = models.CharField(max_length=155)
    date = models.DateField(auto_now=False, auto_now_add=False)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    organizer = models.ForeignKey('Gamer', on_delete=models.CASCADE, related_name='events')
    attendees = models.ManyToManyField('Gamer', through='Attendee')
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    @property
    def joined(self):
        return self.__joined

    @joined.setter
    def joined(self, value):
        self.__joined = value