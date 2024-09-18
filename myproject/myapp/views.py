from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

# Create your views here.

class CreateUserview(APIView):
    serializer_class=UserSerializer
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data,"message":"User created successfully","status":1},status=status.HTTP_201_CREATED)
        else:
            return Response({"data":serializer.errors,"message":"Create user failed","status":0},status=status.HTTP_400_BAD_REQUEST)


# class GetuserDetailview(APIView):
#      serializer_class=UserSerializer
#      permission_classes=[IsAuthenticated]
#      def get(self,request):
#           print(request.user.id,'checkuser===================')
#           Userdata=User.objects.get(id=request.user.id)
#           serializer=self.serializer_class(Userdata)
#           return Response({"data":serializer.data,"message":"Success","status":1},status=status.HTTP_200_OK)
          
     
     
class NoteListcreate(APIView):
    serializer_class=NoteSerializer
    permission_classes=[IsAuthenticated]
    def post(self,request):
        print(request.user)
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response({"data":serializer.data,"message":"Note created Successfully","status":1})
        else:
            return Response({"data":serializer.errors,"message":"Failed to create the notes","status":0})
    
    def get(self,request):
        user=request.user
        Type=request.GET.get("type")
        if Type=="all":
            data=Note.objects.filter(author=user).order_by("-created_at")
            serializer=self.serializer_class(data,many=True)
        else:
            noteId=request.data['noteId']
            data=Note.objects.filter(author=user,id=noteId)
            serializer=self.serializer_class(data,many=True)
        return Response({"data":serializer.data,"message":"Success","status":1})
    
    def delete(self,request):
        noteId=request.data.get("noteId")
        if noteId:
            try:
                note=Note.objects.get(id=noteId)
                note.delete()
                return Response({"message": "Task deleted successfully", "status": 1}, status=status.HTTP_200_OK)
            except Note.DoesNotExist:
                return Response({"message":"Task not found","status":0},status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Task not found", "status": 0}, status=status.HTTP_404_NOT_FOUND)


class LogoutView(APIView):
    def post(self,request):
        try:
            refresh_token = request.data["refresh_token"]
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message":"Blacklisted refresh token successfully"},status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"message":"Blacklisted failed"},status=status.HTTP_400_BAD_REQUEST)
        
class ProductView(APIView):
    serializer_class=ProductSerializer
    permission_classes=[IsAuthenticated]
    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            product=serializer.save()
            productImages = request.FILES.getlist('product_images')
            print(productImages,'==================')
            for i in productImages:
                ProductImage.objects.create(product=product,images=i)
    
            return Response({"data":serializer.data,"message":"Product added successfully","status":1},status=status.HTTP_201_CREATED)
        return Response({"data":serializer.errors,"message":"Failed","status":0},status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        Type=request.GET.get("type")
        if Type=="all":
            data=Product.objects.all()
            serializer=self.serializer_class(data,many=True)
            return Response({"data":serializer.data,"message":"Success","status":1},status=status.HTTP_201_CREATED)
        else:              
            ProId=request.GET.get("id")
            if ProId:
                print(ProId,"------------")
                try:
                    data = Product.objects.get(id=ProId)
                    serializer=self.serializer_class(data)
                    return Response({"data":serializer.data,"message":"Success","status":2},status=status.HTTP_200_OK)
                except Product.DoesNotExist:
                        return Response({"message":"Id is invalid","status":0})
            else:
                  return Response({"message":"Id is not provided","status":0})

class CartView(APIView):
    serializer_class=CartSerializer
    serializer_class_product=ProductCartSerializer
    permission_classes=[IsAuthenticated]
    def post(self,request):
        data=request.data
        serializer = self.serializer_class(data=data, many=True, context={'request': request})
        if serializer.is_valid():
            # serializer["user"]=request.user.id
            serializer.save()
            return Response({"data":serializer.data,"message":"Product added to cart successfully","status":1},status=status.HTTP_201_CREATED)
        return Response({"data":serializer.errors,"message":"Failed to add the product to cart","status":0},status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):
        user=request.GET.get("user_id")
        try:    
                TotalProducts=[]
                cart_items=Cart.objects.filter(user=user)
                for item in cart_items:
                     product_details={  
                          "product_id":item.cart_product.id,
                          "product_name":item.cart_product.name,
                          "product_price":item.cart_product.price,
                          "total_quantity":item.quantity,
                          "total_price":item.total_price
                     }
                     TotalProducts.append(product_details)
                serializer=self.serializer_class_product(TotalProducts,many=True)
                return Response({"data":serializer.data,"message":"succes","status":1},status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
                return Response({"message":"Cart does not exists","status":0},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
                     return Response({"error":str(e),"message":"failed","status":0},status=status.HTTP_400_BAD_REQUEST)

    
