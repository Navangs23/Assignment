from django.contrib import admin
from .models import Profile, Ticket, TicketReply

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')
    list_filter = ('user_type',)
    search_fields = ('user__username',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority')
    search_fields = ('subject', 'user__username')

@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'responder', 'is_ai_generated', 'created_at')
