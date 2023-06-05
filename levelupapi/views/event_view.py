"""View module for handling requests about game types"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Gamer, Game
from rest_framework.decorators import action
from django.db.models import Count
from django.db.models import Q
from django.core.exceptions import ValidationError



class EventView(ViewSet):
    """Level up game types view"""

    def retrieve(self, request, pk):
        """Handle GET requests for single game type

        Returns:
            Response -- JSON serialized game type
        """
        event = Event.objects.get(pk=pk)
        serializer = EventSerializer(event)
        return Response(serializer.data)

    def list(self, request):
        """Handle GET requests to get all game types

        Returns:
            Response -- JSON serialized list of game types
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        events = Event.objects.all()
        events = Event.objects.annotate(attendee_count=Count('attendee'),
            joined=Count(
                'attendees',
                filter=Q(attendees=gamer)))
        serializer = EventSerializer(events, many=True)

        # # Set the `joined` property on every event
        # for event in events:
        #     # Check to see if the gamer is in the attendees list on the event
        #     gamer = Gamer.objects.get(user=request.auth.user)
        #     event.joined = gamer in event.attendees.all()

        return Response(serializer.data)

    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized game instance
        """
        gamer = Gamer.objects.get(user=request.auth.user)
        serializer = CreateEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(gamer=gamer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for a game

        Returns:
            Response -- Empty body with 204 status code
        """

        event=Event.objects.get(pk=pk)
        event.description=request.data["description"]
        event.date=request.data["date"]
        event.time=request.data["time"]

        organizer=Gamer.objects.get(user=request.auth.user)
        event.organizer=organizer

        game=Game.objects.get(pk=request.data["game"])
        event.game=game

        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk):
        event=Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @ action(methods=['post'], detail=True)
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""

        gamer=Gamer.objects.get(user=request.auth.user)
        event=Event.objects.get(pk=pk)
        event.attendees.add(gamer)
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)

    @ action(methods=['delete'], detail=True)
    def leave(self, request, pk):
        """Post request for a user to sign up for an event"""

        gamer=Gamer.objects.get(user=request.auth.user)
        event=Event.objects.get(pk=pk)
        event.attendees.remove(gamer)
        return Response({'message': 'Gamer removed'}, status=status.HTTP_204_NO_CONTENT)



class EventSerializer(serializers.ModelSerializer):
    attendee_count=serializers.IntegerField(default=None)
    joined=serializers.IntegerField(default=None)
    """JSON serializer for game types
    """
    class Meta:
        model=Event
        fields=('id', 'description', 'date', 'time', 'organizer','game', 'attendees', 'joined', 'attendee_count')
        depth=1

class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'description', 'date', 'time', 'game']
