from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import Medicine, MedicineAttribute, Schedule, Reminder, Intake
from .serializers import (
    MedicineSerializer, MedicineDetailSerializer, MedicineAttributeSerializer,
    ScheduleSerializer, ReminderSerializer, ReminderActionSerializer, IntakeSerializer
)


class MedicineViewSet(viewsets.ModelViewSet):
    """ViewSet for Medicine CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'start_date']
    search_fields = ['name', 'brand']
    ordering_fields = ['name', 'start_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MedicineDetailSerializer
        return MedicineSerializer

    def get_queryset(self):
        return Medicine.objects.filter(user=self.request.user).prefetch_related(
            'attributes', 'schedules', 'intakes'
        )

    @action(detail=True, methods=['get'])
    def attributes(self, request, pk=None):
        """Get attributes for a specific medicine"""
        medicine = self.get_object()
        attributes = medicine.attributes.all()
        serializer = MedicineAttributeSerializer(attributes, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        """Get schedules for a specific medicine"""
        medicine = self.get_object()
        schedules = medicine.schedules.all()
        serializer = ScheduleSerializer(schedules, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def intakes(self, request, pk=None):
        """Get intake history for a specific medicine"""
        medicine = self.get_object()
        intakes = medicine.intakes.all()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            intakes = intakes.filter(taken_at__gte=start_date)
        if end_date:
            intakes = intakes.filter(taken_at__lte=end_date)
        
        serializer = IntakeSerializer(intakes, many=True, context={'request': request})
        return Response(serializer.data)


class MedicineAttributeViewSet(viewsets.ModelViewSet):
    """ViewSet for MedicineAttribute CRUD operations"""
    serializer_class = MedicineAttributeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MedicineAttribute.objects.filter(user=self.request.user).select_related('medicine')


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for Schedule CRUD operations"""
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['medicine', 'date']
    ordering_fields = ['date', 'time', 'created_at']
    ordering = ['date', 'time']

    def get_queryset(self):
        return Schedule.objects.filter(user=self.request.user).select_related('medicine')


class ReminderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing reminders (read-only with actions)"""
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'schedule__medicine']
    ordering_fields = ['next_run', 'created_at']
    ordering = ['next_run']

    def get_queryset(self):
        return Reminder.objects.filter(
            schedule__user=self.request.user
        ).select_related('schedule__medicine')

    def list(self, request, *args, **kwargs):
        """List upcoming reminders with optional filtering"""
        queryset = self.get_queryset()
        
        # Filter upcoming reminders by default
        upcoming_only = request.query_params.get('upcoming_only', 'true').lower() == 'true'
        if upcoming_only:
            now = timezone.now()
            queryset = queryset.filter(
                status__in=['pending', 'snoozed'],
                next_run__gte=now - timedelta(hours=1)  # Include recent ones
            )
        
        # Limit to next 50 by default
        limit = int(request.query_params.get('limit', 50))
        queryset = queryset[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def snooze(self, request, pk=None):
        """Snooze a reminder"""
        reminder = self.get_object()
        serializer = ReminderActionSerializer(data=request.data)
        
        if serializer.is_valid():
            snooze_minutes = serializer.validated_data.get('snooze_minutes', 15)
            snooze_until = timezone.now() + timedelta(minutes=snooze_minutes)
            
            reminder.snooze_until = snooze_until
            reminder.status = 'snoozed'
            reminder.save()
            
            return Response({
                'message': f'Reminder snoozed for {snooze_minutes} minutes',
                'snooze_until': snooze_until
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss a reminder"""
        reminder = self.get_object()
        serializer = ReminderActionSerializer(data=request.data)
        
        if serializer.is_valid():
            reminder.status = 'dismissed'
            reminder.resolved_at = timezone.now()
            reminder.save()
            
            return Response({'message': 'Reminder dismissed'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IntakeViewSet(viewsets.ModelViewSet):
    """ViewSet for Intake CRUD operations"""
    serializer_class = IntakeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['medicine', 'status', 'schedule']
    ordering_fields = ['taken_at', 'scheduled_time', 'created_at']
    ordering = ['-taken_at', '-scheduled_time']

    def get_queryset(self):
        return Intake.objects.filter(user=self.request.user).select_related(
            'medicine', 'schedule', 'reminder', 'recorded_by'
        )

    def list(self, request, *args, **kwargs):
        """List intakes with optional date filtering"""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(taken_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(taken_at__lte=end_date)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get intake statistics"""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(taken_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(taken_at__lte=end_date)
        
        total_intakes = queryset.count()
        taken_count = queryset.filter(status='taken').count()
        missed_count = queryset.filter(status='missed').count()
        partial_count = queryset.filter(status='partial').count()
        
        adherence_rate = (taken_count / total_intakes * 100) if total_intakes > 0 else 0
        
        return Response({
            'total_intakes': total_intakes,
            'taken': taken_count,
            'missed': missed_count,
            'partial': partial_count,
            'adherence_rate': round(adherence_rate, 2)
        })
