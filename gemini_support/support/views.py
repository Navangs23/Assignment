import os
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from dotenv import load_dotenv

from .forms import UserRegisterForm, TicketForm
from .models import Ticket, SupportTicket, TicketReply

# --- Gemini API Configuration ---
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# --- Authentication Views ---

def register_view(request):
    """
    Handles user registration. New users are defaulted to 'customer' type.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.user_type = 'customer'
            user.profile.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'support/register.html', {'form': form})


def login_view(request):
    """
    Handles user login and redirects based on user type ('admin' or 'customer').
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                if user.profile.user_type == 'admin':
                    return redirect('admin_ticket_list')
                else:
                    return redirect('ticket_list')

        messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request, 'support/login.html', {'form': form})


def logout_view(request):
    """
    Handles user logout.
    """
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')


# --- Customer Ticket Views (Requires Login) ---

@login_required
def ticket_list(request):
    """
    Customer view: List their tickets and allows creation of new tickets.
    """
    if request.user.profile.user_type != 'customer':
        return redirect('admin_ticket_list')

    tickets = Ticket.objects.filter(user=request.user).prefetch_related('replies').order_by('-created_at')

    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            messages.success(request, "Your ticket has been created successfully!")
            return redirect('ticket_list')
    else:
        form = TicketForm()

    return render(request, 'support/ticket_list.html', {'tickets': tickets, 'form': form})


@login_required
def create_ticket(request):
    """
    Handles POST request for creating a new ticket.
    """
    if request.user.profile.user_type != 'customer':
        return redirect('admin_ticket_list')

    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        priority = request.POST.get('priority')
        attachment = request.FILES.get('attachment')
        category = request.POST.get('category', 'Technical')

        Ticket.objects.create(
            user=request.user,
            subject=subject,
            description=description,
            category=category,
            priority=priority,
            attachment=attachment
        )
        messages.success(request, "Your ticket has been created successfully!")
        return redirect('ticket_list')

    return redirect('ticket_list')

@login_required
def admin_ticket_list(request):
    """
    Admin view: List all tickets in the system.
    """
    if request.user.profile.user_type != 'admin':
        return redirect('ticket_list')

    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'support/admin_ticket_list.html', {'tickets': tickets})


@login_required
def update_ticket(request, ticket_id):
    """
    Admin view: Handles updating a ticket's status and adding/updating an admin response.
    Ensures updated_at of both Ticket and TicketReply are updated.
    """
    if request.user.profile.user_type != 'admin':
        return redirect('ticket_list')

    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        response_text = request.POST.get('response', '').strip()
        status = request.POST.get('status', ticket.status)
        is_ai_generated = request.POST.get('is_ai_generated') == 'true'

        # Update or create the admin reply
        if response_text:
            existing_reply = TicketReply.objects.filter(
                ticket=ticket,
                responder=request.user
            ).order_by('-created_at').first()

            if existing_reply:
                existing_reply.message = response_text
                existing_reply.is_ai_generated = is_ai_generated
                existing_reply.save(update_fields=['message', 'is_ai_generated', 'updated_at'])
            else:
                TicketReply.objects.create(
                    ticket=ticket,
                    responder=request.user,
                    message=response_text,
                    is_ai_generated=is_ai_generated
                )

            ticket.response = response_text

        ticket.status = status
        ticket.save(update_fields=['response', 'status', 'updated_at'])

        messages.success(request, f"Ticket #{ticket.id} updated successfully.")
        return redirect('admin_ticket_list')

    return redirect('admin_ticket_list')

@login_required
@csrf_exempt
def generate_ai_reply(request, ticket_id):
    """
    Generate an AI reply using the configured Gemini API.
    Returns the reply as an HTML string suitable for a rich text editor.
    """
    if request.user.profile.user_type != 'admin':
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)

    try:
        ticket = get_object_or_404(Ticket, id=ticket_id)
        company_name = "WeNS Pvt. Ltd."

        prompt = f"""
        You are a professional customer support assistant at **{company_name}**.
        Your task: generate a **concise, professional, and helpful** reply to this ticket.

        Ticket Details:
        - Subject: {ticket.subject}
        - Description: {ticket.description}
        - Priority: {ticket.priority}

        ### Requirements:
        - Return the **reply strictly in HTML** format.
        - Use only: <p>, <strong>, <em>, <ul>, and <li> tags.
        - Do NOT use Markdown, plain text lists, or email-like templates.
        - Focus only on providing **actionable guidance or solution** for the ticket.
        - Do NOT add greetings like "Dear customer" or sign-offs like "Best regards".
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        ai_response = model.generate_content(prompt)
        reply_html = ai_response.text.strip()

        return JsonResponse({"success": True, "reply": reply_html})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@login_required
def mark_ticket_in_process(request, ticket_id):
    """
    Marks a ticket's status as 'In Process' if it is currently 'Open'.
    """
    if request.method == "POST" and request.user.profile.user_type == 'admin':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            if ticket.status == "Open":
                ticket.status = "In Process"
                ticket.save(update_fields=["status"])
                messages.info(request, f"Ticket #{ticket.id} marked as In Process.")
            return JsonResponse({"success": True, "status": ticket.status})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request or unauthorized."}, status=400)