

class ReadOnlyForStaffMixin:

    def has_add_permission(self, request):
        return bool(request.user.is_superuser)

    def has_change_permission(self, request, obj=None):
        return bool(request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_superuser)

    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)
        return [f.name for f in self.model._meta.fields] + list(getattr(self, "readonly_fields", []))
