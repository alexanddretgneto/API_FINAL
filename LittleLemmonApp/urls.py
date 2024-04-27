from django.urls import include, path
from .views import CategoryViewSet, GroupDeliveryCrewUsersViewSet, GroupManagerUsersViewSet, MenuItemViewSet, CartItemViewSet, OrderViewSet, OrderItemViewSet, UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'carts', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups/manager/users', GroupManagerUsersViewSet, basename='group-manager-users')
router.register(r'groups/delivery-crew/users', GroupDeliveryCrewUsersViewSet, basename='group-delivery-crew-users')

urlpatterns = [
    path('', include(router.urls)),
    path('menu-items/<int:pk>/add-to-cart/', CartItemViewSet.as_view({'post': 'create'}), name='add-to-cart'),
]

urlpatterns += router.urls
