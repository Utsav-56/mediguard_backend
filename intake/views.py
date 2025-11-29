from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta

from .models import Intake
from .serializers import (
    IntakeSerializer,
    IntakeCreateSerializer,
    IntakeUpdateSerializer,
    IntakeBulkCreateSerializer,
    IntakeStatsSerializer,
)
from medicines.models import Medicines


class IntakeListView(APIView):
    """
    GET /list/ - Fetch all intakes for the authenticated user
    POST /list/ - Create a new intake record
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch all intakes for the user.
        
        Query Parameters:
        - date: Filter by specific date (YYYY-MM-DD)
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        - medicine_id: Filter by specific medicine
        - status: Filter by status (pending/taken/skipped/missed)
        """
        user = request.user
        intakes = Intake.objects.filter(user=user)

        # Apply filters
        date = request.query_params.get('date')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        medicine_id = request.query_params.get('medicine_id')
        intake_status = request.query_params.get('status')

        if date:
            try:
                filter_date = datetime.strptime(date, '%Y-%m-%d').date()
                intakes = intakes.filter(scheduled_date=filter_date)
            except ValueError:
                return Response(
                    {"detail": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if start_date:
            try:
                filter_start = datetime.strptime(start_date, '%Y-%m-%d').date()
                intakes = intakes.filter(scheduled_date__gte=filter_start)
            except ValueError:
                return Response(
                    {"detail": "Invalid start_date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if end_date:
            try:
                filter_end = datetime.strptime(end_date, '%Y-%m-%d').date()
                intakes = intakes.filter(scheduled_date__lte=filter_end)
            except ValueError:
                return Response(
                    {"detail": "Invalid end_date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if medicine_id:
            intakes = intakes.filter(medicine_id=medicine_id)

        if intake_status:
            intakes = intakes.filter(status=intake_status)

        serializer = IntakeSerializer(intakes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new intake record"""
        serializer = IntakeCreateSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            intake = serializer.save()
            response_serializer = IntakeSerializer(intake)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IntakeDetailView(APIView):
    """
    GET /intake/<id>/ - Get a specific intake
    PUT /intake/<id>/ - Update an intake
    PATCH /intake/<id>/ - Partial update an intake
    DELETE /intake/<id>/ - Delete an intake
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Get intake object ensuring it belongs to the user"""
        try:
            return Intake.objects.get(pk=pk, user=user)
        except Intake.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get a specific intake record"""
        intake = self.get_object(pk, request.user)
        if not intake:
            return Response(
                {"detail": "Intake not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = IntakeSerializer(intake)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """Update an intake record"""
        intake = self.get_object(pk, request.user)
        if not intake:
            return Response(
                {"detail": "Intake not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = IntakeUpdateSerializer(intake, data=request.data)
        if serializer.is_valid():
            intake = serializer.save()
            response_serializer = IntakeSerializer(intake)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partial update an intake record"""
        intake = self.get_object(pk, request.user)
        if not intake:
            return Response(
                {"detail": "Intake not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = IntakeUpdateSerializer(intake, data=request.data, partial=True)
        if serializer.is_valid():
            intake = serializer.save()
            response_serializer = IntakeSerializer(intake)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete an intake record"""
        intake = self.get_object(pk, request.user)
        if not intake:
            return Response(
                {"detail": "Intake not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        intake.delete()
        return Response(
            {"detail": "Intake deleted successfully"},
            status=status.HTTP_200_OK
        )


class IntakeTodayView(APIView):
    """
    GET /today/ - Fetch all intakes for today
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all intakes scheduled for today"""
        user = request.user
        today = timezone.now().date()
        
        intakes = Intake.objects.filter(user=user, scheduled_date=today)
        serializer = IntakeSerializer(intakes, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class IntakeByMedicineView(APIView):
    """
    GET /medicine/<medicine_id>/ - Fetch all intakes for a specific medicine
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, medicine_id):
        """Get all intakes for a specific medicine"""
        user = request.user
        
        # Verify medicine belongs to user
        try:
            medicine = Medicines.objects.get(pk=medicine_id, user=user)
        except Medicines.DoesNotExist:
            return Response(
                {"detail": "Medicine not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        intakes = Intake.objects.filter(user=user, medicine=medicine)
        
        # Optional date filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                filter_start = datetime.strptime(start_date, '%Y-%m-%d').date()
                intakes = intakes.filter(scheduled_date__gte=filter_start)
            except ValueError:
                pass
        
        if end_date:
            try:
                filter_end = datetime.strptime(end_date, '%Y-%m-%d').date()
                intakes = intakes.filter(scheduled_date__lte=filter_end)
            except ValueError:
                pass
        
        serializer = IntakeSerializer(intakes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IntakeMarkTakenView(APIView):
    """
    POST /mark-taken/<id>/ - Quick action to mark an intake as taken
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Mark an intake as taken with current timestamp"""
        try:
            intake = Intake.objects.get(pk=pk, user=request.user)
        except Intake.DoesNotExist:
            return Response(
                {"detail": "Intake not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        intake.status = 'taken'
        intake.taken_at = timezone.now()
        
        # Optional notes from request
        notes = request.data.get('notes')
        if notes:
            intake.notes = notes
        
        intake.save()
        
        serializer = IntakeSerializer(intake)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IntakeMarkSkippedView(APIView):
    """
    POST /mark-skipped/<id>/ - Quick action to mark an intake as skipped
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Mark an intake as skipped"""
        try:
            intake = Intake.objects.get(pk=pk, user=request.user)
        except Intake.DoesNotExist:
            return Response(
                {"detail": "Intake not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        intake.status = 'skipped'
        intake.taken_at = None
        
        # Optional notes (e.g., reason for skipping)
        notes = request.data.get('notes')
        if notes:
            intake.notes = notes
        
        intake.save()
        
        serializer = IntakeSerializer(intake)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IntakeGenerateView(APIView):
    """
    POST /generate/ - Generate intake records for a date range
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Bulk generate intake records based on medicine schedules.
        
        Request Body:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - medicine_ids: Optional list of medicine IDs (default: all user medicines)
        """
        serializer = IntakeBulkCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        medicine_ids = serializer.validated_data.get('medicine_ids', [])

        user = request.user
        
        # Get medicines
        if medicine_ids:
            medicines = Medicines.objects.filter(user=user, id__in=medicine_ids)
        else:
            medicines = Medicines.objects.filter(user=user)

        created_count = 0
        skipped_count = 0

        # Generate intakes for each day in range
        current_date = start_date
        while current_date <= end_date:
            # Get day of week (1=Sunday, 7=Saturday) to match medicine model
            # Python weekday(): Monday=0, Sunday=6
            # Convert to: Sunday=1, Monday=2, ..., Saturday=7
            python_weekday = current_date.weekday()
            day_of_week = (python_weekday + 2) % 7
            if day_of_week == 0:
                day_of_week = 7

            for medicine in medicines:
                # Check if medicine is scheduled for this day
                if day_of_week not in medicine.days_of_week:
                    continue

                # Check date range of medicine
                if medicine.start_date and current_date < medicine.start_date.date():
                    continue
                if medicine.end_date and current_date > medicine.end_date.date():
                    continue

                # Create intake for each scheduled time
                for time_str in medicine.time:
                    try:
                        scheduled_time = datetime.strptime(time_str, '%H:%M').time()
                    except ValueError:
                        continue

                    # Check if intake already exists
                    existing = Intake.objects.filter(
                        user=user,
                        medicine=medicine,
                        scheduled_date=current_date,
                        scheduled_time=scheduled_time
                    ).exists()

                    if existing:
                        skipped_count += 1
                        continue

                    # Create new intake
                    Intake.objects.create(
                        user=user,
                        medicine=medicine,
                        scheduled_date=current_date,
                        scheduled_time=scheduled_time,
                        status='pending'
                    )
                    created_count += 1

            current_date += timedelta(days=1)

        return Response({
            "detail": "Intakes generated successfully",
            "created": created_count,
            "skipped_existing": skipped_count
        }, status=status.HTTP_201_CREATED)


class IntakeStatsView(APIView):
    """
    GET /stats/ - Get intake statistics for the user
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get intake statistics.
        
        Query Parameters:
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        - medicine_id: Filter by specific medicine
        """
        user = request.user
        intakes = Intake.objects.filter(user=user)

        # Apply date filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        medicine_id = request.query_params.get('medicine_id')

        if start_date:
            try:
                filter_start = datetime.strptime(start_date, '%Y-%m-%d').date()
                intakes = intakes.filter(scheduled_date__gte=filter_start)
            except ValueError:
                pass

        if end_date:
            try:
                filter_end = datetime.strptime(end_date, '%Y-%m-%d').date()
                intakes = intakes.filter(scheduled_date__lte=filter_end)
            except ValueError:
                pass

        if medicine_id:
            intakes = intakes.filter(medicine_id=medicine_id)

        # Calculate stats
        total = intakes.count()
        taken = intakes.filter(status='taken').count()
        missed = intakes.filter(status='missed').count()
        skipped = intakes.filter(status='skipped').count()
        pending = intakes.filter(status='pending').count()

        # Adherence rate (taken / (total - pending))
        completed = total - pending
        adherence_rate = (taken / completed * 100) if completed > 0 else 0.0

        # On-time vs late (for taken intakes)
        on_time = 0
        late = 0
        taken_intakes = intakes.filter(status='taken')
        for intake in taken_intakes:
            if intake.is_late:
                late += 1
            else:
                on_time += 1

        stats = {
            "total_intakes": total,
            "taken_count": taken,
            "missed_count": missed,
            "skipped_count": skipped,
            "pending_count": pending,
            "adherence_rate": round(adherence_rate, 2),
            "on_time_count": on_time,
            "late_count": late
        }

        return Response(stats, status=status.HTTP_200_OK)
