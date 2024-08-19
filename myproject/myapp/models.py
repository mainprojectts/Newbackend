from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Note(models.Model):
    title=models.CharField(max_length=30)
    content=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name="notes")

    def __str__(self):
        return self.title
    
class Brand(models.Model):
    STATUS_CHOICES=(
        ("active","Active"),
        ("inactive","Inactive")
    )
    name=models.CharField(max_length=30)
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default="active")

    def __str__(self):
        return self.name

class Category(models.Model):
    STATUS_CHOICES=(
        ("active","Active"),
        ("inactive","Inactive")
    )
    name=models.CharField(max_length=30)
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default="active")

    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES=(
        ("active","Active"),
        ("inactive","Inactive")
    )
    RATING_CHOICE=((1,1),(2,2),(3,3),(4,4),(5,5))
    name=models.CharField(max_length=30)
    price=models.IntegerField()
    status=models.CharField(max_length=10,choices=STATUS_CHOICES,default="active")
    description=models.TextField()
    brand=models.ForeignKey(Brand,on_delete=models.CASCADE,null=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    image=models.ImageField(upload_to="images/products/",null=True)
    rating = models.IntegerField(choices=RATING_CHOICE,null=True)  # New field added


    def __str__(self):
        return self.name