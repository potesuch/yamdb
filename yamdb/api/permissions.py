from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Право доступа: Только для администратора.

    Пользователь должен быть аутентифицирован и являться администратором.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin
            or request.user.is_authenticated and request.user.is_staff
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Право доступа: Администратор или только чтение.

    Пользователь может выполнять любые действия в безопасных методах HTTP
    или должен быть аутентифицирован и являться администратором для остальных методов.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated and request.user.is_admin
        )


class IsAuthorOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """
    Право доступа: Автор, администратор, модератор или только чтение.

    Пользователь может выполнять любые действия в безопасных методах HTTP
    или должен быть аутентифицирован и соответствовать одной из ролей: автор,
    администратор, модератор, персонал.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
            and request.user == obj.author
            or request.user.is_admin
            or request.user.is_moderator
            or request.user.is_staff
        )
