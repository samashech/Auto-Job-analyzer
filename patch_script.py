import re

with open("templates/index.html", "r") as f:
    content = f.read()

# Define the new script content
new_script = """<script>
        const INTEGRATION_CONFIG = {
            TELEGRAM_BOT_TOKEN: '',
            JOB_SCRAPE_API: '',
            EMAIL_NOTIFY_API: ''
        };

        let isSignupMode = false;
        const appState = {
            fullName: '',
            registeredEmail: '',
            telegramId: '',
            jobTitle: '',
            location: '',
            resume: null,
            resumePhoto: null,
            jobs: [],
            interested: [],
            shareToken: Math.random().toString(36).substr(2, 9)
        };

        const fallbackJobs = [
            { id: 101, title: 'Python Backend Engineer', company: 'ScaleGrid', location: 'Remote', salary: '$140K - $170K', source: 'Indeed', description: 'Build scalable APIs and data pipelines.', matchScore: 91, url: '#' }
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
        }

        function closeAuthModal() {
            document.getElementById('authModal').classList.add('hidden');
        }

        async function handleAuthSubmit(e) {
            e.preventDefault();
            const name = document.getElementById('authName').value.trim();
            const email = document.getElementById('authEmail').value.trim();
            
            // Mock authentication since backend routes were removed
            appState.fullName = name || 'Professional';
            appState.registeredEmail = email;

            closeAuthModal();
            document.getElementById('landingPage').classList.add('hidden');
            document.getElementById('resumeEntryPage').classList.remove('hidden');
            showResumeEntryOptions();

            if (isSignupMode) {
                showBannerResume('Professional account created! Now let\\'s build your profile.', 'success', 'notifyBanner');
            } else {
                showBannerResume(`Welcome back, ${appState.fullName}!`, 'success', 'notifyBanner');
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
            const photoInput = document.getElementById('uploadedPhoto');
            const telegramInput = document.getElementById('uploadedTelegramId');
            const file = fileInput.files[0];

            if (!file) {
                showBannerResume('Please upload your resume file.', 'warning', 'notifyBanner');
                return;
            }

            appState.telegramId = telegramInput.value.trim();
            
            if (photoInput.files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => { appState.resumePhoto = e.target.result; };
                reader.readAsDataURL(photoInput.files[0]);
            }

            const formData = new FormData();
            // Original app.py expects 'resume' instead of 'resume_file'
            formData.append('resume', file);

            try {
                showBannerResume('Analyzing resume... Please wait.', 'info', 'notifyBanner');
                
                // Fetching from the original /upload endpoint
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                if (!response.ok) throw new Error(data.error || 'Upload failed');

                appState.resume = {
                    fileName: file.name,
                    uploadedMode: true,
                    jobTitle: data.level,
                    technicalSkills: data.skills ? data.skills.join(', ') : '',
                    chartUrl: data.chart_url
                };

                // Map jobs immediately since they come directly from /upload
                if (data.jobs && data.jobs.length > 0) {
                    appState.jobs = data.jobs.map((job, index) => ({
                        id: index + 1,
                        title: `${data.level} Role - ${job.name}`,
                        company: "Various Companies",
                        source: job.name,
                        matchScore: 90,
                        description: `A great match for your skills: ${data.skills.slice(0,3).join(', ')}`,
                        url: job.url
                    }));
                } else {
                    appState.jobs = fallbackJobs;
                }
                
                showBannerResume('Resume uploaded and analyzed successfully!', 'success', 'notifyBanner');
                setTimeout(() => generateResumeDisplay(), 1000);
            } catch (error) {
                showBannerResume(error.message, 'error', 'notifyBanner');
            }
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

        // ============ RESUME BUILDER FUNCTIONS ============
        async function handleResumeBuilderSubmit(e) {
            e.preventDefault();
            const form = new FormData(e.target);
            const profile = Object.fromEntries(form.entries());

            appState.fullName = profile.fullName;
            appState.registeredEmail = profile.professionalEmail;
            appState.jobTitle = profile.jobTitle;
            appState.location = profile.location;
            appState.telegramId = (profile.telegram || '').trim();
            appState.resume = profile;

            if (document.getElementById('builderPhoto').files[0]) {
                const reader = new FileReader();
                reader.onload = (e) => { 
                    appState.resumePhoto = e.target.result;
                    generateResumeDisplay();
                };
                reader.readAsDataURL(document.getElementById('builderPhoto').files[0]);
            } else {
                generateResumeDisplay();
            }
        }

        function generateResumeDisplay() {
            document.getElementById('resumeBuilderPage').classList.add('hidden');
            document.getElementById('resumeDisplayPage').classList.remove('hidden');
            renderProfessionalResume();
        }

        function renderProfessionalResume() {
            const resume = appState.resume;
            const container = document.getElementById('resumeContainer');

            let html = `
                <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <!-- Photo & Contact -->
                    <div class="md:col-span-1 flex flex-col items-center">
                        ${appState.resumePhoto ? `<img src="${appState.resumePhoto}" alt="Profile" class="w-32 h-32 rounded-full object-cover border-4 border-blue-600 mb-4">` : `<div class="w-32 h-32 rounded-full bg-slate-200 flex items-center justify-center mb-4 text-slate-400 text-4xl">👤</div>`}
                        <h1 class="text-2xl font-bold text-slate-900 text-center">${resume.fullName || 'Your Name'}</h1>
                        <p class="text-blue-600 font-semibold text-center">${resume.jobTitle || 'Professional Title'}</p>
                        <div class="mt-6 pt-6 border-t border-slate-200 w-full text-sm space-y-3 text-slate-700">
                            <div class="break-words"><strong>Email:</strong> ${resume.professionalEmail || ''}</div>
                            <div><strong>Phone:</strong> ${resume.contactNumber || ''}</div>
                            <div><strong>Location:</strong> ${resume.location || ''}</div>
                            ${resume.linkedin ? `<div><a href="${resume.linkedin}" class="text-blue-600 hover:underline">LinkedIn</a></div>` : ''}
                            ${resume.github ? `<div><a href="${resume.github}" class="text-blue-600 hover:underline">GitHub</a></div>` : ''}
                            ${resume.portfolio ? `<div><a href="${resume.portfolio}" class="text-blue-600 hover:underline">Portfolio</a></div>` : ''}
                        </div>
                    </div>

                    <!-- Main Content -->
                    <div class="md:col-span-3 space-y-6">
                        <!-- About -->
                        ${resume.about ? `
                        <div>
                            <h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">PROFESSIONAL SUMMARY</h2>
                            <p class="text-slate-700 text-sm leading-relaxed">${resume.about}</p>
                        </div>
                        ` : ''}

                        <!-- Skills -->
                        <div>
                            <h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">SKILLS</h2>
                            ${resume.chartUrl ? `<div class="mb-4"><img src="${resume.chartUrl}" alt="Skills Chart" class="w-full max-w-md mx-auto rounded-lg border border-slate-200"></div>` : ''}
                            <div class="grid grid-cols-2 gap-4">
                                ${resume.technicalSkills ? `
                                <div>
                                    <p class="font-semibold text-slate-900 text-sm mb-1">Technical</p>
                                    <p class="text-slate-700 text-sm">${resume.technicalSkills}</p>
                                </div>
                                ` : ''}
                                ${resume.softSkills ? `
                                <div>
                                    <p class="font-semibold text-slate-900 text-sm mb-1">Professional</p>
                                    <p class="text-slate-700 text-sm">${resume.softSkills}</p>
                                </div>
                                ` : ''}
                            </div>
                        </div>

                        <!-- Experience -->
                        ${resume.experienceAchievements ? `
                        <div>
                            <h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">EXPERIENCE & ACHIEVEMENTS</h2>
                            <p class="text-slate-700 text-sm whitespace-pre-wrap">${resume.experienceAchievements}</p>
                        </div>
                        ` : ''}

                        <!-- Education -->
                        ${resume.education ? `
                        <div>
                            <h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">EDUCATION</h2>
                            <p class="text-slate-700 text-sm">${resume.education}</p>
                        </div>
                        ` : ''}

                        <!-- Projects -->
                        ${resume.projects ? `
                        <div>
                            <h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">KEY PROJECTS</h2>
                            <p class="text-slate-700 text-sm whitespace-pre-wrap">${resume.projects}</p>
                        </div>
                        ` : ''}

                        <!-- Certifications -->
                        ${resume.certifications ? `
                        <div>
                            <h2 class="text-lg font-bold text-slate-900 border-b-2 border-blue-600 pb-2 mb-3">CERTIFICATIONS</h2>
                            <p class="text-slate-700 text-sm">${resume.certifications}</p>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;

            container.innerHTML = html;
        }

        function downloadResumePDF() {
            const element = document.getElementById('resumeContainer');
            const opt = {
                margin: 10,
                filename: `${appState.fullName || 'Resume'}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2 },
                jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' }
            };
            html2pdf().set(opt).from(element).save();
            showBannerResume('Resume downloaded as PDF!', 'success', 'notifyBannerResume');
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
            showBannerResume('Share link copied to clipboard!', 'success', 'notifyBannerResume');
        }

        function emailResume() {
            const email = document.getElementById('shareEmail').value;
            if (!email) {
                showBannerResume('Please enter an email address', 'warning', 'notifyBannerResume');
                return;
            }
            showBannerResume(`Resume share link sent to ${email}!`, 'success', 'notifyBannerResume');
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

        // ============ JOB MATCHING FUNCTIONS ============
        function loadAndDisplayJobs() {
            appState.interested = [];
            switchTab('jobs');
            
            // Jobs are already populated in appState.jobs from /upload endpoint
            if (appState.jobs.length === 0) {
                appState.jobs = fallbackJobs;
            }
            
            renderJobs();
            renderInterested();
        }

        function renderJobs() {
            const container = document.getElementById('jobsContent');
            container.innerHTML = appState.jobs.map((job) => `
                <div class="bg-white rounded-xl border border-slate-200 hover:shadow-lg hover:border-blue-300 transition overflow-hidden">
                    <div class="p-6">
                        <div class="flex items-start justify-between mb-4 gap-4">
                            <div>
                                <h3 class="text-lg font-bold text-slate-900">${job.title}</h3>
                                <p class="text-slate-600 font-medium">${job.company}</p>
                                <p class="text-xs text-slate-500 mt-1">Source: ${job.source || 'Integrated Feed'}</p>
                            </div>
                            <div class="text-right">
                                <div class="text-2xl font-bold text-emerald-600">${job.matchScore || 80}%</div>
                                <p class="text-xs text-slate-500">Match</p>
                            </div>
                        </div>
                        <p class="text-sm text-slate-600 mb-4">${job.description || ''}</p>
                        <div class="flex items-center justify-between text-sm text-slate-600 mb-6 pb-4 border-b border-slate-200">
                            <span>${job.location || 'Remote'}</span>
                            <span>${job.salary || 'Compensation TBD'}</span>
                        </div>
                        <div class="flex gap-2">
                            <a href="${job.url || '#'}" target="_blank" onclick="applyJob(${job.id})" class="flex-1 text-center px-4 py-2 rounded-lg bg-blue-600 text-white font-semibold hover:bg-blue-700">Apply Now</a>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function renderInterested() {
            const tbody = document.getElementById('interestedTable');
            if (!appState.interested.length) {
                tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-slate-600">No applications yet. Apply to jobs above!</td></tr>';
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
                            : `<button onclick="markSelected(${job.id})" class="text-blue-600 hover:underline font-semibold text-sm">Mark Selected</button>`}
                    </td>
                </tr>
            `).join('');
        }

        function renderStatusChip(status) {
            if (status === 'Selected') return '<span class="px-3 py-1 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-full">Selected ✓</span>';
            return '<span class="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full">Applied</span>';
        }

        async function applyJob(jobId) {
            const job = appState.jobs.find((j) => j.id === jobId);
            if (job && !appState.interested.find((j) => j.id === jobId)) {
                // Tracking is handled locally since backend endpoint is removed
                appState.interested.unshift({ ...job, status: 'Applied' });
                renderInterested();
                switchTab('interested');
                showBannerResume(`Application tracked for ${job.title} at ${job.company}!`, 'success', 'notifyBannerDash');
            }
        }

        async function markSelected(jobId) {
            const selectedJob = appState.interested.find((j) => j.id === jobId);
            if (!selectedJob) return;

            selectedJob.status = 'Selected';
            renderInterested();

            const results = await notifySelection(selectedJob);
            if (results.telegram && results.email) {
                showBannerResume('Congrats! Selection notification sent via Telegram & email.', 'success', 'notifyBannerDash');
            } else {
                showBannerResume('Selection marked. Configure Telegram & email for notifications.', 'warning', 'notifyBannerDash');
            }
        }

        async function notifySelection(job) {
            const payload = {
                event: 'job_application_selected',
                fullName: appState.fullName,
                email: appState.registeredEmail,
                telegramId: appState.telegramId,
                job
            };

            const telegram = await sendTelegram(payload);
            const email = await sendEmail(payload);
            return { telegram, email };
        }

        async function sendTelegram(payload) {
            if (!payload.telegramId || !INTEGRATION_CONFIG.TELEGRAM_BOT_TOKEN) return false;
            const text = `🎉 Congratulations! ${payload.job.title} at ${payload.job.company} - Selected!\n\nLocation: ${payload.job.location}\nSalary: ${payload.job.salary}`;
            try {
                const res = await fetch(`https://api.telegram.org/bot${INTEGRATION_CONFIG.TELEGRAM_BOT_TOKEN}/sendMessage`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ chat_id: payload.telegramId, text })
                });
                return res.ok;
            } catch { return false; }
        }

        async function sendEmail(payload) {
            if (!payload.email || !INTEGRATION_CONFIG.EMAIL_NOTIFY_API) return false;
            try {
                const res = await fetch(INTEGRATION_CONFIG.EMAIL_NOTIFY_API, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                return res.ok;
            } catch { return false; }
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

        function showBannerResume(message, type, bannerId = 'notifyBanner') {
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
        }

        function logout() {
            document.getElementById('landingPage').classList.remove('hidden');
            document.getElementById('resumeEntryPage').classList.add('hidden');
            document.getElementById('resumeBuilderPage').classList.add('hidden');
            document.getElementById('resumeDisplayPage').classList.add('hidden');
            document.getElementById('dashboardPage').classList.add('hidden');
            appState.shareToken = Math.random().toString(36).substr(2, 9);
        }

        // Event listeners
        document.getElementById('authForm').addEventListener('submit', handleAuthSubmit);
        document.getElementById('authToggleBtn').addEventListener('click', function() {
            toggleAuthMode(isSignupMode ? 'login' : 'signup');
        });
        document.getElementById('resumeBuilderForm').addEventListener('submit', handleResumeBuilderSubmit);
    </script>"""

updated_content = re.sub(r'<script>.*?</script>', new_script, content, flags=re.DOTALL)

with open("templates/index.html", "w") as f:
    f.write(updated_content)

print("HTML patched successfully!")
