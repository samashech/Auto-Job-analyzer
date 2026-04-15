const INTEGRATION_CONFIG = {
    EMAIL_NOTIFY_API: ''
};

let isSignupMode = false;
const appState = {
    fullName: '',
    registeredEmail: '',
    jobTitle: '',
    location: '',
    telegramId: '',
    resume: null,
    resumePhoto: null,
    jobs: [],
    interested: [],
    savedJobs: [],
    shareToken: Math.random().toString(36).substr(2, 9)
};

// ============ AUTH FUNCTIONS ============
function toggleAuthMode(mode) {
    isSignupMode = mode === 'signup';
    document.getElementById('authTitle').textContent = isSignupMode ? 'Create Professional Account' : 'Welcome Back';
    document.getElementById('authName').classList.toggle('hidden', !isSignupMode);
    document.getElementById('authName').required = isSignupMode;
    document.getElementById('authSubmitBtn').textContent = isSignupMode ? 'Sign Up' : 'Sign In';
    document.getElementById('authToggleText').textContent = isSignupMode ? 'Already have an account?' : "Don't have an account?";
    document.getElementById('authToggleBtn').textContent = isSignupMode ? 'Sign in' : 'Sign up';
    document.getElementById('authModal').classList.remove('hidden');

    // Clear errors when toggling
    document.getElementById('authErrorBanner').classList.add('hidden');
    document.getElementById('authName').classList.remove('error-border');
}

function closeAuthModal() {
    document.getElementById('authModal').classList.add('hidden');
}

async function handleAuthSubmit(e) {
    e.preventDefault();
    const nameInput = document.getElementById('authName');
    const name = nameInput.value.trim();
    const email = document.getElementById('authEmail').value.trim();
    const password = document.getElementById('authPassword').value;
    const errorBanner = document.getElementById('authErrorBanner');

    // STRICT VALIDATION: Do not allow sign up if name contains numbers
    if (isSignupMode) {
        if (!/^[A-Za-z\s]+$/.test(name)) {
            nameInput.classList.add('error-border');
            errorBanner.textContent = "Error: Name must contain only alphabets and spaces.";
            errorBanner.classList.remove('hidden');
            return;
        }

        if (password.length < 6) {
            errorBanner.textContent = "Error: Password must be at least 6 characters.";
            errorBanner.classList.remove('hidden');
            return;
        }
    }

    // Show loading state
    const submitBtn = document.getElementById('authSubmitBtn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = isSignupMode ? 'Creating Account...' : 'Signing In...';
    submitBtn.disabled = true;

    try {
        const endpoint = isSignupMode ? '/auth/signup' : '/auth/login';
        const payload = isSignupMode 
            ? { email, password, name }
            : { email, password };

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Authentication failed');
        }

        // Success - store user info
        appState.registeredEmail = email;
        appState.fullName = name || data.user.name;
        appState.userId = data.user.id;

        closeAuthModal();
        document.getElementById('landingPage').classList.add('hidden');

        // Save user info to session storage with all fields
        const userData = {
            id: data.user.id,
            name: data.user.name,
            email: data.user.email,
            skills: data.user.skills ? data.user.skills.split(',').map(s => s.trim()).filter(s => s) : [],
            level: data.user.level,
            location: data.user.location,
            job_type: data.user.job_type,
            job_role: data.user.job_role,
            resume_url: data.user.resume_url,
            has_resume_data: data.user.has_resume_data,
            profile_complete: data.user.profile_complete
        };
        sessionStorage.setItem('raiot_user', JSON.stringify(userData));

        // Restore appState
        if (data.user.skills) {
            appState.skills = data.user.skills.split(',').map(s => s.trim()).filter(s => s);
            appState.level = data.user.level;
            appState.location = data.user.location;
            appState.jobType = data.user.job_type;
            appState.jobRole = data.user.job_role;
        }

        // NEW ROUTING LOGIC based on profile state
        const profileComplete = data.user.profile_complete;
        const hasJobs = data.user.existing_jobs_count > 0;
        const hasResumeData = data.user.has_resume_data;

        if (profileComplete) {
            // Profile is fully complete - go straight to new dashboard
            window.location.href = '/dashboard';
            showBanner(`Welcome back, ${appState.fullName}!`, 'success', 'notifyBanner');
        } else if (hasResumeData && appState.skills && appState.skills.length > 0) {
            // Has resume data but profile not complete - go to complete profile
            document.getElementById('resumeDisplayPage').classList.add('hidden');
            document.getElementById('resumeEntryPage').classList.add('hidden');
            document.getElementById('resumeBuilderPage').classList.add('hidden');
            document.getElementById('dashboardPage').classList.add('hidden');
            window.location.href = '/complete-profile';
            showBanner(`Welcome back, ${appState.fullName}! Please complete your profile.`, 'success', 'notifyBanner');
        } else {
            // New user or no resume data - show upload page
            document.getElementById('resumeEntryPage').classList.remove('hidden');
            document.getElementById('resumeDisplayPage').classList.add('hidden');
            document.getElementById('resumeBuilderPage').classList.add('hidden');
            document.getElementById('dashboardPage').classList.add('hidden');
            showResumeEntryOptions();

            if (isSignupMode) {
                showBanner('Account created successfully! Now let\'s build your profile.', 'success', 'notifyBanner');
            } else {
                showBanner(`Welcome back, ${appState.fullName}! Upload your resume to get started.`, 'success', 'notifyBanner');
            }
        }

    } catch (error) {
        errorBanner.textContent = error.message;
        errorBanner.classList.remove('hidden');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

// ============ PASSWORD RESET FUNCTIONS ============
function showForgotPasswordModal() {
    document.getElementById('forgotPasswordModal').classList.remove('hidden');
    document.getElementById('otpRequestStep').classList.remove('hidden');
    document.getElementById('otpVerifyStep').classList.add('hidden');
    document.getElementById('forgotErrorBanner').classList.add('hidden');
    document.getElementById('forgotSuccessBanner').classList.add('hidden');
}

function closeForgotPasswordModal() {
    document.getElementById('forgotPasswordModal').classList.add('hidden');
}

async function sendOTP() {
    const email = document.getElementById('forgotEmail').value.trim();
    const errorBanner = document.getElementById('forgotErrorBanner');
    const successBanner = document.getElementById('forgotSuccessBanner');

    if (!email) {
        errorBanner.textContent = 'Please enter your registered email.';
        errorBanner.classList.remove('hidden');
        successBanner.classList.add('hidden');
        return;
    }

    try {
        const response = await fetch('/auth/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (response.ok) {
            successBanner.textContent = `OTP sent! (Demo OTP: ${data.demo_otp}) Check your console.`;
            successBanner.classList.remove('hidden');
            errorBanner.classList.add('hidden');
            document.getElementById('otpRequestStep').classList.add('hidden');
            document.getElementById('otpVerifyStep').classList.remove('hidden');
        } else {
            errorBanner.textContent = data.error || 'Failed to send OTP.';
            errorBanner.classList.remove('hidden');
            successBanner.classList.add('hidden');
        }
    } catch (error) {
        errorBanner.textContent = 'Network error. Please try again.';
        errorBanner.classList.remove('hidden');
        successBanner.classList.add('hidden');
    }
}

async function resetPassword() {
    const email = document.getElementById('forgotEmail').value.trim();
    const otp = document.getElementById('otpInput').value.trim();
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmNewPassword').value;
    const errorBanner = document.getElementById('forgotErrorBanner');
    const successBanner = document.getElementById('forgotSuccessBanner');

    if (!otp || !newPassword || !confirmPassword) {
        errorBanner.textContent = 'All fields are required.';
        errorBanner.classList.remove('hidden');
        successBanner.classList.add('hidden');
        return;
    }

    if (newPassword !== confirmPassword) {
        errorBanner.textContent = 'Passwords do not match.';
        errorBanner.classList.remove('hidden');
        successBanner.classList.add('hidden');
        return;
    }

    if (newPassword.length < 6) {
        errorBanner.textContent = 'Password must be at least 6 characters.';
        errorBanner.classList.remove('hidden');
        successBanner.classList.add('hidden');
        return;
    }

    try {
        const response = await fetch('/auth/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, otp, new_password: newPassword })
        });

        const data = await response.json();

        if (response.ok) {
            successBanner.textContent = 'Password reset successful! Please login.';
            successBanner.classList.remove('hidden');
            errorBanner.classList.add('hidden');
            setTimeout(() => {
                closeForgotPasswordModal();
                toggleAuthMode('login');
            }, 2000);
        } else {
            errorBanner.textContent = data.error || 'Failed to reset password.';
            errorBanner.classList.remove('hidden');
            successBanner.classList.add('hidden');
        }
    } catch (error) {
        errorBanner.textContent = 'Network error. Please try again.';
        errorBanner.classList.remove('hidden');
        successBanner.classList.add('hidden');
    }
}

// ============ RESUME ENTRY FUNCTIONS ============
function showResumeEntryOptions() {
    document.getElementById('uploadResumeForm').classList.add('hidden');
}

function showResumeUploadForm() {
    document.getElementById('uploadResumeForm').classList.remove('hidden');
    // Initialize drag and drop when form is shown
    initDragAndDrop();
}

// ============ DRAG & DROP FILE UPLOAD ============
let selectedResumeFile = null;

function initDragAndDrop() {
    const dropZone = document.getElementById('resumeDropZone');
    const fileInput = document.getElementById('resumeFile');
    const overlay = document.getElementById('dragOverlay');

    if (!dropZone || !fileInput) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            overlay.classList.remove('hidden');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            overlay.classList.add('hidden');
        }, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }, false);

    // Handle click to browse
    dropZone.addEventListener('click', (e) => {
        // Don't trigger if clicking the clear button
        if (e.target.closest('button')) return;
        fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFiles(e.target.files);
        }
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0];
    const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/markdown'
    ];

    const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt', '.md'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        showBanner('Invalid file type. Please upload PDF, DOC, DOCX, TXT, or MD files.', 'error', 'notifyBanner');
        return;
    }

    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showBanner('File too large. Maximum size is 10MB.', 'error', 'notifyBanner');
        return;
    }

    selectedResumeFile = file;
    
    // Update the hidden file input
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    document.getElementById('resumeFile').files = dataTransfer.files;

    // Update UI
    updateFileDisplay(file);
}

function updateFileDisplay(file) {
    const dropZoneContent = document.getElementById('dropZoneContent');
    const fileSelectedContent = document.getElementById('fileSelectedContent');
    const fileNameEl = document.getElementById('selectedFileName');
    const fileSizeEl = document.getElementById('selectedFileSize');

    if (!dropZoneContent || !fileSelectedContent) return;

    // Hide default content, show selected file
    dropZoneContent.classList.add('hidden');
    fileSelectedContent.classList.remove('hidden');

    // Update file info
    fileNameEl.textContent = file.name;
    fileSizeEl.textContent = formatFileSize(file.size);
}

function clearSelectedFile(e) {
    e.stopPropagation();
    
    selectedResumeFile = null;
    
    // Reset file input
    document.getElementById('resumeFile').value = '';
    
    // Reset UI
    const dropZoneContent = document.getElementById('dropZoneContent');
    const fileSelectedContent = document.getElementById('fileSelectedContent');
    
    if (dropZoneContent) dropZoneContent.classList.remove('hidden');
    if (fileSelectedContent) fileSelectedContent.classList.add('hidden');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

async function handleResumeUpload() {
    const fileInput = document.getElementById('resumeFile');
    const file = selectedResumeFile || fileInput.files[0];

    if (!file) {
        showBanner('Please upload your resume file.', 'error', 'notifyBanner');
        return;
    }

    // Show loading overlay
    const overlay = document.getElementById('processingOverlay');
    overlay.classList.remove('hidden');

    // Reset all steps
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        step.querySelector('div > div').classList.add('hidden');
        step.classList.remove('text-blue-600', 'font-semibold');
        step.classList.add('text-slate-600');
    }

    const jobType = document.getElementById('jobType').value;
    const experienceLevel = document.getElementById('experienceLevel').value;
    const preferredLocation = document.getElementById('preferredLocation').value;

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_type', jobType);
    formData.append('experience_level', experienceLevel);
    formData.append('preferred_location', preferredLocation);

    try {
        // Show a brief loading state
        const overlay = document.getElementById('processingOverlay');
        overlay.classList.remove('hidden');
        updateProcessingStep(1);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || 'Upload failed');

        // Save user data to session storage
        const userData = {
            id: data.user_id,
            name: data.name || appState.fullName,
            email: data.email || appState.registeredEmail,
            phone: data.phone || '',
            level: data.level,
            skills: data.skills || [],
            job_type: data.job_type || jobType,
            experience_level: data.experience_level || experienceLevel,
            preferred_location: data.preferred_location || preferredLocation,
            resume_url: data.resume_url,
            fileName: file.name
        };
        sessionStorage.setItem('raiot_user', JSON.stringify(userData));

        appState.userId = data.user_id;
        appState.fullName = userData.name;
        appState.registeredEmail = userData.email;

        // Step 2: Redirect to complete profile page
        updateProcessingStep(2);
        await sleep(500);

        // Hide overlay and redirect
        overlay.classList.add('hidden');
        showBanner('Resume analyzed! Redirecting to complete your profile...', 'success', 'notifyBanner');

        // Redirect to complete profile page
        setTimeout(() => {
            window.location.href = data.redirect || '/complete-profile';
        }, 1000);

    } catch (error) {
        overlay.classList.add('hidden');
        showBanner(error.message, 'error', 'notifyBanner');
    }
}

function updateProcessingStep(stepNum) {
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step${i}`);
        const dot = step.querySelector('div > div');

        if (i < stepNum) {
            // Completed steps
            dot.classList.remove('hidden');
            dot.style.backgroundColor = '#10b981'; // Green
            step.classList.remove('text-slate-600');
            step.classList.add('text-emerald-600', 'font-semibold');
            step.querySelector('span').textContent = step.querySelector('span').textContent.replace('...', ' ✓');
        } else if (i === stepNum) {
            // Current step
            dot.classList.remove('hidden');
            dot.style.backgroundColor = '#2563eb'; // Blue
            step.classList.remove('text-slate-600');
            step.classList.add('text-blue-600', 'font-semibold');
        } else {
            // Future steps
            dot.classList.add('hidden');
            step.classList.remove('text-blue-600', 'font-semibold', 'text-emerald-600');
            step.classList.add('text-slate-600');
        }
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function navigateToResumeBuilder() {
    document.getElementById('resumeEntryPage').classList.add('hidden');
    document.getElementById('resumeBuilderPage').classList.remove('hidden');
}

function resumeEntryBackClick() {
    document.getElementById('resumeBuilderPage').classList.add('hidden');
    document.getElementById('resumeEntryPage').classList.remove('hidden');
    showResumeEntryOptions();
}

function goToUpdateResume() {
    document.getElementById('dashboardPage').classList.add('hidden');
    document.getElementById('resumeEntryPage').classList.remove('hidden');
    showResumeEntryOptions();
}

// ============ FORM VALIDATION ============
function clearErrors(form) {
    const errorTexts = form.querySelectorAll('.error-text');
    errorTexts.forEach(el => el.remove());
    const errorInputs = form.querySelectorAll('.error-border');
    errorInputs.forEach(el => el.classList.remove('error-border'));
}

function showError(input, message) {
    input.classList.add('error-border');
    const errorEl = document.createElement('span');
    errorEl.className = 'error-text';
    errorEl.textContent = message;
    input.parentNode.appendChild(errorEl);
}

function validateBuilderForm(form) {
    clearErrors(form);
    let isValid = true;

    const nameInput = form.querySelector('[name="fullName"]');
    if (!/^[A-Za-z\s]+$/.test(nameInput.value.trim())) {
        showError(nameInput, 'Only alphabets are allowed.');
        isValid = false;
    }

    const contactInput = form.querySelector('[name="contactNumber"]');
    if (!/^\d{10}$/.test(contactInput.value.trim())) {
        showError(contactInput, 'Must be exactly 10 numeric digits.');
        isValid = false;
    }

    const urlFields = ['linkedin', 'github', 'portfolio'];
    urlFields.forEach(field => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input.value && !/^https?:\/\/.+/.test(input.value.trim())) {
            showError(input, 'Please enter a valid URL starting with http:// or https://');
            isValid = false;
        }
    });

    const textFields = ['about', 'education', 'technicalSkills', 'softSkills', 'experienceAchievements', 'projects', 'certifications'];
    textFields.forEach(field => {
        const input = form.querySelector(`[name="${field}"]`);
        const wordCount = input.value.trim().split(/\s+/).filter(word => word.length > 0).length;
        if (wordCount < 20) {
            showError(input, `Minimum 20 words required. (Currently: ${wordCount})`);
            isValid = false;
        }
    });

    return isValid;
}

// ============ RESUME BUILDER SUBMIT ============
async function handleResumeBuilderSubmit(e) {
    e.preventDefault();

    if (!validateBuilderForm(e.target)) {
        const firstError = e.target.querySelector('.error-border');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        showBanner('Please fix the errors in the form before proceeding.', 'error', 'notifyBannerBuilder');
        return;
    }

    const form = new FormData(e.target);
    const profile = Object.fromEntries(form.entries());

    appState.fullName = profile.fullName;
    appState.registeredEmail = profile.professionalEmail;
    appState.jobTitle = profile.jobTitle;
    appState.location = profile.location;
    appState.resume = profile;

    const photoInput = document.getElementById('builderPhoto');
    if (photoInput.files[0]) {
        const reader = new FileReader();
        reader.onload = (ev) => {
            appState.resumePhoto = ev.target.result;
            generateResumeDisplay();
        };
        reader.readAsDataURL(photoInput.files[0]);
    } else {
        generateResumeDisplay();
    }
}

function generateResumeDisplay() {
    document.getElementById('resumeBuilderPage').classList.add('hidden');
    document.getElementById('uploadResumeForm').classList.add('hidden');
    document.getElementById('resumeEntryPage').classList.add('hidden');
    document.getElementById('resumeDisplayPage').classList.remove('hidden');
    renderProfessionalResume();
}

function renderProfessionalResume() {
    const resume = appState.resume;
    const container = document.getElementById('resumeContainer');

    // Show uploaded resume PDF if available
    if (resume && resume.uploadedMode && resume.resumeUrl) {
        container.innerHTML = `
            <div class="flex flex-col items-center">
                <h2 class="text-2xl font-bold text-slate-900 mb-6">Your Professional Resume</h2>
                ${appState.resumePhoto ? `<img src="${appState.resumePhoto}" alt="Profile" class="w-32 h-32 rounded-full object-cover border-4 border-blue-600 mb-6">` : `<div class="w-32 h-32 rounded-full bg-slate-200 flex items-center justify-center mb-6 text-slate-400 text-4xl">👤</div>`}
                <h1 class="text-3xl font-bold text-slate-900 text-center mb-2">${resume.fullName || appState.fullName || 'Your Name'}</h1>
                <p class="text-blue-600 font-semibold text-center mb-6">${resume.jobTitle || 'Professional'}</p>
                ${resume.resumeUrl.toLowerCase().endsWith('.pdf') ? 
                    `<iframe src="${resume.resumeUrl}" class="w-full h-[900px] border border-slate-200 rounded-lg"></iframe>` :
                    `<div class="p-8 text-center text-slate-600">
                        <p class="text-lg mb-4">Resume file available</p>
                        <a href="${resume.resumeUrl}" target="_blank" class="text-blue-600 hover:underline">View Resume</a>
                    </div>`
                }
            </div>
        `;
        return;
    }

    // Show builder-created resume
    if (!resume) {
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="text-6xl mb-4">📄</div>
                <h3 class="text-2xl font-bold text-slate-900 mb-3">No Resume Data</h3>
                <p class="text-slate-600">Please upload or create a resume first.</p>
            </div>
        `;
        return;
    }

    let html = `
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div class="md:col-span-1 flex flex-col items-center">
                ${appState.resumePhoto ? `<img src="${appState.resumePhoto}" alt="Profile" class="w-32 h-32 rounded-full object-cover border-4 border-blue-600 mb-4">` : `<div class="w-32 h-32 rounded-full bg-slate-200 flex items-center justify-center mb-4 text-slate-400 text-4xl">👤</div>`}
                <h1 class="text-2xl font-bold text-slate-900 text-center">${resume.fullName || 'Your Name'}</h1>
                <p class="text-blue-600 font-semibold text-center">${resume.jobTitle || 'Professional Title'}</p>
                <div class="mt-6 pt-6 border-t border-slate-200 w-full text-sm space-y-3 text-slate-700">
                    <div class="break-words"><strong>Email:</strong> ${resume.professionalEmail || ''}</div>
                    <div><strong>Phone:</strong> ${resume.contactNumber || ''}</div>
                    <div><strong>Location:</strong> ${resume.location || ''}</div>
                    ${resume.linkedin ? `<div><a href="${resume.linkedin}" target="_blank" class="text-blue-600 hover:underline">LinkedIn</a></div>` : ''}
                    ${resume.github ? `<div><a href="${resume.github}" target="_blank" class="text-blue-600 hover:underline">GitHub</a></div>` : ''}
                    ${resume.portfolio ? `<div><a href="${resume.portfolio}" target="_blank" class="text-blue-600 hover:underline">Portfolio</a></div>` : ''}
                </div>
            </div>

            <div class="md:col-span-3 space-y-6">
                <div><h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">PROFESSIONAL SUMMARY</h2><p class="text-slate-700 text-sm leading-relaxed">${resume.about || ''}</p></div>
                <div>
                    <h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">SKILLS</h2>
                    ${resume.chartUrl ? `<div class="mb-4"><img src="${resume.chartUrl}" alt="Skills Chart" class="w-full max-w-md mx-auto rounded-lg border border-slate-200"></div>` : ''}
                    <div class="grid grid-cols-2 gap-4">
                        <div><p class="font-semibold text-slate-900 text-sm mb-1">Technical</p><p class="text-slate-700 text-sm">${resume.technicalSkills || ''}</p></div>
                        <div><p class="font-semibold text-slate-900 text-sm mb-1">Professional</p><p class="text-slate-700 text-sm">${resume.softSkills || ''}</p></div>
                    </div>
                </div>
                <div><h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">EXPERIENCE & ACHIEVEMENTS</h2><p class="text-slate-700 text-sm whitespace-pre-wrap">${resume.experienceAchievements || ''}</p></div>
                <div><h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">EDUCATION</h2><p class="text-slate-700 text-sm">${resume.education || ''}</p></div>
                <div><h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">KEY PROJECTS</h2><p class="text-slate-700 text-sm whitespace-pre-wrap">${resume.projects || ''}</p></div>
                <div><h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">CERTIFICATIONS</h2><p class="text-slate-700 text-sm">${resume.certifications || ''}</p></div>
            </div>
        </div>
    `;
    container.innerHTML = html;
}

function downloadResumePDF() {
    const element = document.getElementById('resumeContainer');
    const opt = { margin: 10, filename: `${appState.fullName || 'Resume'}.pdf`, image: { type: 'jpeg', quality: 0.98 }, html2canvas: { scale: 2 }, jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' } };
    html2pdf().set(opt).from(element).save();
    showBanner('Resume downloaded as PDF!', 'success', 'notifyBannerResume');
}

function shareResume() {
    document.getElementById('shareModal').classList.remove('hidden');
    document.getElementById('shareLink').value = `https://raiot.app/resume/${appState.shareToken}`;
}

function closeShareModal() {
    document.getElementById('shareModal').classList.add('hidden');
}

function copyToClipboard() {
    const link = document.getElementById('shareLink');
    link.select();
    document.execCommand('copy');
    showBanner('Share link copied to clipboard!', 'success', 'notifyBannerResume');
}

function emailResume() {
    const email = document.getElementById('shareEmail').value;
    if (!email) return showBanner('Please enter an email address', 'warning', 'notifyBannerResume');
    showBanner(`Resume share link sent to ${email}!`, 'success', 'notifyBannerResume');
    setTimeout(() => closeShareModal(), 2000);
}

function continueToJobMatching() {
    document.getElementById('resumeDisplayPage').classList.add('hidden');
    document.getElementById('dashboardPage').classList.remove('hidden');
    loadAndDisplayJobs();
}

function viewMyResume() {
    document.getElementById('dashboardPage').classList.add('hidden');
    document.getElementById('resumeDisplayPage').classList.remove('hidden');

    // If resume data is not in appState, try to load from session or backend
    if (!appState.resume || Object.keys(appState.resume).length === 0) {
        const userData = sessionStorage.getItem('raiot_user');
        if (userData) {
            const user = JSON.parse(userData);
            appState.resume = {
                uploadedMode: true,
                fullName: user.name || appState.fullName,
                professionalEmail: user.email || appState.registeredEmail,
                technicalSkills: user.skills ? user.skills.join(', ') : '',
                resumeUrl: user.resume_url || '',
                fileName: user.fileName || 'Resume.pdf'
            };
        }
    }

    renderProfessionalResume();
}

// ============ JOB MATCHING & DASHBOARD FUNCTIONS ============
async function loadAndDisplayJobs() {
    switchTab('jobs');

    // Load saved jobs from localStorage
    loadSavedJobs();

    // If we have a user ID, load from database first
    if (appState.userId) {
        await loadJobsFromDatabase(appState.userId);
    } else {
        // Check if we have live jobs from session storage
        const storedJobs = sessionStorage.getItem('raiot_jobs');
        if (storedJobs) {
            appState.jobs = JSON.parse(storedJobs);
        } else {
            // Fallback: fetch jobs normally
            await fetchJobsFallback();
        }
    }

    renderJobs();
    renderInterested();
    renderSavedJobs();
}

function connectToRealTimeJobStream() {
    if (!appState.userId) return;

    const eventSource = new EventSource(`/stream-jobs/${appState.userId}`);

    eventSource.onmessage = function(event) {
        const message = JSON.parse(event.data);

        if (message.type === 'init') {
            // Initial state - replace all jobs
            appState.jobs = message.data.jobs.map((job, index) => ({
                id: index + 1,
                title: job.title || `Role`,
                company: job.company || "Various Companies",
                source: job.name || job.source || "Scraper",
                matchScore: job.relevance_score || 0,
                description: job.description || '',
                url: job.url,
                skillCat: job.name || "Scraped Result"
            }));
            renderJobs();
        } else if (message.type === 'job') {
            // New job found - add to list
            const newJob = {
                id: appState.jobs.length + 1,
                title: message.data.title || `Role`,
                company: message.data.company || "Various Companies",
                source: message.data.name || message.data.source || "Scraper",
                matchScore: message.data.relevance_score || 0,
                description: message.data.description || '',
                url: message.data.url,
                skillCat: message.data.name || "Scraped Result"
            };
            appState.jobs.push(newJob);
            renderJobs();
        } else if (message.type === 'complete') {
            // Scraping complete
            console.log(`Scraping complete: ${message.data.total_jobs} jobs found`);
        }
    };

    eventSource.onerror = function() {
        console.log('SSE connection closed');
        eventSource.close();
    };
}

async function fetchJobsFallback() {
    // Fallback for when SSE is not available
    if (appState.resume && appState.jobs.length === 0) {
        showBanner('Fetching matched jobs...', 'info', 'notifyBannerDash');
        try {
            const response = await fetch('/fetch_jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    skills: appState.resume.technicalSkills,
                    level: appState.jobTitle || 'Experienced',
                    job_type: 'Full-time'
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || 'Job fetching failed');

            if (data.jobs && data.jobs.length > 0) {
                appState.jobs = data.jobs.map((job, index) => ({
                    id: index + 1,
                    title: job.title || `Role`,
                    company: job.company || "Various Companies",
                    source: job.name || job.source || "Scraper",
                    matchScore: job.relevance_score || 0,
                    description: job.description || (data.skills ? `Job matching your skills: ${data.skills.slice(0,3).join(', ')}` : ''),
                    url: job.url,
                    skillCat: job.name || "Scraped Result"
                }));
            } else {
                appState.jobs = [];
            }
        } catch (error) {
            showBanner(error.message, 'error', 'notifyBannerDash');
            appState.jobs = [];
        }
    }
}

function refreshJobs() {
    console.log(`🔄 Manually refreshing jobs...`);
    showBanner('Loading latest jobs...', 'info', 'notifyBannerDash');

    // Stop any existing polling
    if (jobPollingInterval) {
        clearInterval(jobPollingInterval);
        jobPollingInterval = null;
    }

    // Reload from database
    if (appState.userId) {
        loadJobsFromDatabase(appState.userId);
    } else {
        // Try to get user from session
        const userData = sessionStorage.getItem('raiot_user');
        if (userData) {
            const user = JSON.parse(userData);
            appState.userId = user.id;
            loadJobsFromDatabase(user.id);
        } else {
            showBanner('No user session found. Please upload a resume first.', 'error', 'notifyBannerDash');
        }
    }
}

function renderJobs() {
    const container = document.getElementById('jobsContent');
    if (appState.jobs.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12">
                <div class="text-6xl mb-4">🔍</div>
                <h3 class="text-2xl font-bold text-slate-900 mb-3">No Relevant Jobs Found</h3>
                <p class="text-slate-600 mb-6 max-w-md mx-auto">We couldn't find job postings that match your specific skills. This means either:</p>
                <ul class="text-sm text-slate-600 max-w-md mx-auto space-y-2 text-left">
                    <li>• The job sites may not have current postings for your skill set</li>
                    <li>• Your resume contains highly specialized skills</li>
                </ul>
                <p class="text-sm text-slate-600 mt-4">Try updating your resume with more in-demand technical skills, or check back later as new jobs are posted daily.</p>
            </div>
        `;
        return;
    }

    const categories = [...new Set(appState.jobs.map(j => j.skillCat))];

    container.innerHTML = categories.map(cat => {
        const catJobs = appState.jobs.filter(j => j.skillCat === cat);
        return `
            <div class="mb-10">
                <h3 class="text-2xl font-bold text-slate-900 border-b-2 border-blue-200 pb-2 mb-6">Matched from: <span class="text-blue-600">${cat}</span></h3>
                <div class="grid md:grid-cols-2 gap-6">
                    ${catJobs.map(job => `
                        <div class="bg-white rounded-xl border border-slate-200 hover:shadow-lg hover:border-blue-300 transition overflow-hidden">
                            <div class="p-6">
                                <div class="flex items-start justify-between mb-4 gap-4">
                                    <div>
                                        <h3 class="text-lg font-bold text-slate-900">${job.title}</h3>
                                        <p class="text-slate-600 font-medium">${job.company}</p>
                                    </div>
                                    <div class="text-right flex items-center gap-3">
                                        <button onclick="toggleSaveJob(${job.id})" class="text-2xl ${isJobSaved(job.id) ? 'text-yellow-500' : 'text-slate-300'} hover:text-yellow-500 transition">
                                            ${isJobSaved(job.id) ? '★' : '☆'}
                                        </button>
                                        <div>
                                            <div class="text-2xl font-bold ${job.matchScore >= 50 ? 'text-emerald-600' : job.matchScore >= 25 ? 'text-yellow-600' : 'text-orange-600'}">${job.matchScore || 0}%</div>
                                            <p class="text-xs text-slate-500">Match</p>
                                        </div>
                                    </div>
                                </div>
                                <p class="text-sm text-slate-600 mb-4">${job.description || ''}</p>
                                <div class="flex gap-2 mt-4">
                                    <a href="${job.url || '#'}" target="_blank" onclick="applyJob(${job.id})" class="flex-1 text-center px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 cursor-pointer">Apply Now</a>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }).join('');
}

function renderInterested() {
    const tbody = document.getElementById('interestedTable');
    if (!appState.interested.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-slate-600">No applications yet. Browse jobs and apply!</td></tr>';
        return;
    }
    tbody.innerHTML = appState.interested.map((job) => `
        <tr class="border-b border-slate-200 hover:bg-slate-50">
            <td class="px-6 py-4 font-semibold text-slate-900">${job.title}</td>
            <td class="px-6 py-4 text-slate-600">${job.company}</td>
            <td class="px-6 py-4 text-slate-600">${job.source || 'N/A'}</td>
            <td class="px-6 py-4 text-right">
                <a href="${job.url || '#'}" target="_blank" class="text-blue-600 hover:underline font-semibold text-sm cursor-pointer">View Job</a>
            </td>
        </tr>
    `).join('');
}

// ============ SAVED JOBS FUNCTIONS ============
function loadSavedJobs() {
    const saved = localStorage.getItem('raiot_saved_jobs');
    if (saved) {
        appState.savedJobs = JSON.parse(saved);
    } else {
        appState.savedJobs = [];
    }
}

function saveSavedJobs() {
    localStorage.setItem('raiot_saved_jobs', JSON.stringify(appState.savedJobs));
}

function isJobSaved(jobId) {
    return appState.savedJobs.some(j => j.id === jobId);
}

function toggleSaveJob(jobId) {
    const job = appState.jobs.find(j => j.id === jobId);
    if (!job) return;

    const index = appState.savedJobs.findIndex(j => j.id === jobId);
    if (index >= 0) {
        // Remove from saved
        appState.savedJobs.splice(index, 1);
        showBanner('Job removed from saved list.', 'info', 'notifyBannerDash');
    } else {
        // Add to saved
        appState.savedJobs.push({ ...job, savedAt: new Date().toISOString() });
        showBanner('Job saved for later!', 'success', 'notifyBannerDash');
    }

    saveSavedJobs();
    renderJobs();
    renderSavedJobs();
}

function renderSavedJobs() {
    const tbody = document.getElementById('savedTable');
    if (!appState.savedJobs.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-slate-600">No saved jobs yet. Click the star icon on any job to save it!</td></tr>';
        return;
    }
    tbody.innerHTML = appState.savedJobs.map((job) => `
        <tr class="border-b border-slate-200 hover:bg-slate-50">
            <td class="px-6 py-4 font-semibold text-slate-900">${job.title}</td>
            <td class="px-6 py-4 text-slate-600">${job.company}</td>
            <td class="px-6 py-4 text-slate-600">${job.source || 'N/A'}</td>
            <td class="px-6 py-4 text-right">
                <button onclick="toggleSaveJob(${job.id})" class="text-red-600 hover:underline font-semibold text-sm cursor-pointer">Remove</button>
            </td>
        </tr>
    `).join('');
}

function applyJob(jobId) {
    const job = appState.jobs.find((j) => j.id === jobId);
    if (job && !appState.interested.find((j) => j.id === jobId)) {
        appState.interested.unshift({ ...job, status: 'Applied' });
        renderInterested();
        showBanner(`Application tracked for ${job.title} at ${job.company}!`, 'success', 'notifyBannerDash');
    }
}

function sortJobs(sortBy) {
    if (!appState.jobs.length) return;

    switch (sortBy) {
        case 'match':
            appState.jobs.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
            break;
        case 'location':
            appState.jobs.sort((a, b) => (a.company || '').localeCompare(b.company || ''));
            break;
        case 'salary':
            // Salary info not available in current scraper, fallback to match score
            appState.jobs.sort((a, b) => (b.matchScore || 0) - (a.matchScore || 0));
            showBanner('Salary info not available. Sorting by match score instead.', 'info', 'notifyBannerDash');
            break;
    }

    renderJobs();
}

function switchTab(tab) {
    ['jobs', 'interested', 'saved'].forEach((name) => {
        const tabEl = document.getElementById(`${name}Tab`);
        if (tabEl) {
            tabEl.classList.toggle('border-blue-600', tab === name);
            tabEl.classList.toggle('text-blue-600', tab === name);
            tabEl.classList.toggle('border-transparent', tab !== name);
            tabEl.classList.toggle('text-slate-600', tab !== name);
        }
    });
    document.getElementById('jobsContent').classList.toggle('hidden', tab !== 'jobs');
    document.getElementById('interestedContent').classList.toggle('hidden', tab !== 'interested');
    document.getElementById('savedContent').classList.toggle('hidden', tab !== 'saved');
}

function showBanner(message, type, bannerId) {
    const banner = document.getElementById(bannerId);
    if(!banner) return;
    const styles = {
        success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
        warning: 'bg-amber-50 border-amber-200 text-amber-800',
        error: 'bg-red-50 border-red-200 text-red-800',
        info: 'bg-blue-50 border-blue-200 text-blue-800'
    };
    banner.className = `mb-6 px-4 py-3 rounded-lg border text-sm font-medium ${styles[type] || styles.info}`;
    banner.textContent = message;
    banner.classList.remove('hidden');
    setTimeout(() => { banner.classList.add('hidden'); }, 4000);
}

async function logout() {
    const userId = appState.userId;

    // Call backend logout endpoint (stops scraping + clears session)
    try {
        await fetch('/auth/logout', { method: 'POST' });
    } catch (error) {
        console.error('Logout error:', error);
    }

    // Clear all local state
    appState.fullName = '';
    appState.registeredEmail = '';
    appState.resume = null;
    appState.jobs = [];
    appState.interested = [];
    appState.savedJobs = [];
    appState.skills = [];
    appState.level = '';
    appState.userId = null;

    // Clear session storage
    sessionStorage.removeItem('raiot_user');
    sessionStorage.removeItem('raiot_jobs');

    // Hide all app pages
    document.getElementById('resumeEntryPage').classList.add('hidden');
    document.getElementById('resumeBuilderPage').classList.add('hidden');
    document.getElementById('resumeDisplayPage').classList.add('hidden');
    document.getElementById('dashboardPage').classList.add('hidden');

    // Show landing page and redirect to root
    document.getElementById('landingPage').classList.remove('hidden');
    window.location.href = '/';

    showBanner('Logged out successfully!', 'info', 'notifyBanner');
}

document.getElementById('authForm').addEventListener('submit', handleAuthSubmit);
document.getElementById('authToggleBtn').addEventListener('click', function() {
    toggleAuthMode(isSignupMode ? 'login' : 'signup');
});
document.getElementById('resumeBuilderForm').addEventListener('submit', handleResumeBuilderSubmit);

// Restore session on page load
async function restoreSession() {
    // First check sessionStorage (fast path for same-session)
    const storedUser = sessionStorage.getItem('raiot_user');
    if (storedUser) {
        try {
            const user = JSON.parse(storedUser);
            if (user && user.id) {
                appState.fullName = user.name;
                appState.registeredEmail = user.email;
                appState.userId = user.id;
                appState.skills = user.skills || [];
                appState.level = user.level;
                appState.location = user.location;
                appState.jobType = user.job_type;
                appState.jobRole = user.job_role;
                return true;
            }
        } catch (e) {
            console.warn('Failed to parse stored user:', e);
        }
    }

    // Fall back to server session check
    try {
        const response = await fetch('/auth/check-session');
        const data = await response.json();
        if (data.logged_in && data.user) {
            appState.fullName = data.user.name;
            appState.registeredEmail = data.user.email;
            appState.userId = data.user.id;
            appState.skills = data.user.skills ? data.user.skills.split(',').map(s => s.trim()).filter(s => s) : [];
            appState.level = data.user.level;
            appState.location = data.user.location;
            appState.jobType = data.user.job_type;
            appState.jobRole = data.user.job_role;

            // Store for future use with all fields
            sessionStorage.setItem('raiot_user', JSON.stringify({
                id: data.user.id,
                name: data.user.name,
                email: data.user.email,
                skills: appState.skills,
                level: data.user.level,
                location: data.user.location,
                job_type: data.user.job_type,
                job_role: data.user.job_role,
                resume_url: data.user.resume_url,
                has_resume_data: data.user.has_resume_data,
                profile_complete: data.user.profile_complete
            }));
            return true;
        }
    } catch (e) {
        console.warn('Session check failed:', e);
    }
    return false;
}

// Run session restore on page load
document.addEventListener('DOMContentLoaded', async () => {
    const isLoggedIn = await restoreSession();
    if (isLoggedIn && appState.userId) {
        // User is logged in - check profile completion status
        const storedUser = sessionStorage.getItem('raiot_user');
        let profileComplete = false;
        let hasJobs = false;

        if (storedUser) {
            try {
                const user = JSON.parse(storedUser);
                profileComplete = user.profile_complete || false;
            } catch (e) {}
        }

        // Check if user has jobs
        try {
            const response = await fetch(`/get-jobs/${appState.userId}`);
            const data = await response.json();
            hasJobs = data.total > 0;
        } catch (e) {
            console.warn('Failed to load jobs on session restore:', e);
        }

        // Route based on profile state
        if (profileComplete) {
            // Profile is complete - go to new dashboard
            document.getElementById('landingPage').classList.add('hidden');
            document.getElementById('resumeDisplayPage').classList.add('hidden');
            document.getElementById('resumeEntryPage').classList.add('hidden');
            document.getElementById('resumeBuilderPage').classList.add('hidden');
            document.getElementById('dashboardPage').classList.add('hidden');
            // Redirect to new dashboard page
            window.location.href = '/dashboard';
        } else if (appState.skills && appState.skills.length > 0) {
            // Has resume data but profile not complete - go to complete profile
            document.getElementById('landingPage').classList.add('hidden');
            document.getElementById('resumeDisplayPage').classList.add('hidden');
            document.getElementById('resumeEntryPage').classList.add('hidden');
            document.getElementById('resumeBuilderPage').classList.add('hidden');
            document.getElementById('dashboardPage').classList.add('hidden');
            // Redirect to complete profile page
            window.location.href = '/complete-profile';
        } else {
            // No resume data - stay on landing page, user needs to upload
            // Landing page is already visible
        }
    }
});

// Handle hash-based routing (for legacy dashboard - kept for backwards compatibility)
window.addEventListener('hashchange', handleHashRoute);
window.addEventListener('load', handleHashRoute);

function handleHashRoute() {
    const hash = window.location.hash;

    if (hash === '#dashboard') {
        // Check if user has jobs in session
        const userData = sessionStorage.getItem('raiot_user');

        if (userData) {
            const user = JSON.parse(userData);
            appState.userId = user.id;
            appState.fullName = user.name;
            appState.registeredEmail = user.email;
            appState.skills = user.skills || [];
            appState.level = user.level;
            appState.resume = {
                uploadedMode: true,
                fullName: user.name,
                professionalEmail: user.email,
                technicalSkills: user.skills ? user.skills.join(', ') : ''
            };

            // If user has no skills (never uploaded), redirect to landing
            if (!user.skills || user.skills.length === 0) {
                window.location.hash = '';
                document.getElementById('dashboardPage').classList.add('hidden');
                document.getElementById('landingPage').classList.remove('hidden');
                return;
            }

            // Show dashboard
            document.getElementById('landingPage').classList.add('hidden');
            document.getElementById('resumeEntryPage').classList.add('hidden');
            document.getElementById('resumeBuilderPage').classList.add('hidden');
            document.getElementById('resumeDisplayPage').classList.add('hidden');
            document.getElementById('dashboardPage').classList.remove('hidden');

            // Load jobs from database directly (most reliable)
            loadJobsFromDatabase(user.id);
        } else {
            // No user data, redirect to landing
            window.location.hash = '';
        }
    }
}

async function loadJobsFromDatabase(userId) {
    try {
        console.log(`=== LOADING JOBS FROM DATABASE ===`);
        console.log(`User ID: ${userId}`);
        console.log(`Session jobs before load: ${JSON.parse(sessionStorage.getItem('raiot_jobs') || '[]').length}`);

        const response = await fetch(`/get-jobs/${userId}`);
        const data = await response.json();

        console.log(`Database response: ${data.total} jobs (source: ${data.source})`);

        if (data.jobs && data.jobs.length > 0) {
            console.log(`✅ Loaded ${data.total} jobs from ${data.source}`);
            console.log(`First job:`, data.jobs[0]);

            appState.jobs = data.jobs.map((job, index) => ({
                id: job.id || index + 1,
                title: job.title || `Role`,
                company: job.company || "Various Companies",
                source: job.source || job.name || "Scraper",
                matchScore: job.relevance_score || 0,
                description: job.description || '',
                url: job.url,
                skillCat: job.source || job.name || "Scraped Result"
            }));

            // Save to session storage
            sessionStorage.setItem('raiot_jobs', JSON.stringify(appState.jobs));

            renderJobs();

            // If scraping is still in progress, poll for more jobs every 5 seconds
            checkAndPollForMoreJobs(userId);
        } else {
            console.log(`⚠️ No jobs found yet, polling for updates...`);
            showBanner('Jobs are still being scraped! This page will auto-refresh...', 'info', 'notifyBannerDash');
            startJobPolling(userId);
        }
    } catch (error) {
        console.error('❌ Error loading jobs:', error);

        // Last resort: try session storage
        const storedJobs = sessionStorage.getItem('raiot_jobs');
        if (storedJobs) {
            appState.jobs = JSON.parse(storedJobs);
            console.log(`💾 Loaded ${appState.jobs.length} jobs from session storage after error`);
            renderJobs();
        }
    }
}

let jobPollingInterval = null;

function startJobPolling(userId) {
    // Clear any existing polling
    if (jobPollingInterval) {
        clearInterval(jobPollingInterval);
    }

    // Poll every 3 seconds
    jobPollingInterval = setInterval(async () => {
        try {
            const response = await fetch(`/get-jobs/${userId}`);
            const data = await response.json();

            console.log(`🔄 Polling: ${data.total} jobs found`);

            if (data.jobs && data.jobs.length > 0) {
                appState.jobs = data.jobs.map((job, index) => ({
                    id: job.id || index + 1,
                    title: job.title || `Role`,
                    company: job.company || "Various Companies",
                    source: job.source || job.name || "Scraper",
                    matchScore: job.relevance_score || 0,
                    description: job.description || '',
                    url: job.url,
                    skillCat: job.source || job.name || "Scraped Result"
                }));

                sessionStorage.setItem('raiot_jobs', JSON.stringify(appState.jobs));
                renderJobs();

                // If we have 20+ jobs or scraping is complete, stop polling
                if (data.total >= 20) {
                    console.log(`✅ Got enough jobs (${data.total}), stopping poll`);
                    clearInterval(jobPollingInterval);
                    showBanner(`Found ${data.total} jobs!`, 'success', 'notifyBannerDash');
                }
            }
        } catch (error) {
            console.error('Poll error:', error);
        }
    }, 3000); // Poll every 3 seconds
}

function checkAndPollForMoreJobs(userId) {
    // If we have jobs but might get more, keep polling
    if (appState.jobs.length > 0 && appState.jobs.length < 20) {
        startJobPolling(userId);
    }
}
