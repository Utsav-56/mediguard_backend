from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Min, Max, Count
from django.utils import timezone
from datetime import timedelta

from .models import HealthMetric, MetricReading, PushSubscription, AuditLog
from .serializers import (
    HealthMetricSerializer, HealthMetricDetailSerializer, 
    MetricReadingSerializer, MetricReadingCreateSerializer,
    PushSubscriptionSerializer, AuditLogSerializer
)


class HealthMetricViewSet(viewsets.ModelViewSet):
    """ViewSet for HealthMetric CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'recorded_at']
    ordering = ['-recorded_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HealthMetricDetailSerializer
        return HealthMetricSerializer

    def get_queryset(self):
        return HealthMetric.objects.filter(user=self.request.user).prefetch_related('readings')

    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """Get readings for a specific health metric"""
        health_metric = self.get_object()
        readings = health_metric.readings.all()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            readings = readings.filter(recorded_at__gte=start_date)
        if end_date:
            readings = readings.filter(recorded_at__lte=end_date)
        
        serializer = MetricReadingSerializer(readings, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a health metric"""
        health_metric = self.get_object()
        readings = health_metric.readings.all()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            readings = readings.filter(recorded_at__gte=start_date)
        if end_date:
            readings = readings.filter(recorded_at__lte=end_date)
        
        stats = {}
        
        # Basic stats
        stats['total_readings'] = readings.count()
        
        if stats['total_readings'] > 0:
            # Blood pressure stats
            if readings.filter(systolic__isnull=False).exists():
                bp_stats = readings.filter(systolic__isnull=False).aggregate(
                    avg_systolic=Avg('systolic'),
                    min_systolic=Min('systolic'),
                    max_systolic=Max('systolic'),
                    avg_diastolic=Avg('diastolic'),
                    min_diastolic=Min('diastolic'),
                    max_diastolic=Max('diastolic')
                )
                stats['blood_pressure'] = bp_stats
            
            # Glucose stats
            if readings.filter(glucose_level__isnull=False).exists():
                glucose_stats = readings.filter(glucose_level__isnull=False).aggregate(
                    avg_glucose=Avg('glucose_level'),
                    min_glucose=Min('glucose_level'),
                    max_glucose=Max('glucose_level')
                )
                stats['glucose'] = glucose_stats
            
            # Weight stats
            if readings.filter(weight__isnull=False).exists():
                weight_stats = readings.filter(weight__isnull=False).aggregate(
                    avg_weight=Avg('weight'),
                    min_weight=Min('weight'),
                    max_weight=Max('weight')
                )
                stats['weight'] = weight_stats
            
            # Heart rate stats
            if readings.filter(heart_rate__isnull=False).exists():
                hr_stats = readings.filter(heart_rate__isnull=False).aggregate(
                    avg_heart_rate=Avg('heart_rate'),
                    min_heart_rate=Min('heart_rate'),
                    max_heart_rate=Max('heart_rate')
                )
                stats['heart_rate'] = hr_stats
        
        return Response(stats)


class MetricReadingViewSet(viewsets.ModelViewSet):
    """ViewSet for MetricReading CRUD operations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['metric', 'metric_key']
    ordering_fields = ['recorded_at', 'created_at']
    ordering = ['-recorded_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return MetricReadingCreateSerializer
        return MetricReadingSerializer

    def get_queryset(self):
        return MetricReading.objects.filter(user=self.request.user).select_related('metric')

    def list(self, request, *args, **kwargs):
        """List metric readings with optional filtering"""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(recorded_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(recorded_at__lte=end_date)
        
        # Filter by metric type
        metric_type = request.query_params.get('metric_type')
        if metric_type == 'blood_pressure':
            queryset = queryset.filter(systolic__isnull=False, diastolic__isnull=False)
        elif metric_type == 'glucose':
            queryset = queryset.filter(glucose_level__isnull=False)
        elif metric_type == 'weight':
            queryset = queryset.filter(weight__isnull=False)
        elif metric_type == 'heart_rate':
            queryset = queryset.filter(heart_rate__isnull=False)
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all metric readings"""
        queryset = self.get_queryset()
        
        # Filter by date range if provided
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(recorded_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(recorded_at__lte=end_date)
        
        summary = {
            'total_readings': queryset.count(),
            'blood_pressure_readings': queryset.filter(systolic__isnull=False).count(),
            'glucose_readings': queryset.filter(glucose_level__isnull=False).count(),
            'weight_readings': queryset.filter(weight__isnull=False).count(),
            'heart_rate_readings': queryset.filter(heart_rate__isnull=False).count(),
        }
        
        # Get metrics by key
        metrics_by_key = queryset.values('metric_key').annotate(count=Count('id')).order_by('-count')
        summary['metrics_by_type'] = list(metrics_by_key)
        
        return Response(summary)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple readings at once"""
        if not isinstance(request.data, list):
            return Response(
                {'error': 'Expected a list of readings'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            readings = serializer.save()
            return Response(
                MetricReadingSerializer(readings, many=True, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PushSubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for PushSubscription CRUD operations"""
    serializer_class = PushSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['platform', 'is_active']

    def get_queryset(self):
        return PushSubscription.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle active status of a push subscription"""
        subscription = self.get_object()
        subscription.is_active = not subscription.is_active
        subscription.save()
        
        return Response({
            'message': f'Subscription {"activated" if subscription.is_active else "deactivated"}',
            'is_active': subscription.is_active
        })


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing audit logs (read-only)"""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['action', 'object_type', 'actor']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return AuditLog.objects.filter(user=self.request.user).select_related('actor', 'user')
