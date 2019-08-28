from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return obj.user == request.user

class IsInFriendship(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj.user1 == request.user or obj.user2 == request.user

class IsOwnerOrFriend(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = obj.user
        return user == request.user or Friendship.objects.filter(
                Q(user1=request.user, user2=user) |
                Q(user2=request.user, user1=user)
               ).filter(is_accepted=True).exists()

class IsFriendOrMyself(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return obj == request.user or Friendship.objects.filter(
                Q(user1=request.user, user2=obj) |
                Q(user2=request.user, user1=obj)
               ).filter(is_accepted=True).exists()