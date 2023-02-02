from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.request import Request
from django.db import IntegrityError
from django.forms.models import model_to_dict

from .models import Team


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

        return Response(teams_dict, status.HTTP_200_OK)


class TeamDetailsView(APIView):
    def get(self, request: Request, team_id: int):
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"message": "Team not found"}, status.HTTP_404_NOT_FOUND)
        team_dict = model_to_dict(team)
        return Response(team_dict)

    def patch(self, request: Request, team_id: int):
        keys_team = [keys.column for keys in Team._meta.get_fields()]
        validate_schema_key = {key: value for key, value in request.data.items() if key in keys_team}

        try:
            Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"message": "Team not found"}, status.HTTP_404_NOT_FOUND)

        Team.objects.filter(id=team_id).update(**validate_schema_key)
        team_response = model_to_dict(Team.objects.get(id=team_id))
        return Response(team_response, status.HTTP_200_OK)

    def delete(self, request: Request, team_id: int):
        try:
            Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            return Response({"message": "Team not found"}, status.HTTP_404_NOT_FOUND)

        Team.objects.filter(id=team_id).delete()
        return Response(None, status.HTTP_204_NO_CONTENT)
