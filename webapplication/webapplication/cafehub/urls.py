from django.urls import path
from . import views

urlpatterns = [
    # frontend pages
    path("", views.details, name="details"),
    path("cafe-data/", views.show_cafe_data, name="cafe_data"),

    # django superuser admin
    # Admin authentication
    path('api/admin/login/', views.admin_login, name='admin_login'),
    
    # Admin dashboard
    path('api/admin/dashboard-stats/', views.admin_dashboard_stats, name='admin_dashboard_stats'),
    path('api/admin/users/', views.admin_users_list, name='admin_users_list'),
    path('api/admin/vendors/', views.admin_vendors_list, name='admin_vendors_list'),
    
    # Admin actions
    path('api/admin/users/<int:user_id>/status/', views.admin_update_user_status, name='admin_update_user_status'),
    path('api/admin/vendors/<int:vendor_id>/verify/', views.admin_verify_vendor, name='admin_verify_vendor'),
    
    # Regular user endpoints
    path('api/register/', views.register, name='register'),
    path('api/login/', views.user_login, name='user_login'),
    path('api/logout/', views.user_logout, name='user_logout'),
    path('api/user/', views.get_current_user, name='get_current_user'),
    
    # Vendor registration
    path('api/vendors/register/', views.vendor_register, name='vendor_register'),
    
    # Data endpoints
    path('api/cafes/', views.get_cafes, name='get_cafes'),
    path('api/products/', views.get_products, name='get_products'),
    path('api/coupons/', views.get_coupons, name='get_coupons'),
    path('api/stats/', views.get_stats, name='get_stats'),
]