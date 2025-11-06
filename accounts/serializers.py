from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

 #this is the serializer for userdetail
class UserSerializer(serializers.ModelSerializer):
 #full_name is not an actual field in or model . it is being added manally to the serializer as an extra field.
  full_name = serializers.ReadOnlyField()

  class Meta:
    model = User
    fields = [
      'id','username','email','first_name','last_name','full_name',
      'bio','avatar','status','last_seen',
      'created_at'
    ]

    read_only_fields = ['id','created_at','last_seen']

#This is the serializer for user registration
class UserRegistrationSerializer(serializers.ModelSerializer):
  password = serializers.CharField(
    write_only = True,
    required = True,
    validators = [validate_password]
  )
  password2 = serializers.CharField(write_only = True, required = True)
  class Meta:
    model = User
    fields = [
      'username','email','password','password2',
      'first_name','last_name'
    ]

    def validate(self,attrs):
      if attrs['password'] != attrs['password2']:
        raise serializers.ValidationError({
          "password":"Password fields didn't match."
        })
      return attrs
    
    def create(self,validated_data):
      validate_password.pop('password2')
      user = User.objects.create_user(**validated_data)
      return user

#Serializer for updating user profile

class UserUpdateSerialzer(serializers.ModelSerializer):

  class Meta:
    model = User
    fields = [
      'username','first_name','last_name','bio',
      'avatar','status'
    ]

#Serializer for password change

class ChangePasswordSerializer(serializers.Serializer):

  old_password = serializers.CharField(required = True)
  new_password = serializers.CharField(
    required = True,
    validators = [validate_password]
  )

  def validate_old_password(self,value):
    user = self.context['request'].user
    if not user.check_password(value):
      raise serializers.ValidationError("Old password is incorrect")
    return value