from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Ticket views
    path('list/', views.ticket_list, name='ticket_list'),
    path('admin/view_ticket/', views.admin_ticket_list, name='admin_ticket_list'),
    path('tickets/update/<int:ticket_id>/', views.update_ticket, name='update_ticket'),

    path('tickets/ai_reply/<int:ticket_id>/', views.generate_ai_reply, name='generate_ai_reply'),
    path('tickets/mark_in_process/<int:ticket_id>/', views.mark_ticket_in_process, name='mark_ticket_in_process'),

]
