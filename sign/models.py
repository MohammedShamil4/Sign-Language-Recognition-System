from django.db import models


# Create your models here.
class Login(models.Model):
    username = models.CharField(max_length=90)
    password = models.CharField(max_length=90)
    type = models.CharField(max_length=90)


class Staff(models.Model):
    st_id = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=90)
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=90)
    post = models.CharField(max_length=90)
    pin = models.IntegerField()
    phone_number = models.BigIntegerField()
    email = models.CharField(max_length=90)


class Parent(models.Model):
    pt_id = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=90)
    dob = models.DateField()
    gender = models.CharField(max_length=10)
    address = models.CharField(max_length=90)
    post = models.CharField(max_length=90)
    pin = models.IntegerField()
    phone_number = models.BigIntegerField()
    email = models.CharField(max_length=90)


class Study(models.Model):
    st_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    materials = models.CharField(max_length=90)
    date = models.DateField()
    description = models.CharField(max_length=100)


class Tip(models.Model):
    st_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    tip = models.CharField(max_length=90)
    date = models.DateField()


class Class(models.Model):
    st_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    work = models.CharField(max_length=90)
    description = models.CharField(max_length=100)
    date = models.DateField()


class Review(models.Model):
    pt_id = models.ForeignKey(Parent, on_delete=models.CASCADE)
    review = models.CharField(max_length=90)
    rating = models.CharField(max_length=90)


class Chat(models.Model):
    fromid = models.ForeignKey(Login, on_delete=models.CASCADE,related_name='fromid')
    toid = models.ForeignKey(Login, on_delete=models.CASCADE,related_name='toid')
    message = models.CharField(max_length=90)
    date = models.DateField()


class Feedback(models.Model):
    st_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    pt_id = models.ForeignKey(Parent, on_delete=models.CASCADE)
    feedback = models.CharField(max_length=90)
    date = models.DateField()
