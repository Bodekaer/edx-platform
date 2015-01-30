import hashlib

from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework import serializers

from student.models import UserProfile


def get_username(email, length=10):
    string = "{}{}".format(email, timezone.now().isoformat())
    return hashlib.sha1(string).hexdigest()[:length]


class UserCreateSerializer(serializers.Serializer):

    id = serializers.Field()
    email = serializers.EmailField()

    def validate_email(self, attrs, source):
        value = attrs[source]
        if value and User.objects.filter(email__iexact=value.strip()).exists():
            raise serializers.ValidationError("Email is used")

        return attrs

    def save_object(self, *args, **kwargs):
        self.object.username = get_username(self.object.email)
        self.object.set_unusable_password()
        self.object.save()

        return self.object

    def restore_object(self, attrs, instance=None):
        if instance:
            instance.email = attrs.get('email', instance.email)
            return instance

        return User(**attrs)


class CustomLabsterUser(object):

    def __init__(self, *args, **kwargs):
        for field in kwargs.keys():
            setattr(self, field, kwargs.get(field))

    def save(self):
        user = User.objects.get(id=self.id)

        labster_user = user.labster_user
        labster_user.nationality = self.nationality
        labster_user.language = self.language
        labster_user.unique_id = self.unique_id
        labster_user.date_of_birth = self.date_of_birth
        labster_user.user_type = self.user_type
        labster_user.phone_number = self.phone_number
        labster_user.user_school_level = self.user_school_level
        labster_user.save()

        profile = UserProfile.objects.get(user=user)
        profile.name = self.name
        profile.gender = self.gender
        profile.level_of_education = self.level_of_education
        profile.year_of_birth = self.year_of_birth
        profile.save()

        password = getattr(self, 'password', None)
        if password:
            user.set_password(password)
            user.save()

        return user


class LabsterUserSerializer(serializers.Serializer):

    id = serializers.Field()
    user_id = serializers.Field()
    is_labster_verified = serializers.Field()
    nationality_name = serializers.Field()

    date_of_birth = serializers.DateField(required=False)
    nationality = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
    unique_id = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)
    level_of_education = serializers.CharField(required=False)
    year_of_birth = serializers.IntegerField(required=False)
    user_type = serializers.IntegerField(required=False)
    user_school_level = serializers.IntegerField(required=False)
    phone_number = serializers.CharField(required=False)

    def save_object(self, *args, **kwargs):
        self.object.save()
        return self.object

    def restore_object(self, attrs, instance=None):
        if instance:
            fields = [
                'unique_id',
                'nationality',
                'language',
                'date_of_birth',
                'user_type',
                'user_school_level',
                'phone_number',
                'name',
                'gender',
                'level_of_education',
                'year_of_birth',
            ]

            for field in fields:
                setattr(instance, field, attrs.get(field, getattr(instance, field)))

            return instance

        return CustomLabsterUser(**attrs)
