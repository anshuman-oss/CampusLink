from rest_framework.permissions import BasePermission
def role_required(*roles):
    class _Perm(BasePermission):
        def has_permission(self, request, view):
            return request.user.is_authenticated and request.user.role in roles
    return _Perm
IsOfficer = role_required("officer")
IsRecruiter = role_required("recruiter", "officer")
IsStudent = role_required("student")
IsStaffRole = role_required("officer", "mentor")