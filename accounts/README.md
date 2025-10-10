# Accounts API Documentation

## Overview

The Accounts app provides user authentication and caretaker management functionality for the MediGuard application. It includes user registration, login, profile management, and caretaker relationship management.

## Base URL

All endpoints are accessed via: `http://your-domain.com/api/accounts/`

**Note**: Currently the accounts URLs are commented out in the main URL configuration. To enable the accounts endpoints, uncomment the line in `main_app/urls.py`:

```python
# Uncomment this line:
path('api/accounts/', include('accounts.urls')),
```

## Authentication

The API uses JWT (JSON Web Token) authentication via Djoser. All endpoints except registration and login require authentication.

### Authentication Headers

Include the JWT token in the Authorization header for authenticated requests:

```
Authorization: Bearer <your_jwt_token>
```

## User Management (via Djoser)

These endpoints are available at `/auth/` base URL:

### 1. User Registration

**Endpoint**: `POST /auth/users/`

**Description**: Register a new user account

**Request Body**:

```json
{
	"email": "user@example.com",
	"password": "securepassword123",
	"full_name": "John Doe",
	"phone_number": "+1234567890",
	"address": "123 Main St, City, Country"
}
```

**Response** (201 Created):

```json
{
	"id": 1,
	"email": "user@example.com",
	"full_name": "John Doe",
	"phone_number": "+1234567890",
	"address": "123 Main St, City, Country",
	"profile_image": null
}
```

**Flutter Example (using Dio)**:

```dart
import 'package:dio/dio.dart';

Future<Map<String, dynamic>> registerUser({
  required String email,
  required String password,
  required String fullName,
  String? phoneNumber,
  String? address,
}) async {
  final dio = Dio();

  try {
    final response = await dio.post(
      'http://your-domain.com/auth/users/',
      data: {
        'email': email,
        'password': password,
        'full_name': fullName,
        'phone_number': phoneNumber,
        'address': address,
      },
    );

    return response.data;
  } catch (e) {
    throw Exception('Registration failed: $e');
  }
}
```

### 2. User Login

**Endpoint**: `POST /auth/jwt/create/`

**Description**: Login and receive JWT tokens

**Request Body**:

```json
{
	"email": "user@example.com",
	"password": "securepassword123"
}
```

**Response** (200 OK):

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Flutter Example**:

```dart
Future<Map<String, String>> loginUser({
  required String email,
  required String password,
}) async {
  final dio = Dio();

  try {
    final response = await dio.post(
      'http://your-domain.com/auth/jwt/create/',
      data: {
        'email': email,
        'password': password,
      },
    );

    return {
      'access': response.data['access'],
      'refresh': response.data['refresh'],
    };
  } catch (e) {
    throw Exception('Login failed: $e');
  }
}
```

### 3. Token Refresh

**Endpoint**: `POST /auth/jwt/refresh/`

**Description**: Refresh the access token using refresh token

**Request Body**:

```json
{
	"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response** (200 OK):

```json
{
	"access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 4. Get Current User

**Endpoint**: `GET /auth/users/me/`

**Description**: Get current authenticated user details

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
	"id": 1,
	"email": "user@example.com",
	"full_name": "John Doe",
	"phone_number": "+1234567890",
	"address": "123 Main St, City, Country",
	"profile_image": "http://your-domain.com/media/profile_images/user_abc123.jpg"
}
```

**Flutter Example**:

```dart
Future<Map<String, dynamic>> getCurrentUser(String accessToken) async {
  final dio = Dio();
  dio.options.headers['Authorization'] = 'Bearer $accessToken';

  try {
    final response = await dio.get('http://your-domain.com/auth/users/me/');
    return response.data;
  } catch (e) {
    throw Exception('Failed to get user: $e');
  }
}
```

### 5. Update User Profile

**Endpoint**: `PATCH /auth/users/me/`

**Description**: Update current user profile

**Headers**: `Authorization: Bearer <access_token>`

**Request Body** (Form Data for file upload):

```json
{
	"full_name": "John Updated Doe",
	"phone_number": "+1234567891",
	"address": "456 New St, City, Country"
}
```

**For Profile Image Upload** (use multipart/form-data):

```
Content-Type: multipart/form-data

full_name: John Doe
profile_image: [binary file data]
```

**Response** (200 OK):

```json
{
	"id": 1,
	"email": "user@example.com",
	"full_name": "John Updated Doe",
	"phone_number": "+1234567891",
	"address": "456 New St, City, Country",
	"profile_image": "http://your-domain.com/media/profile_images/user_xyz789.jpg"
}
```

**Flutter Example (with image upload)**:

```dart
import 'package:dio/dio.dart';
import 'dart:io';

Future<Map<String, dynamic>> updateUserProfile({
  required String accessToken,
  String? fullName,
  String? phoneNumber,
  String? address,
  File? profileImage,
}) async {
  final dio = Dio();
  dio.options.headers['Authorization'] = 'Bearer $accessToken';

  FormData formData = FormData();

  if (fullName != null) formData.fields.add(MapEntry('full_name', fullName));
  if (phoneNumber != null) formData.fields.add(MapEntry('phone_number', phoneNumber));
  if (address != null) formData.fields.add(MapEntry('address', address));

  if (profileImage != null) {
    formData.files.add(MapEntry(
      'profile_image',
      await MultipartFile.fromFile(profileImage.path),
    ));
  }

  try {
    final response = await dio.patch(
      'http://your-domain.com/auth/users/me/',
      data: formData,
    );
    return response.data;
  } catch (e) {
    throw Exception('Profile update failed: $e');
  }
}
```

## Caretaker Management

**Base URL**: `/api/accounts/caretakers/`

### 6. List Caretakers

**Endpoint**: `GET /api/accounts/caretakers/`

**Description**: Get all caretakers linked to the authenticated user

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
[
	{
		"id": 1,
		"full_name": "Jane Smith",
		"email": "jane@example.com",
		"phone": "+1234567890",
		"whatsapp_number": "+1234567890",
		"profile_image": "http://your-domain.com/media/profile_images/caretaker_abc123.jpg",
		"relationship": "Daughter",
		"address": "789 Care St, City, Country",
		"note": "Primary caretaker",
		"created_at": "2024-01-15T10:30:00Z",
		"updated_at": "2024-01-15T10:30:00Z"
	}
]
```

**Flutter Example**:

```dart
Future<List<Map<String, dynamic>>> getCaretakers(String accessToken) async {
  final dio = Dio();
  dio.options.headers['Authorization'] = 'Bearer $accessToken';

  try {
    final response = await dio.get('http://your-domain.com/api/accounts/caretakers/');
    return List<Map<String, dynamic>>.from(response.data);
  } catch (e) {
    throw Exception('Failed to get caretakers: $e');
  }
}
```

### 7. Get Caretaker Details

**Endpoint**: `GET /api/accounts/caretakers/{id}/`

**Description**: Get specific caretaker details

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
{
	"id": 1,
	"full_name": "Jane Smith",
	"email": "jane@example.com",
	"phone": "+1234567890",
	"whatsapp_number": "+1234567890",
	"profile_image": "http://your-domain.com/media/profile_images/caretaker_abc123.jpg",
	"relationship": "Daughter",
	"address": "789 Care St, City, Country",
	"note": "Primary caretaker",
	"created_at": "2024-01-15T10:30:00Z",
	"updated_at": "2024-01-15T10:30:00Z"
}
```

### 8. Create New Caretaker

**Endpoint**: `POST /api/accounts/caretakers/`

**Description**: Create a new caretaker and automatically link to current user

**Headers**: `Authorization: Bearer <access_token>`

**Request Body** (JSON):

```json
{
	"full_name": "Alice Johnson",
	"email": "alice@example.com",
	"phone": "+1234567891",
	"whatsapp_number": "+1234567891",
	"relationship": "Sister",
	"address": "321 Family Ave, City, Country",
	"note": "Emergency contact"
}
```

**Request Body** (Multipart for image upload):

```
Content-Type: multipart/form-data

full_name: Alice Johnson
email: alice@example.com
phone: +1234567891
whatsapp_number: +1234567891
relationship: Sister
address: 321 Family Ave, City, Country
note: Emergency contact
profile_image: [binary file data]
```

**Response** (201 Created):

```json
{
	"id": 2,
	"full_name": "Alice Johnson",
	"email": "alice@example.com",
	"phone": "+1234567891",
	"whatsapp_number": "+1234567891",
	"profile_image": "http://your-domain.com/media/profile_images/caretaker_def456.jpg",
	"relationship": "Sister",
	"address": "321 Family Ave, City, Country",
	"note": "Emergency contact",
	"created_at": "2024-01-15T11:30:00Z",
	"updated_at": "2024-01-15T11:30:00Z"
}
```

**Flutter Example**:

```dart
Future<Map<String, dynamic>> createCaretaker({
  required String accessToken,
  required String fullName,
  required String email,
  required String phone,
  String? whatsappNumber,
  String? relationship,
  String? address,
  String? note,
  File? profileImage,
}) async {
  final dio = Dio();
  dio.options.headers['Authorization'] = 'Bearer $accessToken';

  FormData formData = FormData.fromMap({
    'full_name': fullName,
    'email': email,
    'phone': phone,
    if (whatsappNumber != null) 'whatsapp_number': whatsappNumber,
    if (relationship != null) 'relationship': relationship,
    if (address != null) 'address': address,
    if (note != null) 'note': note,
  });

  if (profileImage != null) {
    formData.files.add(MapEntry(
      'profile_image',
      await MultipartFile.fromFile(profileImage.path),
    ));
  }

  try {
    final response = await dio.post(
      'http://your-domain.com/api/accounts/caretakers/',
      data: formData,
    );
    return response.data;
  } catch (e) {
    throw Exception('Failed to create caretaker: $e');
  }
}
```

### 9. Link Existing Caretaker

**Endpoint**: `POST /api/accounts/caretakers/link-existing/`

**Description**: Link an existing caretaker to the current user

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:

```json
{
	"caretaker_id": 3,
	"active": true,
	"note": "Night shift caretaker"
}
```

**Response** (201 Created or 200 OK if already linked):

```json
{
	"id": 5,
	"user": 1,
	"caretaker": {
		"id": 3,
		"full_name": "Bob Wilson",
		"email": "bob@example.com",
		"phone": "+1234567892",
		"whatsapp_number": "+1234567892",
		"profile_image": null,
		"relationship": "Friend",
		"address": "654 Helper Rd, City, Country",
		"note": "Available evenings",
		"created_at": "2024-01-10T09:00:00Z",
		"updated_at": "2024-01-10T09:00:00Z"
	},
	"active": true,
	"note": "Night shift caretaker",
	"created_at": "2024-01-15T12:00:00Z"
}
```

## User-Caretaker Relationship Management

**Base URL**: `/api/accounts/user-caretakers/`

### 10. List User-Caretaker Links

**Endpoint**: `GET /api/accounts/user-caretakers/`

**Description**: Get all caretaker relationships for the authenticated user

**Headers**: `Authorization: Bearer <access_token>`

**Response** (200 OK):

```json
[
	{
		"id": 1,
		"user": 1,
		"caretaker": {
			"id": 1,
			"full_name": "Jane Smith",
			"email": "jane@example.com",
			"phone": "+1234567890",
			"whatsapp_number": "+1234567890",
			"profile_image": "http://your-domain.com/media/profile_images/caretaker_abc123.jpg",
			"relationship": "Daughter",
			"address": "789 Care St, City, Country",
			"note": "Primary caretaker",
			"created_at": "2024-01-15T10:30:00Z",
			"updated_at": "2024-01-15T10:30:00Z"
		},
		"active": true,
		"note": "Primary contact",
		"created_at": "2024-01-15T10:30:00Z"
	}
]
```

### 11. Update User-Caretaker Link

**Endpoint**: `PATCH /api/accounts/user-caretakers/{id}/`

**Description**: Update relationship details (activate/deactivate, update notes)

**Headers**: `Authorization: Bearer <access_token>`

**Request Body**:

```json
{
	"active": false,
	"note": "Temporarily unavailable"
}
```

**Response** (200 OK):

```json
{
	"id": 1,
	"user": 1,
	"caretaker": {
		"id": 1,
		"full_name": "Jane Smith",
		"email": "jane@example.com",
		"phone": "+1234567890",
		"whatsapp_number": "+1234567890",
		"profile_image": "http://your-domain.com/media/profile_images/caretaker_abc123.jpg",
		"relationship": "Daughter",
		"address": "789 Care St, City, Country",
		"note": "Primary caretaker",
		"created_at": "2024-01-15T10:30:00Z",
		"updated_at": "2024-01-15T10:30:00Z"
	},
	"active": false,
	"note": "Temporarily unavailable",
	"created_at": "2024-01-15T10:30:00Z"
}
```

### 12. Delete User-Caretaker Link

**Endpoint**: `DELETE /api/accounts/user-caretakers/{id}/`

**Description**: Remove the relationship between user and caretaker

**Headers**: `Authorization: Bearer <access_token>`

**Response** (204 No Content)

**Flutter Example**:

```dart
Future<void> deleteCaretakerLink(String accessToken, int linkId) async {
  final dio = Dio();
  dio.options.headers['Authorization'] = 'Bearer $accessToken';

  try {
    await dio.delete('http://your-domain.com/api/accounts/user-caretakers/$linkId/');
  } catch (e) {
    throw Exception('Failed to delete caretaker link: $e');
  }
}
```

## Data Models

### User Model

```json
{
	"id": 1,
	"email": "user@example.com",
	"full_name": "John Doe",
	"phone_number": "+1234567890",
	"address": "123 Main St, City, Country",
	"profile_image": "http://your-domain.com/media/profile_images/user_abc123.jpg"
}
```

### Caretaker Model

```json
{
	"id": 1,
	"full_name": "Jane Smith",
	"email": "jane@example.com",
	"phone": "+1234567890",
	"whatsapp_number": "+1234567890",
	"profile_image": "http://your-domain.com/media/profile_images/caretaker_abc123.jpg",
	"relationship": "Daughter",
	"address": "789 Care St, City, Country",
	"note": "Primary caretaker",
	"created_at": "2024-01-15T10:30:00Z",
	"updated_at": "2024-01-15T10:30:00Z"
}
```

### UserCaretaker Link Model

```json
{
	"id": 1,
	"user": 1,
	"caretaker": {
		/* Caretaker object */
	},
	"active": true,
	"note": "Primary contact",
	"created_at": "2024-01-15T10:30:00Z"
}
```

## Error Responses

### Common Error Formats

**401 Unauthorized**:

```json
{
	"detail": "Given token not valid for any token type"
}
```

**400 Bad Request**:

```json
{
	"email": ["This field is required."],
	"password": ["This field is required."]
}
```

**404 Not Found**:

```json
{
	"detail": "Not found."
}
```

**500 Internal Server Error**:

```json
{
	"detail": "Internal server error"
}
```

## Flutter Integration Example

Here's a complete Flutter service class example:

```dart
import 'package:dio/dio.dart';
import 'dart:io';

class AccountsService {
  final Dio _dio;
  final String baseUrl;

  AccountsService({required this.baseUrl}) : _dio = Dio() {
    _dio.options.baseUrl = baseUrl;
  }

  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  // Authentication
  Future<Map<String, dynamic>> register({
    required String email,
    required String password,
    required String fullName,
    String? phoneNumber,
    String? address,
  }) async {
    final response = await _dio.post('/auth/users/', data: {
      'email': email,
      'password': password,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'address': address,
    });
    return response.data;
  }

  Future<Map<String, String>> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post('/auth/jwt/create/', data: {
      'email': email,
      'password': password,
    });
    return {
      'access': response.data['access'],
      'refresh': response.data['refresh'],
    };
  }

  Future<String> refreshToken(String refreshToken) async {
    final response = await _dio.post('/auth/jwt/refresh/', data: {
      'refresh': refreshToken,
    });
    return response.data['access'];
  }

  // User Management
  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/auth/users/me/');
    return response.data;
  }

  Future<Map<String, dynamic>> updateProfile({
    String? fullName,
    String? phoneNumber,
    String? address,
    File? profileImage,
  }) async {
    FormData formData = FormData();

    if (fullName != null) formData.fields.add(MapEntry('full_name', fullName));
    if (phoneNumber != null) formData.fields.add(MapEntry('phone_number', phoneNumber));
    if (address != null) formData.fields.add(MapEntry('address', address));

    if (profileImage != null) {
      formData.files.add(MapEntry(
        'profile_image',
        await MultipartFile.fromFile(profileImage.path),
      ));
    }

    final response = await _dio.patch('/auth/users/me/', data: formData);
    return response.data;
  }

  // Caretaker Management
  Future<List<Map<String, dynamic>>> getCaretakers() async {
    final response = await _dio.get('/api/accounts/caretakers/');
    return List<Map<String, dynamic>>.from(response.data);
  }

  Future<Map<String, dynamic>> getCaretaker(int id) async {
    final response = await _dio.get('/api/accounts/caretakers/$id/');
    return response.data;
  }

  Future<Map<String, dynamic>> createCaretaker({
    required String fullName,
    required String email,
    required String phone,
    String? whatsappNumber,
    String? relationship,
    String? address,
    String? note,
    File? profileImage,
  }) async {
    FormData formData = FormData.fromMap({
      'full_name': fullName,
      'email': email,
      'phone': phone,
      if (whatsappNumber != null) 'whatsapp_number': whatsappNumber,
      if (relationship != null) 'relationship': relationship,
      if (address != null) 'address': address,
      if (note != null) 'note': note,
    });

    if (profileImage != null) {
      formData.files.add(MapEntry(
        'profile_image',
        await MultipartFile.fromFile(profileImage.path),
      ));
    }

    final response = await _dio.post('/api/accounts/caretakers/', data: formData);
    return response.data;
  }

  Future<Map<String, dynamic>> linkExistingCaretaker({
    required int caretakerId,
    bool active = true,
    String? note,
  }) async {
    final response = await _dio.post('/api/accounts/caretakers/link-existing/', data: {
      'caretaker_id': caretakerId,
      'active': active,
      'note': note,
    });
    return response.data;
  }

  // User-Caretaker Links
  Future<List<Map<String, dynamic>>> getUserCaretakerLinks() async {
    final response = await _dio.get('/api/accounts/user-caretakers/');
    return List<Map<String, dynamic>>.from(response.data);
  }

  Future<Map<String, dynamic>> updateCaretakerLink({
    required int linkId,
    bool? active,
    String? note,
  }) async {
    final response = await _dio.patch('/api/accounts/user-caretakers/$linkId/', data: {
      if (active != null) 'active': active,
      if (note != null) 'note': note,
    });
    return response.data;
  }

  Future<void> deleteCaretakerLink(int linkId) async {
    await _dio.delete('/api/accounts/user-caretakers/$linkId/');
  }
}
```

## Setup Instructions

### For Backend Team

1. **Enable accounts URLs**: Uncomment the accounts URL in `main_app/urls.py`:

    ```python
    path('api/accounts/', include('accounts.urls')),
    ```

2. **Add missing User serializers**: The settings reference user serializers that don't exist yet. Add them to `accounts/serializers.py`:

    ```python
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'email', 'full_name', 'phone_number', 'address', 'profile_image']
            read_only_fields = ['id']

    class UserCreateSerializer(serializers.ModelSerializer):
        password = serializers.CharField(write_only=True)

        class Meta:
            model = User
            fields = ['email', 'password', 'full_name', 'phone_number', 'address']
            extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            password = validated_data.pop('password')
            user = User.objects.create_user(password=password, **validated_data)
            return user
    ```

### For Frontend Team

1. **Install Dio package** in your Flutter project:

    ```yaml
    dependencies:
        dio: ^5.3.2
    ```

2. **Use the AccountsService class** provided above as a starting point

3. **Handle token storage** using secure storage packages like `flutter_secure_storage`

4. **Implement proper error handling** for network requests

## Testing the API

You can test the API endpoints using tools like Postman, curl, or the provided Flutter service class. Make sure to:

1. Start with user registration/login to get authentication tokens
2. Include the Bearer token in subsequent requests
3. Use proper Content-Type headers (application/json for JSON, multipart/form-data for file uploads)

## Notes for Beginners

- **Authentication is required** for all endpoints except registration and login
- **Store JWT tokens securely** in your app (use flutter_secure_storage)
- **Handle token expiration** by implementing automatic token refresh
- **Use FormData** for requests that include file uploads (profile images)
- **Always validate user input** before sending requests
- **Implement proper error handling** to show meaningful messages to users
- **Test each endpoint individually** before integrating into your app

## Support

If you encounter any issues or need clarification on any endpoint, please reach out to the backend team with specific details about the problem and the request you're trying to make.
