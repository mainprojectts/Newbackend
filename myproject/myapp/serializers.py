from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","username","password"]
        extra_kwargs={"password":{"write_only":True}}

    def create(self,validated_data):
        user=User(username=validated_data['username'])
        print(validated_data["password"],'----------------')
        user.set_password(validated_data['password'])   
        user.save()
        return user

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Note
        fields=["id","title","content","created_at","author"]
        # extra_kwargs={"author":{"read_only":True}}