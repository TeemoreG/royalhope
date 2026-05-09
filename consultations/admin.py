from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from .models import Lead, Consultation
from django.conf import settings

class ConsultationInline(admin.TabularInline):
    model = Consultation
    extra = 0
    fields = ['symptoms', 'duration', 'age_range', 'conditions', 'status', 'created_at']
    readonly_fields = ['created_at']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'county', 'gender', 'created_at']
    list_filter = ['county', 'gender', 'created_at']
    search_fields = ['name', 'phone', 'email']
    inlines = [ConsultationInline]

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_patient_name', 'get_patient_phone', 'age_range', 'status', 'created_at', 'action_buttons']
    list_filter = ['status', 'age_range', 'created_at']
    search_fields = ['lead__name', 'lead__phone', 'lead__email', 'symptoms']
    readonly_fields = ['created_at', 'updated_at', 'response_whatsapp_sent']
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('lead',)
        }),
        ('Health Concerns', {
            'fields': ('symptoms', 'duration', 'age_range', 'conditions')
        }),
        ('Doctor Response', {
            'fields': ('doctor_response', 'status', 'responded_by', 'responded_at')
        }),
        ('WhatsApp Status', {
            'fields': ('response_whatsapp_sent',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_patient_name(self, obj):
        return obj.lead.name
    get_patient_name.short_description = 'Patient'
    
    def get_patient_phone(self, obj):
        return obj.lead.phone
    get_patient_phone.short_description = 'Phone'
    
    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}" style="background:#25D366;color:white;padding:5px 10px;text-decoration:none;border-radius:5px;margin-right:5px;">📝 Respond</a>'
            '<a class="button" href="{}" style="background:#25D366;color:white;padding:5px 10px;text-decoration:none;border-radius:5px;">📱 WhatsApp</a>',
            f'/admin/send-response/{obj.id}/',
            f'/admin/send-whatsapp/{obj.id}/'
        )
    action_buttons.short_description = 'Actions'
    
    def save_model(self, request, obj, form, change):
        if 'doctor_response' in form.changed_data and form.cleaned_data.get('doctor_response'):
            obj.responded_by = request.user.username
            from django.utils import timezone
            obj.responded_at = timezone.now()
            obj.status = 'consultation_done'
        super().save_model(request, obj, form, change)