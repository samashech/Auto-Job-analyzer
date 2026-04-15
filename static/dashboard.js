// Dashboard state
const dashboardState = {
    userId: null,
    userName: '',
    userEmail: '',
    currentSection: 'home',
    currentRole: null,
    allJobs: [],
    roleKeywords: [],
    savedJobs: [],
    applications: [],
    trackedJobIds: new Set()
};

// Section titles mapping
const sectionTitles = {
    'home': 'Job Listings',
    'saved-jobs': 'Saved Job Roles',
    'applications': 'Application Selection',
    'skillup': 'Skill Up',
    'profile': 'Your Profile'
};

// On page load
document.addEventListener('DOMContentLoaded', async () => {
    await initDashboard();
});

async function initDashboard() {
    // Get user from session storage
    const storedUser = sessionStorage.getItem('raiot_user');
    if (!storedUser) {
        // Not logged in - redirect to home
        window.location.href = '/';
        return;
    }

    try {
        const user = JSON.parse(storedUser);
        dashboardState.userId = user.id;
        dashboardState.userName = user.name;
        dashboardState.userEmail = user.email;

        // Set welcome text
        document.getElementById('welcomeText').textContent = `Welcome, ${user.name}`;

        // Load all data
        await Promise.all([
            loadAllJobs(),
            loadSavedJobs(),
            loadApplications(),
            loadProfileData()
        ]);

    } catch (e) {
        console.error('Failed to initialize dashboard:', e);
        window.location.href = '/';
    }
}

// ============ SECTION SWITCHING ============
function switchSection(sectionName) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.section === sectionName);
    });

    // Update section content
    document.querySelectorAll('.section-content').forEach(section => {
        section.classList.remove('active');
    });
    const targetSection = document.getElementById(`section-${sectionName}`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Update title
    document.getElementById('sectionTitle').textContent = sectionTitles[sectionName] || 'Dashboard';

    dashboardState.currentSection = sectionName;

    // Load section-specific data
    if (sectionName === 'saved-jobs') {
        loadSavedJobs();
    } else if (sectionName === 'applications') {
        loadApplications();
    } else if (sectionName === 'skillup') {
        loadSkillUp();
    } else if (sectionName === 'profile') {
        loadProfileData();
    }
}

// ============ HOME / JOB LISTINGS ============
async function loadAllJobs() {
    const loadingEl = document.getElementById('jobListingsLoading');
    const errorEl = document.getElementById('jobListingsError');
    const emptyEl = document.getElementById('jobListingsEmpty');
    const containerEl = document.getElementById('jobCardsContainer');
    const tabsEl = document.getElementById('roleTabs');

    loadingEl.classList.remove('hidden');
    errorEl.classList.add('hidden');
    emptyEl.classList.add('hidden');
    containerEl.innerHTML = '';

    try {
        const response = await fetch(`/api/all-jobs/${dashboardState.userId}`);
        const data = await response.json();

        loadingEl.classList.add('hidden');

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load jobs');
        }

        dashboardState.allJobs = data.jobs || [];
        dashboardState.roleKeywords = data.roles || [];

        if (dashboardState.allJobs.length === 0) {
            emptyEl.classList.remove('hidden');
            return;
        }

        // Build role tabs
        renderRoleTabs();

        // Show jobs for first role by default
        if (dashboardState.roleKeywords.length > 0) {
            dashboardState.currentRole = dashboardState.roleKeywords[0];
            renderJobCards(dashboardState.allJobs);
        } else {
            // No role keywords - show all jobs
            renderJobCards(dashboardState.allJobs);
        }

    } catch (e) {
        console.error('Error loading jobs:', e);
        loadingEl.classList.add('hidden');
        errorEl.classList.remove('hidden');
    }
}

function renderRoleTabs() {
    const tabsEl = document.getElementById('roleTabs');
    if (!tabsEl) return;

    tabsEl.innerHTML = dashboardState.roleKeywords.map(role => `
        <button class="role-tab ${role === dashboardState.currentRole ? 'active' : ''}"
                onclick="selectRole('${role.replace(/'/g, "\\'")}')">
            ${role}
        </button>
    `).join('');
}

function selectRole(role) {
    dashboardState.currentRole = role;

    // Update active tab
    document.querySelectorAll('.role-tab').forEach(tab => {
        tab.classList.toggle('active', tab.textContent.trim() === role);
    });

    // Filter and render jobs
    const filteredJobs = dashboardState.allJobs.filter(job =>
        job.title.toLowerCase().includes(role.toLowerCase())
    );

    renderJobCards(filteredJobs.length > 0 ? filteredJobs : dashboardState.allJobs);
}

function renderJobCards(jobs) {
    const containerEl = document.getElementById('jobCardsContainer');
    const emptyEl = document.getElementById('jobListingsEmpty');

    if (jobs.length === 0) {
        containerEl.innerHTML = '';
        emptyEl.classList.remove('hidden');
        return;
    }

    emptyEl.classList.add('hidden');

    containerEl.innerHTML = jobs.map(job => createJobCardHTML(job)).join('');
}

function createJobCardHTML(job, showTrack = true) {
    const scoreClass = job.relevance_score >= 50 ? 'score-high' :
                       job.relevance_score >= 25 ? 'score-medium' : 'score-low';

    return `
        <div class="job-card" data-job-id="${job.id}">
            <div class="job-card-header">
                <div class="job-card-title">${escapeHtml(job.title)}</div>
                <button class="job-card-save ${job.saved ? 'saved' : ''}"
                        onclick="toggleSaveJob(${job.id})"
                        title="${job.saved ? 'Unsave' : 'Save'}">
                    ${job.saved ? '★' : '☆'}
                </button>
            </div>
            <div class="job-card-company">${escapeHtml(job.company || 'Company')}</div>
            <span class="job-card-source">${escapeHtml(job.source || 'Unknown')}</span>
            <div class="job-card-score">
                Match: <span class="score-value ${scoreClass}">${job.relevance_score}%</span>
            </div>
            <div class="job-card-actions">
                <a href="${escapeHtml(job.url)}" target="_blank" class="btn-apply" style="text-align:center;text-decoration:none;">Apply Now</a>
                ${showTrack ? `<button class="btn-track" onclick="trackApplication(${job.id})">Track</button>` : ''}
            </div>
        </div>
    `;
}

// ============ SAVE/UNSAVE JOBS ============
async function toggleSaveJob(jobId) {
    try {
        const response = await fetch('/api/toggle-save-job', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_id: jobId, user_id: dashboardState.userId })
        });

        const data = await response.json();
        if (data.saved !== undefined) {
            // Update local state
            const job = dashboardState.allJobs.find(j => j.id === jobId);
            if (job) job.saved = data.saved;

            // Re-render if on home section
            if (dashboardState.currentSection === 'home') {
                if (dashboardState.currentRole) {
                    selectRole(dashboardState.currentRole);
                } else {
                    renderJobCards(dashboardState.allJobs);
                }
            }

            // Re-render saved jobs if on that section
            if (dashboardState.currentSection === 'saved-jobs') {
                loadSavedJobs();
            }
        }
    } catch (e) {
        console.error('Error toggling save:', e);
    }
}

// ============ SAVED JOBS ============
async function loadSavedJobs() {
    const loadingEl = document.getElementById('savedJobsLoading');
    const emptyEl = document.getElementById('savedJobsEmpty');
    const gridEl = document.getElementById('savedJobsGrid');

    loadingEl.classList.remove('hidden');
    emptyEl.classList.add('hidden');
    gridEl.innerHTML = '';

    try {
        const response = await fetch(`/api/saved-jobs/${dashboardState.userId}`);
        const data = await response.json();

        loadingEl.classList.add('hidden');

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load saved jobs');
        }

        dashboardState.savedJobs = data.jobs || [];

        if (dashboardState.savedJobs.length === 0) {
            emptyEl.classList.remove('hidden');
            return;
        }

        gridEl.innerHTML = dashboardState.savedJobs.map(job => createJobCardHTML(job, false)).join('');

    } catch (e) {
        console.error('Error loading saved jobs:', e);
        loadingEl.classList.add('hidden');
        emptyEl.classList.remove('hidden');
    }
}

// ============ APPLICATIONS ============
async function loadApplications() {
    try {
        const response = await fetch(`/api/applications/${dashboardState.userId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load applications');
        }

        dashboardState.applications = data.applications || [];
        dashboardState.trackedJobIds = new Set(dashboardState.applications.map(a => a.job_id));

        renderApplications();

    } catch (e) {
        console.error('Error loading applications:', e);
    }
}

function renderApplications() {
    const emptyEl = document.getElementById('applicationsEmpty');
    const appliedEl = document.getElementById('appliedApps');
    const interviewEl = document.getElementById('interviewApps');
    const rejectedEl = document.getElementById('rejectedApps');
    const selectedEl = document.getElementById('selectedApps');

    if (dashboardState.applications.length === 0) {
        emptyEl.classList.remove('hidden');
        appliedEl.innerHTML = '';
        interviewEl.innerHTML = '';
        rejectedEl.innerHTML = '';
        selectedEl.innerHTML = '';
        return;
    }

    emptyEl.classList.add('hidden');

    // Group by status
    const byStatus = { Applied: [], Interview: [], Rejected: [], Selected: [] };
    dashboardState.applications.forEach(app => {
        if (byStatus[app.status]) {
            byStatus[app.status].push(app);
        } else {
            byStatus['Applied'].push(app);
        }
    });

    appliedEl.innerHTML = byStatus['Applied'].map(app => createApplicationItemHTML(app)).join('');
    interviewEl.innerHTML = byStatus['Interview'].map(app => createApplicationItemHTML(app)).join('');
    rejectedEl.innerHTML = byStatus['Rejected'].map(app => createApplicationItemHTML(app)).join('');
    selectedEl.innerHTML = byStatus['Selected'].map(app => createApplicationItemHTML(app)).join('');
}

function createApplicationItemHTML(app) {
    return `
        <div class="application-item">
            <div class="application-item-title">${escapeHtml(app.title)}</div>
            <div class="application-item-company">${escapeHtml(app.company || '')}</div>
            <div class="application-item-actions">
                <select onchange="updateApplicationStatus(${app.id}, this.value)">
                    <option value="Applied" ${app.status === 'Applied' ? 'selected' : ''}>Applied</option>
                    <option value="Interview" ${app.status === 'Interview' ? 'selected' : ''}>Interview</option>
                    <option value="Rejected" ${app.status === 'Rejected' ? 'selected' : ''}>Rejected</option>
                    <option value="Selected" ${app.status === 'Selected' ? 'selected' : ''}>Selected</option>
                </select>
                <a href="${escapeHtml(app.url)}" target="_blank">View</a>
            </div>
        </div>
    `;
}

async function trackApplication(jobId) {
    // Check if already tracked
    if (dashboardState.trackedJobIds.has(jobId)) {
        // Navigate to applications section
        switchSection('applications');
        return;
    }

    try {
        const response = await fetch('/api/application', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: dashboardState.userId,
                job_id: jobId,
                status: 'Applied'
            })
        });

        const data = await response.json();
        if (data.success) {
            dashboardState.trackedJobIds.add(jobId);
            // Navigate to applications
            switchSection('applications');
            loadApplications();
        }
    } catch (e) {
        console.error('Error tracking application:', e);
    }
}

async function updateApplicationStatus(appId, newStatus) {
    try {
        const response = await fetch('/api/update-application-status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                application_id: appId,
                status: newStatus
            })
        });

        const data = await response.json();
        if (data.success) {
            // Reload applications
            loadApplications();
        }
    } catch (e) {
        console.error('Error updating application status:', e);
    }
}

// ============ SKILL UP ============
async function loadSkillUp() {
    const loadingEl = document.getElementById('skillupLoading');
    const emptyEl = document.getElementById('skillupEmpty');
    const gridEl = document.getElementById('skillupGrid');

    loadingEl.classList.remove('hidden');
    emptyEl.classList.add('hidden');
    gridEl.innerHTML = '';

    try {
        const response = await fetch(`/api/skillup/${dashboardState.userId}`);
        const data = await response.json();

        loadingEl.classList.add('hidden');

        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze skills');
        }

        const missingSkills = data.missing_skills || [];

        if (missingSkills.length === 0) {
            emptyEl.classList.remove('hidden');
            return;
        }

        gridEl.innerHTML = missingSkills.map(item => `
            <div class="skillup-card">
                <h3>${escapeHtml(item.skill)}</h3>
                <p>${escapeHtml(item.resource_name)}</p>
                <a href="${escapeHtml(item.resource_url)}" target="_blank">Start Learning →</a>
            </div>
        `).join('');

    } catch (e) {
        console.error('Error loading skill up:', e);
        loadingEl.classList.add('hidden');
        gridEl.innerHTML = '<p class="error-state">Failed to analyze skills. Please try again later.</p>';
    }
}

// ============ PROFILE ============
async function loadProfileData() {
    const storedUser = sessionStorage.getItem('raiot_user');
    if (!storedUser) return;

    try {
        const user = JSON.parse(storedUser);

        document.getElementById('profileName').value = user.name || '';
        document.getElementById('profileEmail').value = user.email || '';
        document.getElementById('profileJobType').value = user.job_type || 'Internship';
        document.getElementById('profileLocation').value = user.location || '';
        document.getElementById('profileSkills').value = user.skills || '';

        // Set preferred job roles from job_role field or derive from skills
        if (user.job_role) {
            document.getElementById('profileJobRoles').value = user.job_role;
        }
    } catch (e) {
        console.error('Error loading profile data:', e);
    }
}

async function saveProfilePreferences() {
    const statusEl = document.getElementById('profileSaveStatus');
    statusEl.classList.remove('hidden', 'success', 'error');

    const data = {
        user_id: dashboardState.userId,
        name: document.getElementById('profileName').value,
        email: document.getElementById('profileEmail').value,
        job_role: document.getElementById('profileJobRoles').value,
        job_type: document.getElementById('profileJobType').value,
        location: document.getElementById('profileLocation').value,
        skills: document.getElementById('profileSkills').value
    };

    try {
        const response = await fetch('/api/update-profile-preferences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            statusEl.textContent = 'Profile updated successfully!';
            statusEl.classList.add('success');

            // Update session storage
            const storedUser = JSON.parse(sessionStorage.getItem('raiot_user') || '{}');
            Object.assign(storedUser, {
                name: data.name,
                email: data.email,
                job_role: data.job_role,
                job_type: data.job_type,
                location: data.location,
                skills: data.skills,
                profile_complete: true
            });
            sessionStorage.setItem('raiot_user', JSON.stringify(storedUser));

            // Update dashboard state
            dashboardState.userName = data.name;
            document.getElementById('welcomeText').textContent = `Welcome, ${data.name}`;
        } else {
            statusEl.textContent = result.error || 'Failed to update profile';
            statusEl.classList.add('error');
        }
    } catch (e) {
        console.error('Error saving profile:', e);
        statusEl.textContent = 'Network error. Please try again.';
        statusEl.classList.add('error');
    }

    // Hide status after 3 seconds
    setTimeout(() => {
        statusEl.classList.add('hidden');
    }, 3000);
}

// ============ LOGOUT ============
async function handleLogout() {
    try {
        await fetch('/auth/logout', { method: 'POST' });
    } catch (e) {
        console.error('Logout error:', e);
    }

    sessionStorage.clear();
    window.location.href = '/';
}

// ============ HELPERS ============
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
