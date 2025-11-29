from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from medicines.models import Medicines


class AlarmListView(APIView):
    """
    GET /list/ - Fetch all alarms for the authenticated user
    POST /list/ - Not allowed (405 Method Not Allowed)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch all alarms based on user's medicines.
        Returns medicine schedules formatted as alarms.
        """
        user = request.user
        medicines = Medicines.objects.filter(user=user)
        
        alarms = {}
        for medicine in medicines:
            alarms[str(medicine.id)] = {
                "name": medicine.name,
                "days_of_week": medicine.days_of_week if medicine.days_of_week else [],
                "time": medicine.time if medicine.time else []
            }
        
        return Response(alarms, status=status.HTTP_200_OK)

    def post(self, request):
        """POST method not allowed for alarms."""
        return Response(
            {"detail": "POST method not allowed. Alarms are generated from medicines."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class AlarmDetailView(APIView):
    """
    Handles PUT/PATCH/DELETE requests - all not allowed.
    Users should modify medicines to update alarms.
    """
    permission_classes = [IsAuthenticated]

    def put(self, request, pk=None):
        return Response(
            {"detail": "PUT method not allowed. Edit medicines to update alarms."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def patch(self, request, pk=None):
        return Response(
            {"detail": "PATCH method not allowed. Edit medicines to update alarms."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def delete(self, request, pk=None):
        return Response(
            {"detail": "DELETE method not allowed. Delete medicines to remove alarms."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )