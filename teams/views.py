from rest_framework.views import APIView, status
from rest_framework.response import Response
from django.db import IntegrityError
from django.forms.models import model_to_dict

from .models import Team
import ipdb


class TeamView(APIView):
    def post(self, request):
        request = request.data
        year = int(request["first_cup"][0:4])
        year_cup = list(range(1930, 2023, 4))
        valid_title = list(range(int(year), 2023, 4))

        try:
            if request["titles"] < 0:
                return Response({"error": "titles cannot be negative"}, status.HTTP_400_BAD_REQUEST)
            if year < 1930:
                return Response({"error": "there was no world cup this year"}, status.HTTP_400_BAD_REQUEST)
            if year not in year_cup:
                return Response({"error": "there was no world cup this year"}, status.HTTP_400_BAD_REQUEST)
            if request["titles"] > len(valid_title):
                return Response({"error": "impossible to have more titles than disputed cups"}, status.HTTP_400_BAD_REQUEST)
            team = Team.objects.create(**request)
        except IntegrityError:
            return Response({"error": "team already exists"}, status.HTTP_404_NOT_FOUND)

        team_dict = model_to_dict(team)
        return Response(team_dict, status.HTTP_201_CREATED)

    def get(self, request):
        teams = Team.objects.all()
        teams_dict = [model_to_dict(teams) for teams in teams]

        return Response(teams_dict)
