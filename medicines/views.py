from django.shortcuts import render

# Create your views here.

# /medicine route will be the main entry point for all medicine related operations
# /medicine will support GET, POST, PUT, DELETE methods
# it must need to be authenticated to access every route
# 
# GET /medicine will return all medicines of  user
# POST /medicine will create a new medicine for  user
# PUT /medicine/<int:medicine_id> will update the medicine with the given id for  user
# DELETE /medicine/<int:medicine_id> will delete the medicine with the given id for  user

# GET /medicine/<int:medicine_id> will return the medicine with the given id for  user
# PUT /medicine/<int:medicine_id> will update the medicine with the given id for  user
# DELETE /medicine/<int:medicine_id> will delete the medicine with the given id for user

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# serializer is short so we included it in this file itself
from .models import Medicines,MedicineSerializer

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def medicines(request):
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

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def medicine_detail(request, medicine_id):
    try:
        medicine = Medicines.objects.get(id=medicine_id, user=request.user)
    except Medicines.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = MedicineSerializer(medicine)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = MedicineSerializer(medicine, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        medicine.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

