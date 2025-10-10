from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Caretaker, UserCaretaker
from .serializers import (
    CaretakerSerializer, UserCaretakerSerializer, 
    CaretakerCreateSerializer
)


class CaretakerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user's caretakers"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CaretakerCreateSerializer
        return CaretakerSerializer

    def get_queryset(self):
        # Return caretakers linked to the current user
        user_caretaker_ids = UserCaretaker.objects.filter(
            user=self.request.user
        ).values_list('caretaker_id', flat=True)
        
        return Caretaker.objects.filter(id__in=user_caretaker_ids)

    def list(self, request, *args, **kwargs):
        """List user's caretakers with permission details"""
        user_caretakers = UserCaretaker.objects.filter(
            user=request.user
        ).select_related('caretaker')
        
        serializer = UserCaretakerSerializer(
            user_caretakers, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def link_existing(self, request):
        """Link an existing caretaker to the user"""
        serializer = UserCaretakerSerializer(
            data=request.data, context={'request': request}
        )
        
        if serializer.is_valid():
            # Check if link already exists
            caretaker_id = serializer.validated_data['caretaker_id']
            if UserCaretaker.objects.filter(
                user=request.user, caretaker_id=caretaker_id
            ).exists():
                return Response(
                    {'error': 'Caretaker is already linked to your account'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_caretaker = serializer.save()
            return Response(
                UserCaretakerSerializer(user_caretaker, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put', 'patch'])
    def update_permissions(self, request, pk=None):
        """Update permissions for a caretaker link"""
        try:
            user_caretaker = UserCaretaker.objects.get(
                user=request.user, caretaker_id=pk
            )
        except UserCaretaker.DoesNotExist:
            return Response(
                {'error': 'Caretaker link not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserCaretakerSerializer(
            user_caretaker, data=request.data, partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def unlink(self, request, pk=None):
        """Unlink a caretaker from the user"""
        try:
            user_caretaker = UserCaretaker.objects.get(
                user=request.user, caretaker_id=pk
            )
            user_caretaker.delete()
            return Response({'message': 'Caretaker unlinked successfully'})
        except UserCaretaker.DoesNotExist:
            return Response(
                {'error': 'Caretaker link not found'},
                status=status.HTTP_404_NOT_FOUND
            )
