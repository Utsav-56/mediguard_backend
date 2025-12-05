from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import datetime, timedelta

from core.permissions_models import EveryoneAllowed
from .models import HealthTemplate, HealthRecord
from .serializers import (
    HealthTemplateSerializer,
    HealthTemplateListSerializer,
    HealthRecordSerializer,
    HealthRecordCreateSerializer,
    HealthRecordUpdateSerializer,
    HealthRecordListSerializer,
)


# ============== Template Views (Read-Only for Users) ==============


class HealthTemplateListView(APIView):
    """
    GET /templates/ - List all available health templates
    """

    permission_classes = [EveryoneAllowed]

    def get(self, request):
        """
        Get all active health templates.

        Query Parameters:
        - category: Filter by category (e.g., 'cardiovascular', 'metabolic')
        """
        templates = HealthTemplate.objects.filter(is_active=True)

        # Filter by category if provided
        category = request.query_params.get("category")
        if category:
            templates = templates.filter(category__iexact=category)

        serializer = HealthTemplateListSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HealthTemplateDetailView(APIView):
    """
    GET /templates/<id>/ - Get template details by ID
    GET /templates/slug/<slug>/ - Get template details by slug
    """

    permission_classes = [EveryoneAllowed]

    def get(self, request, pk=None, slug=None):
        """Get template details including schema"""
        try:
            if pk:
                template = HealthTemplate.objects.get(pk=pk, is_active=True)
            elif slug:
                template = HealthTemplate.objects.get(slug=slug, is_active=True)
            else:
                return Response(
                    {"detail": "Provide either ID or slug"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except HealthTemplate.DoesNotExist:
            return Response(
                {"detail": "Template not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = HealthTemplateSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HealthTemplateCategoriesView(APIView):
    """
    GET /templates/categories/ - List all template categories
    """

    permission_classes = [EveryoneAllowed]

    def get(self, request):
        """Get list of all available categories"""
        categories = (
            HealthTemplate.objects.filter(is_active=True, category__isnull=False)
            .values_list("category", flat=True)
            .distinct()
        )

        return Response(list(categories), status=status.HTTP_200_OK)


# ============== Health Record Views ==============


class HealthRecordListView(APIView):
    """
    GET /records/ - List user's health records
    POST /records/ - Create a new health record
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Get all health records for the user.

        Query Parameters:
        - template_id: Filter by template ID
        - template_slug: Filter by template slug
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        - limit: Limit number of results
        """
        user = request.user
        records = HealthRecord.objects.filter(user=user)

        # Apply filters
        template_id = request.query_params.get("template_id")
        template_slug = request.query_params.get("template_slug")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        limit = request.query_params.get("limit")

        if template_id:
            records = records.filter(template_id=template_id)

        if template_slug:
            records = records.filter(template__slug=template_slug)

        if start_date:
            try:
                filter_start = datetime.strptime(start_date, "%Y-%m-%d")
                records = records.filter(recorded_at__date__gte=filter_start)
            except ValueError:
                return Response(
                    {"detail": "Invalid start_date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if end_date:
            try:
                filter_end = datetime.strptime(end_date, "%Y-%m-%d")
                records = records.filter(recorded_at__date__lte=filter_end)
            except ValueError:
                return Response(
                    {"detail": "Invalid end_date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if limit:
            try:
                records = records[: int(limit)]
            except ValueError:
                pass

        serializer = HealthRecordListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create a new health record"""
        serializer = HealthRecordCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            record = serializer.save()
            response_serializer = HealthRecordSerializer(record)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HealthRecordDetailView(APIView):
    """
    GET /records/<id>/ - Get a specific health record
    PUT /records/<id>/ - Update a health record
    PATCH /records/<id>/ - Partial update a health record
    DELETE /records/<id>/ - Delete a health record
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """Get record ensuring it belongs to the user"""
        try:
            return HealthRecord.objects.get(pk=pk, user=user)
        except HealthRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get a specific health record"""
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"detail": "Health record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = HealthRecordSerializer(record)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """Update a health record"""
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"detail": "Health record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = HealthRecordUpdateSerializer(record, data=request.data)
        if serializer.is_valid():
            record = serializer.save()
            response_serializer = HealthRecordSerializer(record)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partial update a health record"""
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"detail": "Health record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = HealthRecordUpdateSerializer(
            record, data=request.data, partial=True
        )
        if serializer.is_valid():
            record = serializer.save()
            response_serializer = HealthRecordSerializer(record)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a health record"""
        record = self.get_object(pk, request.user)
        if not record:
            return Response(
                {"detail": "Health record not found"}, status=status.HTTP_404_NOT_FOUND
            )

        record.delete()
        return Response(
            {"detail": "Health record deleted successfully"}, status=status.HTTP_200_OK
        )


class HealthRecordByTemplateView(APIView):
    """
    GET /records/template/<template_slug>/ - Get all records for a specific template
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, template_slug):
        """Get all records for a specific template type"""
        user = request.user

        try:
            template = HealthTemplate.objects.get(slug=template_slug, is_active=True)
        except HealthTemplate.DoesNotExist:
            return Response(
                {"detail": "Template not found"}, status=status.HTTP_404_NOT_FOUND
            )

        records = HealthRecord.objects.filter(user=user, template=template)

        # Optional date filters
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        limit = request.query_params.get("limit")

        if start_date:
            try:
                filter_start = datetime.strptime(start_date, "%Y-%m-%d")
                records = records.filter(recorded_at__date__gte=filter_start)
            except ValueError:
                pass

        if end_date:
            try:
                filter_end = datetime.strptime(end_date, "%Y-%m-%d")
                records = records.filter(recorded_at__date__lte=filter_end)
            except ValueError:
                pass

        if limit:
            try:
                records = records[: int(limit)]
            except ValueError:
                pass

        serializer = HealthRecordListSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HealthRecordLatestView(APIView):
    """
    GET /records/latest/ - Get the latest record for each template type
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get the most recent record for each template"""
        user = request.user

        # Get all templates user has records for
        template_ids = (
            HealthRecord.objects.filter(user=user)
            .values_list("template_id", flat=True)
            .distinct()
        )

        latest_records = []
        for template_id in template_ids:
            latest = HealthRecord.objects.filter(
                user=user, template_id=template_id
            ).first()  # Already ordered by -recorded_at
            if latest:
                latest_records.append(latest)

        serializer = HealthRecordListSerializer(latest_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HealthRecordStatsView(APIView):
    """
    GET /records/stats/<template_slug>/ - Get statistics for a template
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, template_slug):
        """
        Get statistics for records of a specific template.

        Query Parameters:
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        - days: Number of days to look back (default: 30)
        """
        user = request.user

        try:
            template = HealthTemplate.objects.get(slug=template_slug, is_active=True)
        except HealthTemplate.DoesNotExist:
            return Response(
                {"detail": "Template not found"}, status=status.HTTP_404_NOT_FOUND
            )

        records = HealthRecord.objects.filter(user=user, template=template)

        # Date filtering
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        days = request.query_params.get("days", "30")

        if start_date:
            try:
                filter_start = datetime.strptime(start_date, "%Y-%m-%d")
                records = records.filter(recorded_at__date__gte=filter_start)
            except ValueError:
                pass
        elif not end_date:
            # Default to last N days
            try:
                days_back = int(days)
                filter_start = timezone.now() - timedelta(days=days_back)
                records = records.filter(recorded_at__gte=filter_start)
            except ValueError:
                pass

        if end_date:
            try:
                filter_end = datetime.strptime(end_date, "%Y-%m-%d")
                records = records.filter(recorded_at__date__lte=filter_end)
            except ValueError:
                pass

        # Calculate stats for numeric fields
        stats = {
            "template_name": template.name,
            "template_slug": template.slug,
            "total_records": records.count(),
            "fields": {},
        }

        if records.exists():
            stats["first_record"] = records.last().recorded_at
            stats["latest_record"] = records.first().recorded_at

            # Calculate stats for each numeric field in schema
            for field_name, field_config in template.schema.items():
                field_type = field_config.get("type")

                if field_type in ["int", "float"]:
                    values = []
                    for record in records:
                        val = record.data.get(field_name)
                        if val is not None and isinstance(val, (int, float)):
                            values.append(val)

                    if values:
                        stats["fields"][field_name] = {
                            "unit": field_config.get("unit", ""),
                            "count": len(values),
                            "min": min(values),
                            "max": max(values),
                            "avg": round(sum(values) / len(values), 2),
                            "latest": values[0] if values else None,
                        }

        return Response(stats, status=status.HTTP_200_OK)


class HealthRecordSummaryView(APIView):
    """
    GET /records/summary/ - Get a summary of all health records
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get summary of user's health records"""
        user = request.user
        records = HealthRecord.objects.filter(user=user)

        # Group by template
        summary = {}
        templates = HealthTemplate.objects.filter(
            id__in=records.values_list("template_id", flat=True).distinct()
        )

        for template in templates:
            template_records = records.filter(template=template)
            latest = template_records.first()

            summary[template.slug] = {
                "template_id": template.id,
                "template_name": template.name,
                "template_icon": template.icon,
                "total_records": template_records.count(),
                "latest_record": (
                    {
                        "id": latest.id,
                        "data": latest.data,
                        "recorded_at": latest.recorded_at,
                    }
                    if latest
                    else None
                ),
            }

        return Response(summary, status=status.HTTP_200_OK)
