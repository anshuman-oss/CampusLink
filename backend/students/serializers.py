from django.db import transaction
from rest_framework import serializers
from accounts.models import User
from .models import StudentProfile
from .services import refresh_readiness

BRANCHES = ["CSE", "IT", "ECE", "EEE", "ME", "CE"]


class StudentSerializer(serializers.ModelSerializer):
    """The student's own view: they can edit only target_role, skills, projects, certifications."""
    name = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ["id", "name", "roll_no", "branch", "cgpa", "backlogs", "aptitude_score",
                  "mock_score", "soft_score", "target_role", "skills", "projects",
                  "certifications", "readiness_score", "readiness_level", "placed", "batch"]
        read_only_fields = ["roll_no", "branch", "cgpa", "backlogs", "aptitude_score",
                            "mock_score", "soft_score", "readiness_score", "readiness_level",
                            "placed", "batch"]

    def get_name(self, o):
        return o.user.get_full_name() or o.user.username


class RosterSerializer(serializers.ModelSerializer):
    """The officer's view: create and edit students, scores and mentor."""
    first_name = serializers.CharField(source="user.first_name", max_length=60)
    last_name = serializers.CharField(source="user.last_name", max_length=60, required=False, allow_blank=True)
    email = serializers.EmailField(source="user.email")
    mentor_name = serializers.SerializerMethodField()
    activated = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = ["id", "roll_no", "first_name", "last_name", "email", "branch", "cgpa", "backlogs",
                  "batch", "aptitude_score", "mock_score", "soft_score", "mentor", "mentor_name",
                  "readiness_score", "readiness_level", "placed", "activated", "skills"]
        read_only_fields = ["readiness_score", "readiness_level", "placed", "skills"]
        extra_kwargs = {"roll_no": {"validators": []}}

    def get_mentor_name(self, o):
        return (o.mentor.get_full_name() or o.mentor.username) if o.mentor else None

    def get_activated(self, o):
        return o.user.has_usable_password()

    def validate_roll_no(self, v):
        v = v.strip()
        if self.instance is None and (User.objects.filter(username__iexact=v).exists()
                                      or StudentProfile.all_objects.filter(roll_no__iexact=v).exists()):
            raise serializers.ValidationError("This roll number is already on the roster.")
        return v

    def validate_branch(self, v):
        v = v.strip().upper()
        if v not in BRANCHES:
            raise serializers.ValidationError(f"Branch must be one of: {', '.join(BRANCHES)}.")
        return v

    def validate_cgpa(self, v):
        if not 0 <= v <= 10:
            raise serializers.ValidationError("CGPA must be between 0 and 10.")
        return v

    def validate(self, d):
        for f in ("aptitude_score", "mock_score", "soft_score"):
            if f in d and not 0 <= d[f] <= 100:
                raise serializers.ValidationError({f: "Score must be between 0 and 100."})
        return d

    @transaction.atomic
    def create(self, v):
        ud = v.pop("user")
        u = User(username=v["roll_no"], email=ud["email"].lower(), role="student",
                 first_name=ud["first_name"], last_name=ud.get("last_name", ""))
        u.set_unusable_password()          # the student sets it when activating
        u.save()
        p = StudentProfile.objects.create(user=u, **v)
        refresh_readiness(p)
        return p

    @transaction.atomic
    def update(self, inst, v):
        ud = v.pop("user", {})
        v.pop("roll_no", None)             # the roll number is the login name: never changes
        u = inst.user
        for k in ("first_name", "last_name", "email"):
            if k in ud:
                setattr(u, k, ud[k].lower() if k == "email" else ud[k])
        u.save()
        for k, val in v.items():
            setattr(inst, k, val)
        inst.save()
        refresh_readiness(inst)
        return inst