# Create your views here.
"""
Medicine Management Views Module
This module provides API endpoints for managing medicines in the MediGuard system.
All endpoints require user authentication via token.
Endpoints:
    - GET /medicines/list/ - Retrieve all medicines for authenticated user
    - POST /medicines/list/ - Create a new medicine for authenticated user
    - POST /medicines/add/ - Create a new medicine (alternative endpoint)
    - GET /medicines/detail/<int:medicine_id>/ - Retrieve specific medicine details
    - POST /medicines/detail/<int:medicine_id>/ - Update specific medicine (alternative)
    - PATCH/PUT /medicines/update/<int:medicine_id>/ - Update specific medicine
    - DELETE /medicines/delete/<int:medicine_id>/ - Delete specific medicine
Authentication:
    All endpoints require valid authentication token. Unauthorized requests
    will receive 401 UNAUTHORIZED response.
Author: MediGuard Backend Team
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

# serializer is short so we included it in this file itself
from .models import Medicines, MedicineSerializer


def check_authentication(request):
    """Helper function to check if user is authenticated"""
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Auth token is needed for this endpoint (invalid request)"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    return None


# 1. List view - GET or POST both allowed
@api_view(["GET", "POST"])
def medicines_list(request):
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response

    if request.method == "GET":
        medicines = Medicines.objects.filter(user=request.user)
        serializer = MedicineSerializer(medicines, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = MedicineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 2. Add view - POST only
@api_view(["POST"])
def medicines_add(request):
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response

    serializer = MedicineSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 3. Detail view - GET or POST both allowed
@api_view(["GET", "POST"])
def medicine_detail(request, medicine_id):
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response

    try:
        medicine = Medicines.objects.get(id=medicine_id, user=request.user)
    except Medicines.DoesNotExist:
        return Response(
            {"detail": "Medicine not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = MedicineSerializer(medicine)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = MedicineSerializer(medicine, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 4. Update view - PATCH or PUT
@api_view(["PATCH", "PUT"])
def medicine_update(request, medicine_id):
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response

    try:
        medicine = Medicines.objects.get(id=medicine_id, user=request.user)
    except Medicines.DoesNotExist:
        return Response(
            {"detail": "Medicine not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # partial=True for PATCH, partial=False for PUT
    partial = request.method == "PATCH"
    serializer = MedicineSerializer(medicine, data=request.data, partial=partial)

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 5. Delete view - DELETE only
@api_view(["DELETE"])
def medicine_delete(request, medicine_id):
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response

    try:
        medicine = Medicines.objects.get(id=medicine_id, user=request.user)
    except Medicines.DoesNotExist:
        return Response(
            {"detail": "Medicine not found"}, status=status.HTTP_404_NOT_FOUND
        )

    medicine.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
