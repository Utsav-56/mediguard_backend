from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from .models import User, Caretaker, UserCaretaker


class UserCreateSerializer(BaseUserCreateSerializer):
    full_name = serializers.CharField(required=True)
    profile_image = serializers.ImageField(
        required=False, allow_null=True
    )  # ✅ optional

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "password",
            "full_name",
            "phone_number",
            "address",
            "timezone",
            "profile_image",
        )
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}


class UserSerializer(BaseUserSerializer):
    profile_image = serializers.SerializerMethodField()  # ✅ return absolute URL

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone_number",
            "address",
            "timezone",
            "profile_image",
        )

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image:
            return request.build_absolute_uri(obj.profile_image.url)
        return None


class CaretakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caretaker
        fields = [
            'id', 'full_name', 'phone_number', 'email', 'address',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserCaretakerSerializer(serializers.ModelSerializer):
    caretaker = CaretakerSerializer(read_only=True)
    caretaker_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = UserCaretaker
        fields = [
            'id', 'caretaker', 'caretaker_id', 'can_view_medicines', 
            'can_add_medicines', 'can_edit_medicines', 'can_delete_medicines',
            'can_view_health_metrics', 'can_add_health_metrics', 
            'can_confirm_intakes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        caretaker_id = validated_data.pop('caretaker_id')
        try:
            caretaker = Caretaker.objects.get(id=caretaker_id)
            validated_data['caretaker'] = caretaker
        except Caretaker.DoesNotExist:
            raise serializers.ValidationError({'caretaker_id': 'Caretaker not found'})
        
        return super().create(validated_data)


class CaretakerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new caretaker and linking to user"""
    # Permission fields for the link
    can_view_medicines = serializers.BooleanField(default=True)
    can_add_medicines = serializers.BooleanField(default=False)
    can_edit_medicines = serializers.BooleanField(default=False)
    can_delete_medicines = serializers.BooleanField(default=False)
    can_view_health_metrics = serializers.BooleanField(default=True)
    can_add_health_metrics = serializers.BooleanField(default=False)
    can_confirm_intakes = serializers.BooleanField(default=True)

    class Meta:
        model = Caretaker
        fields = [
            'full_name', 'phone_number', 'email', 'address',
            'can_view_medicines', 'can_add_medicines', 'can_edit_medicines', 
            'can_delete_medicines', 'can_view_health_metrics', 
            'can_add_health_metrics', 'can_confirm_intakes'
        ]

    def create(self, validated_data):
        # Extract permission fields
        permission_fields = {
            'can_view_medicines': validated_data.pop('can_view_medicines', True),
            'can_add_medicines': validated_data.pop('can_add_medicines', False),
            'can_edit_medicines': validated_data.pop('can_edit_medicines', False),
            'can_delete_medicines': validated_data.pop('can_delete_medicines', False),
            'can_view_health_metrics': validated_data.pop('can_view_health_metrics', True),
            'can_add_health_metrics': validated_data.pop('can_add_health_metrics', False),
            'can_confirm_intakes': validated_data.pop('can_confirm_intakes', True),
        }

        # Create caretaker
        caretaker = super().create(validated_data)

        # Create UserCaretaker link
        UserCaretaker.objects.create(
            user=self.context['request'].user,
            caretaker=caretaker,
            **permission_fields
        )

        return caretaker
