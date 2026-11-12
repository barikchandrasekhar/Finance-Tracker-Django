from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import FinancialDetailForm
from .models import FinancialDetail
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import io

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return render(request, 'login.html', {'error': 'Username and password are required'})
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    return render(request, 'login.html', {'error': ''})

@login_required
def dashboard(request):
    details = FinancialDetail.objects.filter(user=request.user).order_by('-created_at').first()
    if details:
        net_worth = details.savings - details.debts
        financial_health = "Good" if net_worth > 0 else "Needs Improvement"
    else:
        net_worth = 0
        financial_health = "No data available"
    return render(request, 'dashboard.html', {
        'details': details,
        'net_worth': net_worth,
        'financial_health': financial_health
    })

@login_required
def upload_details(request):
    if request.method == 'POST':
        form = FinancialDetailForm(request.POST)
        if form.is_valid():
            financial_detail = form.save(commit=False)
            financial_detail.user = request.user
            financial_detail.save()
            return redirect('dashboard')
        else:
            return render(request, 'upload_details.html', {'form': form})
    else:
        form = FinancialDetailForm()
    return render(request, 'upload_details.html', {'form': form})

@login_required
def history(request):
    history = FinancialDetail.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'history': history})

@login_required
def delete_record(request, record_id):
    record = FinancialDetail.objects.filter(id=record_id, user=request.user).first()
    if record:
        record.delete()
    return redirect('history')

@login_required
def download_report(request):
    details = FinancialDetail.objects.filter(user=request.user).order_by('-created_at').first()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Financial Report", styles['Title']))
    elements.append(Spacer(1, 12))

    if details:
        data = [
            ['Metric', 'Amount'],
            ['Income', f"${details.income}"],
            ['Expenses', f"${details.expenses}"],
            ['Savings', f"${details.savings}"],  # Fixed: Changed 'Savings' to "Savings"
            ['Debts', f"${details.debts}"],
            ['Net Worth', f"${details.savings - details.debts}"],
            ['Financial Health', "Good" if (details.savings - details.debts) > 0 else "Needs Improvement"],
        ]
    else:
        data = [['No financial data available', '']]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="financial_report.pdf"'
    return response