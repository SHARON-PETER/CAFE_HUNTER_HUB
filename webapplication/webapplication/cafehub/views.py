from django.shortcuts import render
def details(request):
    return render(request,"success.html")
    


# Create your views here.
from django.shortcuts import render
from .models import CafeHubDatabase

def show_cafe_data(request):
    data = CafeHubDatabase.objects.all()[:100]  # Show first 100 records
    return render(request, "cafe_data.html", {"cafe_data": data})


#django Admin Authentication
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import json
import uuid

from .models import Vendor, Cafe, Coupon, Transaction, Order, ProductReview, FavoriteCafe, UserActivity

# ===== ADMIN VIEWS =====

@csrf_exempt
# In cafehub/views.py, find the existing admin_login function and replace it with this:

@csrf_exempt
def admin_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username') or data.get('email')  # Accept either
            password = data.get('password')
            
            # Try to find user by username or email
            try:
                if '@' in username:
                    user = User.objects.get(email=username)
                    username = user.username
                else:
                    user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_superuser:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': 'admin',
                        'is_superuser': user.is_superuser,
                        'date_joined': user.date_joined.isoformat(),
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid credentials or not a superuser'
                }, status=401)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@staff_member_required
def admin_dashboard_stats(request):
    """Get all admin dashboard statistics"""
    try:
        # Time period filters
        days = int(request.GET.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # User statistics
        total_users = User.objects.count()
        new_users = User.objects.filter(date_joined__gte=start_date).count()
        
        # Vendor statistics
        total_vendors = Vendor.objects.count()
        verified_vendors = Vendor.objects.filter(is_verified=True).count()
        pending_vendors = Vendor.objects.filter(is_verified=False).count()
        
        # Cafe statistics
        total_cafes = Cafe.objects.count()
        partner_cafes = Cafe.objects.filter(is_partner=True).count()
        avg_rating = Cafe.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Coupon statistics
        active_coupons = Coupon.objects.filter(
            valid_until__gte=timezone.now(),
            status='active'
        ).count()
        total_coupons = Coupon.objects.count()
        total_redeemed = Coupon.objects.aggregate(Sum('times_used'))['times_used__sum'] or 0
        
        # Transaction statistics
        transactions = Transaction.objects.filter(date__gte=start_date)
        total_revenue = transactions.aggregate(Sum('platform_commission'))['platform_commission__sum'] or 0
        total_transaction_amount = transactions.aggregate(Sum('transaction_amount'))['transaction_amount__sum'] or 0
        avg_order = transactions.aggregate(Avg('transaction_amount'))['transaction_amount__avg'] or 0
        platform_fees = transactions.aggregate(Sum('platform_commission'))['platform_commission__sum'] or 0
        vendor_payouts = transactions.aggregate(Sum('vendor_share'))['vendor_share__sum'] or 0
        
        # City distribution
        city_stats = Cafe.objects.values('city').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # User growth (last 30 days)
        user_growth = []
        for i in range(30):
            day = timezone.now() - timedelta(days=i)
            count = User.objects.filter(
                date_joined__date=day.date()
            ).count()
            user_growth.append({
                'date': day.date().isoformat(),
                'count': count
            })
        
        # Activity stats (last 7 days)
        activity_stats = []
        for i in range(7):
            day = timezone.now() - timedelta(days=i)
            login_count = UserActivity.objects.filter(
                activity_type='login',
                created_at__date=day.date()
            ).count()
            order_count = Order.objects.filter(
                created_at__date=day.date()
            ).count()
            activity_stats.append({
                'date': day.date().isoformat(),
                'logins': login_count,
                'orders': order_count
            })
        
        return JsonResponse({
            'stats': {
                'total_users': total_users,
                'new_users': new_users,
                'vendors': total_vendors,
                'verified_vendors': verified_vendors,
                'pending_vendors': pending_vendors,
                'total_cafes': total_cafes,
                'partner_cafes': partner_cafes,
                'avg_rating': round(avg_rating, 1),
                'active_coupons': active_coupons,
                'total_coupons': total_coupons,
                'total_redeemed': total_redeemed,
                'total_revenue': float(total_revenue),
                'total_transaction_amount': float(total_transaction_amount),
                'platform_fees': float(platform_fees),
                'vendor_payouts': float(vendor_payouts),
                'avg_order_value': float(avg_order),
            },
            'city_distribution': list(city_stats),
            'user_growth': user_growth,
            'activity_stats': activity_stats
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def admin_users_list(request):
    """Get paginated list of users with filters"""
    try:
        # Get filter parameters
        search = request.GET.get('search', '')
        status = request.GET.get('status', 'all')
        role = request.GET.get('role', 'all')
        page = int(request.GET.get('page', 1))
        page_size = 20
        
        # Base queryset
        users = User.objects.all()
        
        # Apply filters
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if status != 'all':
            is_active = status == 'active'
            users = users.filter(is_active=is_active)
        
        if role != 'all':
            if role == 'vendor':
                users = users.filter(vendor_profile__isnull=False)
            elif role == 'customer':
                users = users.filter(vendor_profile__isnull=True)
        
        # Get total count
        total = users.count()
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        
        users_data = []
        for user in users[start:end]:
            # Get user stats
            orders_count = Order.objects.filter(user=user).count()
            total_spent = Order.objects.filter(user=user, status='delivered').aggregate(Sum('final_amount'))['final_amount__sum'] or 0
            reviews_count = ProductReview.objects.filter(user=user).count()
            favorites_count = FavoriteCafe.objects.filter(user=user).count()
            
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name(),
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff,
                'is_vendor': hasattr(user, 'vendor_profile'),
                'vendor_id': user.vendor_profile.vendor_id if hasattr(user, 'vendor_profile') else None,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'orders_count': orders_count,
                'total_spent': float(total_spent),
                'reviews_count': reviews_count,
                'favorites_count': favorites_count,
            })
        
        return JsonResponse({
            'users': users_data,
            'total': total,
            'page': page,
            'pages': (total + page_size - 1) // page_size
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
def admin_vendors_list(request):
    """Get paginated list of vendors with analytics"""
    try:
        vendors = Vendor.objects.all().select_related('user')
        
        vendors_data = []
        for vendor in vendors:
            cafes_count = Cafe.objects.filter(vendor=vendor).count()
            coupons_count = Coupon.objects.filter(vendor=vendor).count()
            active_coupons = Coupon.objects.filter(vendor=vendor, status='active').count()
            
            transactions = Transaction.objects.filter(vendor=vendor)
            total_revenue = transactions.aggregate(Sum('vendor_share'))['vendor_share__sum'] or 0
            total_transactions = transactions.count()
            avg_transaction = transactions.aggregate(Avg('transaction_amount'))['transaction_amount__avg'] or 0
            
            orders_count = Order.objects.filter(vendor=vendor).count()
            
            vendors_data.append({
                'id': vendor.id,
                'vendor_id': vendor.vendor_id,
                'cafe_name': vendor.cafe_name,
                'owner_name': vendor.owner_name,
                'email': vendor.email,
                'phone': vendor.phone,
                'address': vendor.address,
                'city': vendor.city,
                'state': vendor.state,
                'pincode': vendor.pincode,
                'gst_number': vendor.gst_number,
                'years_in_business': vendor.years_in_business,
                'is_verified': vendor.is_verified,
                'is_active': vendor.is_active,
                'cafes_count': cafes_count,
                'coupons_count': coupons_count,
                'active_coupons': active_coupons,
                'total_revenue': float(total_revenue),
                'total_transactions': total_transactions,
                'avg_transaction': float(avg_transaction),
                'orders_count': orders_count,
                'joined_date': vendor.created_at.isoformat(),
                'user': {
                    'id': vendor.user.id if vendor.user else None,
                    'username': vendor.user.username if vendor.user else None,
                    'email': vendor.user.email if vendor.user else None
                } if vendor.user else None
            })
        
        return JsonResponse({'vendors': vendors_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@staff_member_required
@csrf_exempt
def admin_update_user_status(request, user_id):
    """Activate/suspend user"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)
            
            if 'is_active' in data:
                user.is_active = data['is_active']
                user.save()
                
                # Log activity
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='admin_action',
                    description=f"{'Activated' if data['is_active'] else 'Suspended'} user {user.username}",
                    metadata={'target_user': user_id, 'action': 'status_change'}
                )
                
                return JsonResponse({
                    'success': True,
                    'message': f'User {"activated" if data["is_active"] else "suspended"} successfully'
                })
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@staff_member_required
@csrf_exempt
def admin_verify_vendor(request, vendor_id):
    """Verify vendor"""
    if request.method == 'POST':
        try:
            vendor = Vendor.objects.get(id=vendor_id)
            data = json.loads(request.body)
            
            vendor.is_verified = data.get('is_verified', True)
            vendor.save()
            
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='admin_action',
                description=f"{'Verified' if vendor.is_verified else 'Unverified'} vendor {vendor.cafe_name}",
                metadata={'target_vendor': vendor_id, 'action': 'verification'}
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Vendor {"verified" if vendor.is_verified else "unverified"} successfully'
            })
        except Vendor.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Vendor not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# ===== USER AUTHENTICATION VIEWS =====

@csrf_exempt
def register(request):
    """User registration endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('email').split('@')[0]  # Use email prefix as username
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('name', '').split()[0] if data.get('name') else ''
            last_name = ' '.join(data.get('name', '').split()[1:]) if data.get('name') and len(data.get('name').split()) > 1 else ''
            phone = data.get('phone', '')
            
            # Check if user exists
            if User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'error': 'User already exists'}, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Save additional info in profile (you might want to extend User model)
            # For now, we'll just return success
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='register',
                description='User registered',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': 'customer',
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def user_login(request):
    """User login endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # Find user by email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
            
            # Authenticate
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='login',
                    description='User logged in',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': 'admin' if user.is_superuser else ('vendor' if hasattr(user, 'vendor_profile') else 'customer'),
                        'is_superuser': user.is_superuser,
                        'vendor_id': user.vendor_profile.vendor_id if hasattr(user, 'vendor_profile') else None,
                    }
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def user_logout(request):
    """User logout endpoint"""
    if request.method == 'POST':
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='logout',
            description='User logged out',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        logout(request)
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def get_current_user(request):
    """Get current user info"""
    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': 'admin' if user.is_superuser else ('vendor' if hasattr(user, 'vendor_profile') else 'customer'),
        'is_superuser': user.is_superuser,
        'vendor_id': user.vendor_profile.vendor_id if hasattr(user, 'vendor_profile') else None,
        'date_joined': user.date_joined.isoformat(),
    })

# ===== VENDOR VIEWS =====

@csrf_exempt
def vendor_register(request):
    """Vendor registration endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Check if email already exists
            if Vendor.objects.filter(email=data.get('email')).exists():
                return JsonResponse({'success': False, 'error': 'Vendor with this email already exists'}, status=400)
            
            # Create user account if not exists
            email = data.get('email')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create new user
                username = email.split('@')[0]
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=data.get('password', 'defaultpass123'),  # Generate random password or require in form
                    first_name=data.get('owner_name', '').split()[0] if data.get('owner_name') else '',
                    last_name=' '.join(data.get('owner_name', '').split()[1:]) if data.get('owner_name') and len(data.get('owner_name').split()) > 1 else ''
                )
            
            # Create vendor
            vendor = Vendor.objects.create(
                user=user,
                cafe_name=data.get('cafe_name'),
                owner_name=data.get('owner_name'),
                business_type=data.get('business_type'),
                email=data.get('email'),
                phone=data.get('phone'),
                address=data.get('address'),
                city=data.get('city'),
                state=data.get('state'),
                gst_number=data.get('gst_number'),
                years_in_business=data.get('years_in_business', 0),
                opening_time=data.get('opening_time', '08:00'),
                closing_time=data.get('closing_time', '22:00'),
                description=data.get('description', ''),
                seating_capacity=data.get('seating_capacity', 0),
                amenities=data.get('amenities', []),
                is_verified=False,
                is_active=True
            )
            
            # Create welcome coupon
            coupon_code = f"WELCOME{vendor.vendor_id[:6].upper()}"
            valid_until = timezone.now() + timedelta(days=30)
            
            coupon = Coupon.objects.create(
                vendor=vendor,
                code=coupon_code,
                description=f"Welcome discount for {vendor.cafe_name}",
                discount_value=15,
                valid_until=valid_until,
                usage_limit=100,
                status='active'
            )
            
            # Create cafe entry
            Cafe.objects.create(
                vendor=vendor,
                name=vendor.cafe_name,
                city=vendor.city,
                state=vendor.state,
                lat=20.5937 + (hash(vendor.cafe_name) % 100) / 1000,  # Generate approximate coordinates
                lng=78.9629 + (hash(vendor.cafe_name) % 100) / 1000,
                rating=4.0,
                address=vendor.address,
                description=vendor.description,
                is_partner=True,
                opening_hours=f"{vendor.opening_time.strftime('%I:%M %p')} - {vendor.closing_time.strftime('%I:%M %p')}",
                contact=vendor.phone,
                email=vendor.email,
                amenities=vendor.amenities,
                is_active=True
            )
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='vendor_register',
                description=f'Vendor registered: {vendor.cafe_name}',
                metadata={'vendor_id': vendor.id}
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Vendor registered successfully',
                'vendor_id': vendor.vendor_id,
                'coupon': {
                    'code': coupon.code,
                    'discount_value': coupon.discount_value
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

# ===== DATA ENDPOINTS =====

def get_cafes(request):
    """Get all cafes"""
    cafes = Cafe.objects.filter(is_active=True).values(
        'id', 'name', 'city', 'state', 'lat', 'lng', 'rating', 
        'address', 'description', 'is_partner', 'opening_hours', 
        'contact', 'vendor_id'
    )
    return JsonResponse(list(cafes), safe=False)

def get_products(request):
    """Get products (you might want to create a Product model)"""
    # For now, return empty list - you can implement later
    return JsonResponse([], safe=False)

def get_coupons(request):
    """Get active coupons"""
    coupons = Coupon.objects.filter(
        status='active',
        valid_until__gte=timezone.now()
    ).values('code', 'description', 'discount_value', 'valid_until')
    return JsonResponse(list(coupons), safe=False)

def get_stats(request):
    """Get platform stats"""
    stats = {
        'total_cafes': Cafe.objects.filter(is_active=True).count(),
        'total_cities': Cafe.objects.values('city').distinct().count(),
        'vendor_partners': Vendor.objects.filter(is_verified=True).count(),
        'active_users': UserActivity.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('user').distinct().count()
    }
    return JsonResponse(stats)