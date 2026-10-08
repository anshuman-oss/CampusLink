from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers
from jobs.models import Company
from .models import Notification, User


def strong_password(pw, field="password"):
    try:
        validate_password(pw)
    except DjangoValidationError as e:
        raise serializers.ValidationError({field: list(e.messages)})


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "title", "message", "is_read", "created_at"]


class RegisterSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["student", "recruiter"])   # officer/mentor impossible
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    roll_no = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=60)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=60)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)
    company_name = serializers.CharField(required=False, allow_blank=True, max_length=100)

    def validate(self, d):
        strong_password(d["password"])
        email = d["email"].strip().lower()
        d["email"] = email
        if d["role"] == "student":
            roll = (d.get("roll_no") or "").strip()
            if not roll:
                raise serializers.ValidationError({"roll_no": "Roll number is required."})
            u = User.objects.filter(role="student", email__iexact=email,
                                    profile__roll_no__iexact=roll, profile__is_active=True).first()
            if not u or u.has_usable_password():
                raise serializers.ValidationError(
                    "This roll number and email were not found in the college roster, or the "
                    "account is already activated. Please contact the placement cell.")
            self.student = u
        else:
            for f in ("username", "first_name", "company_name"):
                if not (d.get(f) or "").strip():
                    raise serializers.ValidationError({f: "This field is required."})
            if User.objects.filter(username__iexact=d["username"].strip()).exists():
                raise serializers.ValidationError({"username": "This username is already taken."})
            if User.objects.filter(email__iexact=email).exists():
                raise serializers.ValidationError({"email": "An account with this email already exists."})
        return d

    @transaction.atomic
    def create(self, d):
        if d["role"] == "student":
            u = self.student
            u.set_password(d["password"])
            u.save(update_fields=["password"])
            return u
        u = User(username=d["username"].strip(), email=d["email"], role="recruiter",
                 first_name=d["first_name"].strip(), last_name=(d.get("last_name") or "").strip(),
                 phone=d.get("phone", ""), is_approved=False)
        u.set_password(d["password"])
        u.save()
        Company.objects.create(user=u, name=d["company_name"].strip(), contact_email=d["email"])
        return u


class StaffCreateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["mentor", "officer"])
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=60)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=60)
    email = serializers.EmailField()

    def validate(self, d):
        strong_password(d["password"])
        if User.objects.filter(username__iexact=d["username"]).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        return d

    def create(self, d):
        u = User(username=d["username"], email=d["email"].lower(), role=d["role"],
                 first_name=d["first_name"], last_name=d.get("last_name", ""), is_approved=True)
        u.set_password(d["password"])
        u.save()
        return u


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=60)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=60)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)
    company_name = serializers.CharField(required=False, max_length=100)    # recruiters only
    industry = serializers.CharField(required=False, allow_blank=True, max_length=60)