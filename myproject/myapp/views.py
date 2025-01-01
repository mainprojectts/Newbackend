from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from .serializers import  *
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests 
import requests
import time

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

class googleLogin(APIView):
     permission_classes=[AllowAny]

     def post(self,request):
          Idtoken=request.data.get("id_token")
          print(request.data,"idtokennnnnnnnnn")
         
          if Idtoken is None:
               return Response({"error":"Token is none"})
          try:
            idinfo=id_token.verify_oauth2_token(Idtoken,google_requests.Request())
            print(idinfo,"idinfoooooooo")
            if idinfo['exp'] < time.time():
             return Response({"error": "ID token has expired"}, status=status.HTTP_400_BAD_REQUEST)
            name=idinfo["name"] 
            email=idinfo["email"]
            try:
                    user=User.objects.get(email=email)
                
                   
            except User.DoesNotExist:
                original_username = name
                counter = 1
                new_username = original_username

                while User.objects.filter(username=new_username).exists():
                # Add a number at the front and check again
                    new_username = f"{original_username}{counter}"
                    counter += 1
             
                 
                try:
                    user = User(
                         username=new_username,
                        email=email
                    )

                    user.set_unusable_password()

                    user.save()
                 
                except ValueError as e:
                    return Response({"error of user":e})  
                except Exception as e:
                     return Response({"error": "An unexpected error occurred during user creation: " + str(e)})
                
            refresh=RefreshToken.for_user(user)
            return Response({"refresh":str(refresh),"access":str(refresh.access_token)})

          except ValueError as e:
                    return Response({"error of google":e})  
    

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
            serializer=self.serializer_class(data,many=True,context={"user_id":request.user.id})
            return Response({"data":serializer.data,"message":"Success","status":1},status=status.HTTP_201_CREATED)
        else:              
            ProId=request.GET.get("id")
            if ProId:
                print(ProId,"------------")
                try:
                    data = Product.objects.get(id=ProId)
                    # wishlist=Wishlist.objects.get(product=data,user=request.user)
                    # print(wishlist,"=============================")
                    serializer=self.serializer_class(data,context={"user_id":request.user.id})
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
        productId=request.data.get("cart_product")
        try:
         cartquantity = Cart.objects.get(user=request.user, cart_product=productId).quantity
         print(cartquantity, 'checkcartquantity')
        except Cart.DoesNotExist:
        # Handle the case where the Cart object does not exist
         cartquantity = 0
         print('Cart does not exist for this product')

      
        quantity = data.get("quantity")
        try:
             product=Product.objects.get(id=productId)
        except Product.DoesNotExist:
            return Response({"message": "Product not found", "status": 0}, status=status.HTTP_404_NOT_FOUND)
        prodStock=product.stock
        print(prodStock,"00000000000000")
        print(quantity,"00000000000000")
        if prodStock < quantity:
           return Response({"message": "Maximum quantity exceeded", "status": 0}, status=status.HTTP_400_BAD_REQUEST)
        if cartquantity+quantity > prodStock:
                        return Response({"message": "Not that much stock available", "status": 0}, status=status.HTTP_400_BAD_REQUEST)
        cart_item=Cart.objects.filter(user=request.user,cart_product=product).first()
        if cart_item:
             cart_item.quantity+=quantity
             cart_item.save()
             product.save()
             return Response({"data": CartSerializer(cart_item).data, "message": "Product quantity updated successfully", "status": 1}, status=status.HTTP_200_OK)
        else:
             data['user'] = request.user.id 
             serializer = self.serializer_class(data=data, context={'request': request})
             if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data, "message": "Product added to cart successfully", "status": 1}, status=status.HTTP_201_CREATED)
             return Response({"data": serializer.errors, "message": "Failed to add the product to cart", "status": 0}, status=status.HTTP_400_BAD_REQUEST)


        


        # if(ProdStock>=data["quantity"]):
        #     if(product.id.includes()):
        #          #increase the quantity
        #     serializer = self.serializer_class(data=data, context={'request': request})
        #     if serializer.is_valid():
        #         # serializer["user"]=request.user.id    
        #         serializer.save()
        #         return Response({"data":serializer.data,"message":"Product added to cart successfully","status":1},status=status.HTTP_201_CREATED)
        #     return Response({"data":serializer.errors,"message":"Failed to add the product to cart","status":0},status=status.HTTP_400_BAD_REQUEST)
        # return Response({"message":"Maximum quantity added","status":0},status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request):
        user=request.user
        print(user,"************")
        try:    
                TotalProducts=[]
                cart_items=Cart.objects.filter(user=user)
                for item in cart_items:
                     product=Product.objects.get(id=item.cart_product.id)
                     print(product.image,'-----------------------')
                     product_details={  
                          "product_id":item.cart_product.id,
                          "product_name":item.cart_product.name,
                          "product_price":item.cart_product.price,
                          "total_quantity":item.quantity,
                          "total_price":item.total_price,
                          "image":product.image
                     }
                     TotalProducts.append(product_details)
                serializer=self.serializer_class_product(TotalProducts,many=True)
                return Response({"data":serializer.data,"message":"succes","status":1},status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
                return Response({"message":"Cart does not exists","status":0},status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
                     return Response({"error":str(e),"message":"failed","status":0},status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request):
        productId=request.GET.get("product")
        if productId:
             try:
                  product=Cart.objects.get(cart_product=productId,user=request.user)
                  product.delete()
                  return Response({"message":"Product removed from cart successfully","status":1},status=status.HTTP_200_OK)
             except Cart.DoesNotExist:
                  return Response({"message":"Product not found","status":0},status=status.HTTP_400_BAD_REQUEST)
        else:
               return Response({"message":"Product not found","status":0},status=status.HTTP_400_BAD_REQUEST)

                   
    
class Wishlistview(APIView):
     serializer_class=WishlistSerializer
     serializer_class_wishlist=wishlistProductSerializer
     
     def post(self,request):
          data=request.data
          wishlistdata=Wishlist.objects.filter(user=request.user.id,product_id=data["product"]).first()
          if wishlistdata:
                return Response({"message":"Item already exists","status":2},status=status.HTTP_400_BAD_REQUEST)
          else:    
            data["user"]=request.user.id
            serializer=self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data":serializer.data,"message":"Product add to wishlist successfully","status":1},status=status.HTTP_201_CREATED)
            return Response({"error":serializer.errors,"message":"Product add to wishlist failed","status":0},status=status.HTTP_400_BAD_REQUEST)
    
     def get(self,request):
          user=request.user
          try:
               TotalProducts=[]
               products=Wishlist.objects.filter(user=user)
               for item in products:
                    # product=Product.objects.filter(id=item.product.id)
                    product_details={
                         "product_id":item.product.id,
                         "product_name":item.product.name,
                         "product_price":item.product.price,
                         "image":item.product.image
                    }
                    TotalProducts.append(product_details)
               serializer=self.serializer_class_wishlist(TotalProducts,many=True)
               return Response({"data":serializer.data,"message":"success","status":1},status=status.HTTP_200_OK)

          except Exception as e:
                     return Response({"error":str(e),"message":"failed","status":0},status=status.HTTP_400_BAD_REQUEST)
               
     def delete(self,request):
            productId=request.GET.get("product")
            if productId:
                try:
                    wihlist=Wishlist.objects.get(product=productId,user=request.user)
                    wihlist.delete()
                    return Response({"message":"Product removed from wishlist","status":1},status=status.HTTP_200_OK)
                except Wishlist.DoesNotExist:
                    return Response({"message":"Product not found","status":2},status=status.HTTP_404_NOT_FOUND)
            else:
             return Response({"message":"Product not found","status":3},status=status.HTTP_404_NOT_FOUND)

