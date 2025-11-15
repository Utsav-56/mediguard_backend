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
from rest_framework.decorators import api_view
from rest_framework.response import Response

# serializer is short so we included it in this file itself
from .models import Medicines, MedicineSerializer


def check_authentication(request):
    """Helper function to check if user is authenticated"""
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Auth token is needed for this endpoint (invalid request)"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    return None


@api_view(["GET"])
def medicines_list(request):
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response
    
    medicines = Medicines.objects.filter(user=request.user)
    serializer = MedicineSerializer(medicines, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
def medicines_create(request):
    if request.method != "POST":
        return Response(
            {"detail": f"(Invalid method) only POST method is allowed here but provided with {request.method}"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response
    
    serializer = MedicineSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
def medicine_detail(request, medicine_id):
    if request.method != "GET":
        return Response(
            {"detail": f"(Invalid method) only GET method is allowed here but provided with {request.method}"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response
    
    try:
        medicine = Medicines.objects.get(id=medicine_id, user=request.user)
    except Medicines.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = MedicineSerializer(medicine)
    return Response(serializer.data)


@api_view(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
def medicine_update(request, medicine_id):
    if request.method != "PUT":
        return Response(
            {"detail": f"(Invalid method) only PUT method is allowed here but provided with {request.method}"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response
    
    try:
        medicine = Medicines.objects.get(id=medicine_id, user=request.user)
    except Medicines.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = MedicineSerializer(medicine, data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
def medicine_delete(request, medicine_id):
    if request.method != "DELETE":
        return Response(
            {"detail": f"(Invalid method) only DELETE method is allowed here but provided with {request.method}"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    auth_response = check_authentication(request)
    if auth_response:
        return auth_response
    
    try:
        medicine = Medicines.objects.get(id=medicine_id, user=request.user)
    except Medicines.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    medicine.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
