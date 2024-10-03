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
        extra_kwargs={"author":{"read_only":True}}


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'images']
        
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    is_wishlist=serializers.SerializerMethodField()
    class Meta:
        model=Product
        fields=["id","name","price","status","description","brand","category","created_at","image","rating","images","stock","is_wishlist"]
    def get_is_wishlist(self,obj):
        userId=self.context.get("user_id")
        if userId:
            return Wishlist.objects.filter(product=obj,user_id=userId).exists()
        return False
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields=["id","cart_product","created_at","quantity","total_price"]


    def create(self,validated_data):
        validated_data["user"]=self.context["request"].user
        print(validated_data,'check-------------------------')
        return Cart.objects.create(**validated_data)
    
class WishlistSerializer(serializers.ModelSerializer):

    class Meta:
        model=Wishlist
        fields=["id","product","created_at","user"]


class wishlistProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image=serializers.ImageField()
class ProductCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    total_quantity  = serializers.IntegerField()
    product_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    image=serializers.ImageField()

