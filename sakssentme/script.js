const INTEGRATION_CONFIG = {
    EMAIL_NOTIFY_API: ''
};

let isSignupMode = false;
const appState = {
    fullName: '',
    registeredEmail: '',
    jobTitle: '',
    location: '',
    resume: null,
    resumePhoto: null,
    jobs: [],
    interested: [],
    shareToken: Math.random().toString(36).substr(2, 9)
};

// Default fallback jobs for general tracking
const fallbackJobs = [
    { id: 101, title: 'Backend Engineer', company: 'TechCorp', location: 'Remote', salary: '$120K - $150K', source: 'Indeed', description: 'Build scalable APIs.', matchScore: 88, url: '#', skillCat: 'General' },
    { id: 102, title: 'Frontend Developer', company: 'WebSolutions', location: 'New York', salary: '$100K - $130K', source: 'LinkedIn', description: 'Create dynamic user interfaces.', matchScore: 85, url: '#', skillCat: 'General' }
];

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
    const errorBanner = document.getElementById('authErrorBanner');

    // STRICT VALIDATION: Do not allow sign up if name contains numbers
    if (isSignupMode) {
        if (!/^[A-Za-z\s]+$/.test(name)) {
            nameInput.classList.add('error-border');
            errorBanner.textContent = "Error: Name must contain only alphabets and spaces.";
            errorBanner.classList.remove('hidden');
            return; // STRICT RETURN: Stop execution right here.
        }
    }

    appState.registeredEmail = email;

    closeAuthModal();
    document.getElementById('landingPage').classList.add('hidden');

    if (isSignupMode) {
        // New User Flow
        appState.fullName = name || 'Professional';
        document.getElementById('resumeEntryPage').classList.remove('hidden');
        showResumeEntryOptions();
        showBanner('Professional account created! Now let\'s build your profile.', 'success', 'notifyBanner');
    } else {
        // Old User Flow - Skip directly to Dashboard
        appState.fullName = "Returning Professional"; // Mock data
        
        // Mocking an existing resume for the old user
        appState.resume = {
            fullName: appState.fullName,
            technicalSkills: "Python, Web Developer, Data Scientist",
            jobTitle: "Senior Engineer"
        };
        
        document.getElementById('dashboardPage').classList.remove('hidden');
        loadAndDisplayJobs();
        showBanner(`Welcome back! Your dashboard is ready.`, 'success', 'notifyBannerDash');
    }
}

// ============ RESUME ENTRY FUNCTIONS ============
function showResumeEntryOptions() {
    document.getElementById('uploadResumeForm').classList.add('hidden');
}

function showResumeUploadForm() {
    document.getElementById('uploadResumeForm').classList.remove('hidden');
}

async function handleResumeUpload() {
    const fileInput = document.getElementById('resumeFile');
    if (!fileInput.files[0]) {
        showBanner('Please upload your resume file.', 'error', 'notifyBanner');
        return;
    }
    
    // Mocking success due to backend removal
    showBanner('Analyzing resume... Please wait.', 'info', 'notifyBanner');
    setTimeout(() => {
        appState.resume = {
            fileName: fileInput.files[0].name,
            uploadedMode: true,
            fullName: appState.fullName,
            technicalSkills: "Web Development, Database Management", // Mock parsed skills
            resumeUrl: URL.createObjectURL(fileInput.files[0])
        };
        showBanner('Resume uploaded successfully!', 'success', 'notifyBanner');
        setTimeout(() => generateResumeDisplay(), 1000);
    }, 1500);
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

    // Validate Name (Alphabets and spaces only)
    const nameInput = form.querySelector('[name="fullName"]');
    if (!/^[A-Za-z\s]+$/.test(nameInput.value.trim())) {
        showError(nameInput, 'Only alphabets are allowed.');
        isValid = false;
    }

    // Validate Contact (Exactly 10 digits)
    const contactInput = form.querySelector('[name="contactNumber"]');
    if (!/^\d{10}$/.test(contactInput.value.trim())) {
        showError(contactInput, 'Must be exactly 10 numeric digits.');
        isValid = false;
    }

    // Validate URLs
    const urlFields = ['linkedin', 'github', 'portfolio'];
    urlFields.forEach(field => {
        const input = form.querySelector(`[name="${field}"]`);
        if (input.value && !/^https?:\/\/.+/.test(input.value.trim())) {
            showError(input, 'Please enter a valid URL starting with http:// or https://');
            isValid = false;
        }
    });

    // Validate Word Counts (Min 20 words)
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
    
    // STRICT RETURN: Execution completely stops here if validation fails
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

    if (resume.uploadedMode && resume.resumeUrl && resume.fileName.toLowerCase().endsWith('.pdf')) {
        container.innerHTML = `
            <div class="flex flex-col items-center">
                <h2 class="text-2xl font-bold text-slate-900 mb-6">Your Uploaded Resume</h2>
                <iframe src="${resume.resumeUrl}" class="w-full h-[800px] border border-slate-200 rounded-lg"></iframe>
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
                <div class="grid grid-cols-2 gap-4">
                    <div><p class="font-semibold text-slate-900 text-sm mb-1">Technical</p><p class="text-slate-700 text-sm">${resume.technicalSkills || ''}</p></div>
                    <div><p class="font-semibold text-slate-900 text-sm mb-1">Professional</p><p class="text-slate-700 text-sm">${resume.softSkills || ''}</p></div>
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
}

// ============ JOB MATCHING & DASHBOARD FUNCTIONS ============
function generateJobsFromSkills() {
    const skillsString = appState.resume?.technicalSkills || "";
    // Grab key comma-separated skills
    const skills = skillsString.split(',').map(s => s.trim()).filter(s => s.length > 0).slice(0, 4); // limit categories
    let generatedJobs = [];
    
    if (skills.length === 0) {
        return fallbackJobs;
    }

    let idCounter = 200;
    skills.forEach(skill => {
        generatedJobs.push({ id: idCounter++, title: `Junior ${skill} Engineer`, company: 'TechNova', location: 'Remote', salary: 'Competitive', source: 'Indeed', description: `Looking for talent in ${skill} to build great products.`, matchScore: 94, skillCat: skill });
        generatedJobs.push({ id: idCounter++, title: `Senior ${skill} Developer`, company: 'Apex Systems', location: 'Hybrid', salary: '$120K+', source: 'LinkedIn', description: `Lead the development team using ${skill}.`, matchScore: 89, skillCat: skill });
    });

    return generatedJobs;
}

function loadAndDisplayJobs() {
    switchTab('jobs');
    // Generate jobs based on user's current skills
    appState.jobs = generateJobsFromSkills();
    renderJobs();
    renderInterested();
}

function renderJobs() {
    const container = document.getElementById('jobsContent');
    
    // Group jobs by skill category
    const categories = [...new Set(appState.jobs.map(j => j.skillCat))];
    
    container.innerHTML = categories.map(cat => {
        const catJobs = appState.jobs.filter(j => j.skillCat === cat);
        return `
            <div class="mb-10">
                <h3 class="text-2xl font-bold text-slate-900 border-b-2 border-blue-200 pb-2 mb-6">Matched for: <span class="text-blue-600">${cat}</span></h3>
                <div class="grid md:grid-cols-2 gap-6">
                    ${catJobs.map(job => `
                        <div class="bg-white rounded-xl border border-slate-200 hover:shadow-lg hover:border-blue-300 transition overflow-hidden">
                            <div class="p-6">
                                <div class="flex items-start justify-between mb-4 gap-4">
                                    <div>
                                        <h3 class="text-lg font-bold text-slate-900">${job.title}</h3>
                                        <p class="text-slate-600 font-medium">${job.company}</p>
                                    </div>
                                    <div class="text-right">
                                        <div class="text-2xl font-bold text-emerald-600">${job.matchScore || 80}%</div>
                                        <p class="text-xs text-slate-500">Match</p>
                                    </div>
                                </div>
                                <p class="text-sm text-slate-600 mb-4">${job.description || ''}</p>
                                <div class="flex gap-2 mt-4">
                                    <button onclick="applyJob(${job.id})" class="flex-1 text-center px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700 cursor-pointer">Apply Now</button>
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
        tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-slate-600">No applications yet. Browse Skill-Based Jobs and apply!</td></tr>';
        return;
    }
    tbody.innerHTML = appState.interested.map((job) => `
        <tr class="border-b border-slate-200 hover:bg-slate-50">
            <td class="px-6 py-4 font-semibold text-slate-900">${job.title}</td>
            <td class="px-6 py-4 text-slate-600">${job.company}</td>
            <td class="px-6 py-4">${renderStatusChip(job.status)}</td>
            <td class="px-6 py-4 text-right">
                ${job.status === 'Selected'
                    ? '<span class="text-emerald-700 font-semibold text-sm">Notified ✓</span>'
                    : `<button onclick="markSelected(${job.id})" class="text-emerald-600 hover:underline font-semibold text-sm cursor-pointer">Mark Selected</button>`}
            </td>
        </tr>
    `).join('');
}

function renderStatusChip(status) {
    if (status === 'Selected') return '<span class="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-full">Selected ✓</span>';
    return '<span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">Applied</span>';
}

function applyJob(jobId) {
    const job = appState.jobs.find((j) => j.id === jobId);
    if (job && !appState.interested.find((j) => j.id === jobId)) {
        appState.interested.unshift({ ...job, status: 'Applied' });
        
        // Auto-generate a new job recommendation in that category to simulate endless discovery
        const newScore = Math.max(70, job.matchScore - Math.floor(Math.random() * 5));
        appState.jobs.push({
            id: Date.now(),
            title: `Associated ${job.skillCat} Role`,
            company: 'NextGen Tech',
            location: 'Remote',
            description: `A new role was found based on your application to ${job.company}.`,
            matchScore: newScore,
            skillCat: job.skillCat
        });
        
        renderInterested();
        renderJobs(); // refresh list with new recommendation
        switchTab('interested');
        showBanner(`Application tracked for ${job.title}! A new recommendation has been added.`, 'success', 'notifyBannerDash');
    }
}

async function markSelected(jobId) {
    const selectedJob = appState.interested.find((j) => j.id === jobId);
    if (!selectedJob) return;

    selectedJob.status = 'Selected';
    renderInterested();

    // Trigger mock email
    showBanner('Congrats! Selection marked and email notification simulated.', 'success', 'notifyBannerDash');
}

function switchTab(tab) {
    ['jobs', 'interested'].forEach((name) => {
        document.getElementById(`${name}Tab`).classList.toggle('border-blue-600', tab === name);
        document.getElementById(`${name}Tab`).classList.toggle('text-blue-600', tab === name);
        document.getElementById(`${name}Tab`).classList.toggle('border-transparent', tab !== name);
        document.getElementById(`${name}Tab`).classList.toggle('text-slate-600', tab !== name);
    });
    document.getElementById('jobsContent').classList.toggle('hidden', tab !== 'jobs');
    document.getElementById('interestedContent').classList.toggle('hidden', tab !== 'interested');
}

function showBanner(message, type, bannerId) {
    const banner = document.getElementById(bannerId);
    const styles = {
        success: 'bg-emerald-50 border-emerald-200 text-emerald-800',
        warning: 'bg-amber-50 border-amber-200 text-amber-800',
        error: 'bg-red-50 border-red-200 text-red-800',
        info: 'bg-blue-50 border-blue-200 text-blue-800'
    };
    banner.className = `mb-6 px-4 py-3 rounded-lg border text-sm font-medium ${styles[type] || styles.info}`;
    banner.textContent = message;
    banner.classList.remove('hidden');
    setTimeout(() => { banner.classList.add('hidden'); }, 4000); // auto dismiss
}

function logout() {
    appState.fullName = '';
    appState.registeredEmail = '';
    appState.resume = null;
    appState.jobs = [];
    appState.interested = [];
    
    // Hide all internal pages
    document.getElementById('resumeEntryPage').classList.add('hidden');
    document.getElementById('resumeBuilderPage').classList.add('hidden');
    document.getElementById('resumeDisplayPage').classList.add('hidden');
    document.getElementById('dashboardPage').classList.add('hidden');
    
    // Show landing
    document.getElementById('landingPage').classList.remove('hidden');
    
    // Reset forms
    document.getElementById('authForm').reset();
    document.getElementById('resumeBuilderForm').reset();
}

// Event listeners
document.getElementById('authForm').addEventListener('submit', handleAuthSubmit);
document.getElementById('authToggleBtn').addEventListener('click', function() {
    toggleAuthMode(isSignupMode ? 'login' : 'signup');
});
document.getElementById('resumeBuilderForm').addEventListener('submit', handleResumeBuilderSubmit);