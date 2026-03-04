# Import necessary modules
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
import json
import traceback
import io
import os
import re
import pdfkit
import anthropic

# Import models and forms
from talentshield.models import CustomUser, ResumeUpload, Profile, Skill
from talentshield.forms import SignUpForm, ProfileForm, UserForm

# Basic page views
def index(request):
    return render(request, 'index.html')

def resume(request):
    return render(request, 'resumebuilder.html')

def upload(request):
    return render(request, 'upload.html')

def option(request):
    return render(request, 'option.html')

def signup(request):
    return render(request, 'signup.html')

def results(request):
    return render(request, 'results.html')

def profile(request):
    return render(request, 'profile.html')

def candidate(request):
    return render(request, 'candidate.html')

def hrmanager(request):
    return render(request, 'hrmanager.html')

def dashboard(request):
    return render(request, 'dashboard.html')

def login_view(request):
    if request.method == "POST":
        # Handle form submission
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid credentials. Try again.")
    # For GET requests, just render the template
    return render(request, "login.html")

# Authentication views
@csrf_exempt
def api_login(request):
    if request.method == "POST":
        try:
            # Parse JSON data from request body
            body_unicode = request.body.decode('utf-8')
            print(f"Raw Request Body: {request.body}")
            body_data = json.loads(body_unicode)
            print(f"Parsed JSON Data: {body_data}")
            
            email = body_data.get('email')
            password = body_data.get('password')
            role = body_data.get('role', 'candidate')
            
            print(f"Login attempt with email: {email}")
            
            # Directly use Django's built-in authentication
            from django.contrib.auth import get_user_model, authenticate
            User = get_user_model()
            
            try:
                # Find the user
                user_obj = User.objects.get(email=email)
                print(f"User found in database: {user_obj.username}")
                
                # DEBUG: Print what's being checked
                print(f"Attempting authentication with username: {user_obj.username}, email: {email}")
                
                # Try different authentication approaches
                auth_by_email = authenticate(request, email=email, password=password)
                auth_by_username = authenticate(request, username=user_obj.username, password=password)
                
                print(f"Auth by email result: {auth_by_email is not None}")
                print(f"Auth by username result: {auth_by_username is not None}")
                
                # Use whichever authentication worked
                user = auth_by_email or auth_by_username
                
                if user is not None:
                    login(request, user)
                    print(f"Authentication successful for user: {user.email}")
                    
                    response_data = {
                        'success': True,
                        'message': 'Login successful',
                        'redirect': '/candidate.html' if user.role == 'candidate' else '/hrmanager.html',
                        'user': {
                            'name': user.username,
                            'email': user.email,
                            'role': user.role
                        }
                    }
                    return JsonResponse(response_data)
                else:
                    # Try a direct password check for debugging
                    from django.contrib.auth.hashers import check_password
                    password_check = check_password(password, user_obj.password)
                    print(f"Direct password check result: {password_check}")
                    print(f"Stored password hash: {user_obj.password[:10]}...")
                    
                    print(f"Authentication failed! Password might be incorrect.")
                    return JsonResponse({'error': 'Invalid credentials'}, status=400)
                    
            except User.DoesNotExist:
                print(f"User does not exist in database")
                return JsonResponse({'error': 'Invalid credentials'}, status=400)
                
        except json.JSONDecodeError:
            print("Invalid JSON format received")
            return JsonResponse({'error': 'Invalid request format'}, status=400)
        except Exception as e:
            print(f"Login error: {str(e)}")
            print(traceback.format_exc())
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
@csrf_exempt
def api_signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            full_name = data.get("full_name", "").strip()
            email = data.get("email", "").strip().lower()
            password = data.get("password")
            role = data.get("role")

            print("Received Signup Data:", data)

            if not full_name or not email or not password or not role:
                print("❌ Missing fields in request")
                return JsonResponse({"error": "All fields are required"}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                print("❌ Email already exists in database")
                return JsonResponse({"error": "Email is already registered"}, status=400)

            # Split the full name to get first and last name
            name_parts = full_name.split(maxsplit=1)
            first_name = name_parts[0] if name_parts else ""
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            username = email.split('@')[0]  # Use part before @ as username

            # Create user - IMPORTANT: Use create_user instead of create
            user = CustomUser.objects.create_user(  # Use create_user instead of create
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password,  # No need to hash manually with create_user
                role=role
            )

            print("✅ User created successfully:", user)
            return JsonResponse({"message": "Account created successfully!"}, status=201)

        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
            return JsonResponse({"error": "Invalid request"}, status=400)
        except Exception as e:
            print(f"❌ Error creating user: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    print("❌ Wrong request method")
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def hr_login(request):
    if request.method == "POST":
        try:
            # Parse the JSON data
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
            
            # Hardcoded HR credentials
            HR_EMAIL = "hr@talentshield.com"
            HR_PASSWORD = "TalentShield"
            
            # Check if the provided credentials match the HR credentials
            if email == HR_EMAIL and password == HR_PASSWORD:
                # In a real-world scenario, you'd create a specific HR user in the database
                # For this example, we'll simulate a successful login
                return JsonResponse({
                    'success': True,
                    'message': 'HR Login successful',
                    'redirect': '/hrmanager.html'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid HR credentials'
                }, status=400)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid request format'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    }, status=405)
# Dashboard and profile views
def candidate_dashboard(request):
    """
    View function for displaying the candidate dashboard.
    """
    return render(request, 'candidate.html')

def upload_documents(request):
    """
    View function for the document upload page.
    """
    return render(request, 'upload.html')

@login_required
def user_profile(request):
    """
    View function for displaying the user's profile.
    """
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    
    context = {
        'user': user,
        'profile': profile,
    }
    
    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    """
    View function for editing the user's profile.
    """
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    user_skills = profile.skills.all()
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_instance = profile_form.save(commit=False)
            profile_instance.user = user
            profile_instance.save()
            
            # Handle skills
            # Clear existing skills
            profile.skills.clear()
            
            # Add existing skills
            if 'skills' in request.POST:
                skill_ids = request.POST.getlist('skills')
                for skill_id in skill_ids:
                    skill = get_object_or_404(Skill, id=skill_id)
                    profile.skills.add(skill)
            
            # Add new skills
            if 'new_skills' in request.POST:
                new_skills = request.POST.getlist('new_skills')
                for skill_name in new_skills:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    profile.skills.add(skill)
            
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    
    context = {
        'form': profile_form,
        'user_form': user_form,
        'user_skills': user_skills,
    }
    
    return render(request, 'users/edit_profile.html', context)

# Resume builder functions
def resume_builder(request):
    """View to render the resume builder interface"""
    return render(request, 'resumebuilder.html')

def calculate_resume_score(context):
    """
    Calculate a resume score based on completeness and content quality.
    Returns a score out of 100 and feedback for improvement.
    """
    score = 0
    feedback = []
    
    # Initialize scoring weights
    weights = {
        'personal_info': 15,
        'summary': 20,
        'experience': 25,
        'education': 15,
        'skills': 15,
        'certifications': 10
    }
    
    # Score personal information (name, email, phone, location)
    personal_score = 0
    if context.get('name'):
        personal_score += 5
    if context.get('email'):
        personal_score += 4
    if context.get('phone'):
        personal_score += 3
    if context.get('location'):
        personal_score += 3
    score += (personal_score / 15) * weights['personal_info']
    
    if personal_score < 15:
        feedback.append("Complete all personal information fields for better visibility.")
    
    # Score professional summary
    summary_score = 0
    summary = context.get('summary', '')
    if summary:
        # Basic length check (minimum 200 characters for a good summary)
        if len(summary) >= 200:
            summary_score += 15
        elif len(summary) >= 100:
            summary_score += 10
        else:
            summary_score += 5
            feedback.append("Expand your professional summary to at least 200 characters.")
        
        # Check for key terms like "experience", "skills", "expertise"
        keywords = ['experience', 'skills', 'expertise', 'qualified', 'professional', 
                   'accomplished', 'successful', 'background', 'knowledge']
        keyword_count = sum(1 for keyword in keywords if keyword.lower() in summary.lower())
        summary_score += min(keyword_count, 5)
    else:
        feedback.append("Add a professional summary to highlight your qualifications.")
    
    score += (summary_score / 20) * weights['summary']
    
    # Score work experience
    experience_score = 0
    if context.get('company') and context.get('position'):
        experience_score += 10
        
        # Check for duration
        if context.get('duration'):
            experience_score += 5
        else:
            feedback.append("Add employment duration to your experience.")
        
        # Check responsibilities description
        responsibilities = context.get('responsibilities', '')
        if responsibilities:
            if len(responsibilities) >= 200:
                experience_score += 10
            elif len(responsibilities) >= 100:
                experience_score += 5
                feedback.append("Provide more details about your responsibilities and achievements.")
        else:
            feedback.append("Describe your job responsibilities and achievements.")
    else:
        feedback.append("Add your work experience details.")
    
    score += (experience_score / 25) * weights['experience']
    
    # Score education
    education_score = 0
    education = context.get('education', {})
    if education.get('institution'):
        education_score += 5
    else:
        feedback.append("Add your educational institution.")
        
    if education.get('degree'):
        education_score += 7
    else:
        feedback.append("Include your degree or qualification.")
        
    if education.get('graduation_year'):
        education_score += 3
    else:
        feedback.append("Add your graduation year.")
    
    score += (education_score / 15) * weights['education']
    
    # Score skills
    skills_score = 0
    skills = context.get('skills', [])
    if skills:
        skill_count = len(skills)
        if skill_count >= 8:
            skills_score += 15
        elif skill_count >= 5:
            skills_score += 10
        elif skill_count >= 3:
            skills_score += 5
            feedback.append("Add more skills to showcase your capabilities (aim for at least 8).")
        else:
            feedback.append("List more of your professional skills.")
    else:
        feedback.append("Add your professional skills to the resume.")
    
    score += (skills_score / 15) * weights['skills']
    
    # Score certifications
    cert_score = 0
    certifications = context.get('certifications', [])
    if certifications:
        cert_count = len(certifications)
        if cert_count >= 2:
            cert_score += 10
        else:
            cert_score += 5
            feedback.append("Add more professional certifications if you have them.")
    else:
        feedback.append("Include professional certifications to boost your credibility.")
    
    score += (cert_score / 10) * weights['certifications']
    
    # Round the final score
    final_score = round(score)
    
    # Determine rating based on score
    if final_score >= 90:
        rating = "Excellent"
    elif final_score >= 80:
        rating = "Very Good"
    elif final_score >= 70:
        rating = "Good"
    elif final_score >= 60:
        rating = "Above Average"
    elif final_score >= 50:
        rating = "Average"
    else:
        rating = "Needs Improvement"
    
    # Limit to top 3 feedback items if there are too many
    if len(feedback) > 3:
        feedback = feedback[:3]
    
    return {
        'score': final_score,
        'rating': rating,
        'feedback': feedback
    }

def generate_pdf(request):
    if request.method == "POST":
        # Get form data
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        phone = request.POST.get("phone", "")
        location = request.POST.get("location", "")
        summary = request.POST.get("summary", "")
        
        # Work experience
        company = request.POST.get("company", "")
        position = request.POST.get("position", "")
        duration = request.POST.get("duration", "")
        responsibilities = request.POST.get("responsibilities", "")
        
        # Education
        institution = request.POST.get("institution", "")
        degree = request.POST.get("degree", "")
        graduation_year = request.POST.get("graduation_year", "")
        
        # Skills - assuming it's a comma-separated string
        skills_input = request.POST.get("skills", "")
        skills_list = [{'name': skill.strip()} for skill in skills_input.split(',') if skill.strip()]
        
        # Certification
        certification = request.POST.get("certification", "")
        organization = request.POST.get("organization", "")
        date_earned = request.POST.get("date_earned", "")
        
        # Get selected template
        selected_template = request.POST.get("selected_template", "professional")
        
        # Prepare education data structure to match our templates
        education = {
            'institution': institution,
            'degree': degree,
            'graduation_year': graduation_year,
        }
        
        # Prepare certifications data
        certifications = []
        if certification:
            certifications.append({
                'name': certification,
                'organization': organization,
                'date_earned': date_earned,
            })
        
        # Create context for template
        context = {
            'name': name,
            'email': email,
            'phone': phone,
            'location': location,
            'summary': summary,
            'position': position,
            'company': company,
            'duration': duration,
            'responsibilities': responsibilities,
            'education': education,
            'skills': skills_list,
            'certifications': certifications,
            'experiences': []  # Empty list for additional experiences
        }
        
        # Calculate resume score
        resume_score = calculate_resume_score(context)
        context['resume_score'] = resume_score
        
        # Determine template file based on selection
        template_mapping = {
            'professional': 'resume_templates/professional.html',
            'creative': 'resume_templates/creative.html',
            'technical': 'resume_templates/technical.html',
        }
        
        template_path = template_mapping.get(selected_template, 'resume_templates/professional.html')
        
        # Render the template with context
        template = get_template(template_path)
        html_string = template.render(context)
        
        # Set path to wkhtmltopdf.exe
        path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
        
        # PDF options
        options = {
            'page-size': 'Letter',
            'encoding': 'UTF-8',
            'no-outline': None,
            'enable-local-file-access': None
        }
        
        # Generate PDF
        pdf = pdfkit.from_string(html_string, False, options=options, configuration=config)
        
        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"{name.replace(' ', '_')}_resume.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    # If not POST request, redirect to resume builder
    return redirect('resume_builder')

# Resume upload views
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        position = request.POST.get('position', 'Not specified')
        
        # Save the resume
        resume = ResumeUpload(
            file_name=resume_file.name,
            file=resume_file,
            position=position
        )
        resume.save()
        
        return JsonResponse({'success': True, 'id': resume.id})
    
    return render(request, 'upload.html')

def hr_dashboard(request):
    resumes = ResumeUpload.objects.all().order_by("-upload_date")
    for resume in resumes:
        if resume.ats_feedback:
            resume.ats_feedback = json.loads(resume.ats_feedback)

    return render(request, "hrmanager.html", {"resumes": resumes})

def view_resume(request, resume_id):
    try:
        resume = ResumeUpload.objects.get(id=resume_id)
        response = HttpResponse(resume.file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{resume.file_name}"'
        return response
    except ResumeUpload.DoesNotExist:
        return HttpResponse("Resume not found", status=404)

def update_status(request, resume_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            status = data.get('status')
            
            resume = ResumeUpload.objects.get(id=resume_id)
            resume.status = status
            resume.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

################

from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

def get_all_users(request):
    users = User.objects.all()

    users_data = []
    for user in users:
        users_data.append({
            "id": user.id,  # Needed if you want to view a specific user
            "name": user.username,
            "title": getattr(user, 'profile_title', "User"),  # Check if field exists
            "email": user.email,
            "phone": getattr(user, 'phone', "N/A"),
            "location": getattr(user, 'location', "Not Provided"),
            "profile_picture": user.profile_picture.url if getattr(user, 'profile_picture', None) else "https://via.placeholder.com/120",
            "skills": user.skills.split(",") if getattr(user, 'skills', None) else []
        })

    return JsonResponse({"users": users_data})
########

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required  # Ensures only authenticated users can access
def get_logged_in_user(request):
    user = request.user  # Fetch the logged-in user

    user_data = {
        "id": user.id,
        "name": user.username,
        "title": getattr(user, 'profile_title', "User"),  # Check if field exists
        "email": user.email,
        "phone": getattr(user, 'phone', "N/A"),
        "location": getattr(user, 'location', "Not Provided"),
        "profile_picture": user.profile_picture.url if getattr(user, 'profile_picture', None) else "https://via.placeholder.com/120",
        "skills": user.skills.split(",") if getattr(user, 'skills', None) else []
    }

    return JsonResponse(user_data)
#########
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser  # Ensure you're using your custom user model

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")  # Get role from form

        user = authenticate(request, email=email, password=password)

        if user is not None:
            # 🔹 Ensure user logs in with the correct role
            if user.role != role:
                messages.error(request, f"Invalid login. You are registered as {user.role}, not {role}.")
                return redirect("login")

            login(request, user)

            # 🔹 Redirect user based on role
            if user.role == "HR Manager":
                return redirect("hr_dashboard")  # HR Dashboard
            elif user.role == "Candidate":
                return redirect("candidate_dashboard")  # Candidate Dashboard

        else:
            messages.error(request, "Invalid email or password.")

    return render(request, "login.html")

##########


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseForbidden

@login_required
def hr_dashboard(request):
    if request.user.role != "HR Manager":
        return HttpResponseForbidden("You are not allowed to access this page.")  # Restrict access

    return render(request, "hr_dashboard.html")
#########

@login_required
def candidate_dashboard(request):
    if request.user.role != "Candidate":
        return HttpResponseForbidden("You are not allowed to access this page.")

    return render(request, "candidate_dashboard.html")
#######

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_current_user(request):
    user = request.user
    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    })
###
from django.contrib.auth import logout
from django.http import JsonResponse

def logout_view(request):
    logout(request)
    return JsonResponse({"message": "Logged out successfully"})

##############ai

import google.generativeai as genai
import os
import PyPDF2
from django.views.decorators.csrf import csrf_exempt


# Extract text from uploaded resume
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text


# Helper function to extract score from AI response
def extract_score(response_text):
    import re
    match = re.search(r'(\d{1,3})/100', response_text)
    return int(match.group(1)) if match else 60  # Default score

# Helper function to extract keyword lists
def extract_keywords(response_text, section):
    start = response_text.find(section)
    if start == -1:
        return []
    end = response_text.find("\n\n", start)
    return response_text[start + len(section):end].strip().split(", ") if end != -1 else []

# Modify resume upload function
@csrf_exempt
def upload_resume(request):
    if request.method == "POST" and request.FILES.get("resume"):
        resume_file = request.FILES["resume"]
        job_description = request.POST.get("position", "Not specified")

        # Extract text from the PDF
        resume_text = extract_text_from_pdf(resume_file)

        # Get ATS Score
        ats_result = get_ats_score_google(resume_text, job_description)

        # Save the resume and ATS score
        resume = ResumeUpload(
            file_name=resume_file.name,
            file=resume_file,
            position=job_description,
            ats_score=ats_result["score"],
            ats_feedback=json.dumps(ats_result)
        )
        resume.save()

        return JsonResponse({
            "success": True,
            "id": resume.id,
            "ats_score": ats_result
        })
    
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_ats_feedback(request, resume_id):
    try:
        resume = ResumeUpload.objects.get(id=resume_id)
        if resume.ats_feedback:
            ats_feedback = json.loads(resume.ats_feedback)
            return JsonResponse(ats_feedback)
        else:
            return JsonResponse({"error": "No ATS feedback available"}, status=404)
    except ResumeUpload.DoesNotExist:
        return JsonResponse({"error": "Resume not found"}, status=404)

