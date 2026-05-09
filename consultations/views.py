from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from .models import Lead, Consultation
from datetime import datetime
from urllib.parse import quote

# ========== WHATSAPP NOTIFICATION FUNCTIONS ==========

def send_whatsapp_notification_to_admin(lead, consultation):
    """Send WhatsApp notification to Royal Hope team (254791597351)"""
    your_phone = '254791597351'
    
    whatsapp_msg = f"""ROYALHOPE NEW PATIENT

PATIENT: {lead.name}
PHONE: {lead.phone}
EMAIL: {lead.email or 'Not provided'}
COUNTY: {lead.county or 'Not specified'}
GENDER: {lead.gender or 'Not specified'}

SYMPTOMS:
{consultation.symptoms}

DURATION: {consultation.duration}

AGE RANGE: {consultation.age_range}

PRE-EXISTING CONDITIONS:
{consultation.conditions or 'None'}

Respond to this patient via WhatsApp
Admin: /admin/consultations/consultation/{consultation.id}/change/"""
    
    whatsapp_url = f"https://wa.me/{your_phone}?text={quote(whatsapp_msg)}"
    return whatsapp_url


def send_whatsapp_confirmation_to_patient(lead):
    """Send WhatsApp confirmation to patient"""
    patient_phone = lead.phone.replace('+', '').replace(' ', '').replace('-', '')
    
    whatsapp_msg = f"""RoyalHope Home Based Care

Thank you {lead.name}! Your consultation has been received.

Dr. Solomon will review your health screening and respond shortly.

Emergency: +254 791 597 351

Stay healthy"""
    
    whatsapp_url = f"https://wa.me/{patient_phone}?text={quote(whatsapp_msg)}"
    return whatsapp_url


def send_whatsapp_response_to_patient(consultation, response_text, doctor_name):
    """Send doctor's response to patient via WhatsApp"""
    patient = consultation.lead
    patient_phone = patient.phone.replace('+', '').replace(' ', '').replace('-', '')
    
    whatsapp_msg = f"""RoyalHope - Doctor's Response

Dear {patient.name},

Dr. {doctor_name} has reviewed your consultation:

Your symptoms: {consultation.symptoms}

Doctor's response:
{response_text}

Need more help? Call us: +254 791 597 351

Stay healthy"""
    
    whatsapp_url = f"https://wa.me/{patient_phone}?text={quote(whatsapp_msg)}"
    return whatsapp_url


# ========== MAIN VIEWS ==========

def home(request):
    if request.method == "POST":
        name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email", "")
        county = request.POST.get("county", "")
        gender = request.POST.get("gender", "")
        referral = request.POST.get("referral", "")
        consent = request.POST.get("consent") == "on"
        
        if not name or not phone:
            messages.error(request, "Please fill in all fields (name, phone)")
            return render(request, "home.html")
        
        lead = Lead.objects.create(
            name=name,
            phone=phone,
            email=email if email else None,
            county=county,
            gender=gender,
            referral=referral if referral else None,
            consent=consent,
        )
        
        request.session['lead_id'] = lead.id
        return redirect("screening")
    
    return render(request, "home.html")


def screening(request):
    lead_id = request.session.get('lead_id')
    
    if not lead_id:
        messages.warning(request, "Please fill out the consultation request first")
        return redirect("home")
    
    try:
        lead = Lead.objects.get(id=lead_id)
    except Lead.DoesNotExist:
        messages.error(request, "Session expired. Please start over.")
        return redirect("home")
    
    if request.method == "POST":
        symptoms = request.POST.get("symptoms", "")
        duration = request.POST.get("duration", "")
        age_range = request.POST.get("age_range", "")
        conditions = request.POST.get("conditions_combined", request.POST.get("conditions", ""))
        
        consultation = Consultation.objects.create(
            lead=lead,
            symptoms=symptoms,
            duration=duration,
            age_range=age_range,
            conditions=conditions,
            status='pending',
        )
        
        message = f"""NEW PATIENT - RoyalHope

Name: {lead.name}
Phone: {lead.phone}
County: {lead.county or 'Not specified'}

SYMPTOMS:
{symptoms}

Duration: {duration}
Age: {age_range}
Conditions: {conditions or 'None'}

Reply to this patient via WhatsApp"""
        
        whatsapp_url = f"https://wa.me/254791597351?text={quote(message)}"
        
        print(f"\n{'='*60}")
        print(f"WHATSAPP LINK:")
        print(f"{whatsapp_url}")
        print(f"{'='*60}\n")
        
        return redirect(whatsapp_url)
    
    return render(request, "screening.html", {"lead": lead})


# ========== ADMIN RESPONSE VIEWS ==========

@staff_member_required
def send_response_form(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    
    if request.method == 'POST':
        response_text = request.POST.get('response_text')
        
        consultation.doctor_response = response_text
        consultation.responded_by = request.user.username
        consultation.responded_at = datetime.now()
        consultation.status = 'consultation_done'
        consultation.save()
        
        whatsapp_link = send_whatsapp_response_to_patient(consultation, response_text, request.user.username)
        
        messages.success(request, f'Response saved for {consultation.lead.name}!')
        messages.info(request, f'<a href="{whatsapp_link}" target="_blank" style="color:#25D366; font-weight:bold;">Click to send to patient</a>')
        
        return redirect('/admin/consultations/consultation/')
    
    return render(request, 'admin/response_form.html', {'consultation': consultation})


@staff_member_required
def send_whatsapp_manual(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    patient = consultation.lead
    
    phone_clean = patient.phone.replace('+', '').replace(' ', '').replace('-', '')
    message = f"Hi {patient.name}, Dr. {request.user.username} responded to your consultation."
    whatsapp_url = f"https://wa.me/{phone_clean}?text={quote(message)}"
    
    return redirect(whatsapp_url)
