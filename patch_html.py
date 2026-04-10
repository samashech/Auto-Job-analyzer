import re

with open("templates/index.html", "r") as f:
    content = f.read()

# 1. Add Job Type dropdown to the resume upload form
old_form_inputs = """                    <div>
                        <label class="block text-sm font-semibold text-slate-900 mb-2">Resume File</label>
                        <input id="resumeFile" type="file" accept=".txt,.md,.pdf,.doc,.docx" class="w-full px-4 py-3 rounded-lg border border-slate-200">
                    </div>"""

new_form_inputs = """                    <div>
                        <label class="block text-sm font-semibold text-slate-900 mb-2">Resume File</label>
                        <input id="resumeFile" type="file" accept=".txt,.md,.pdf,.doc,.docx" class="w-full px-4 py-3 rounded-lg border border-slate-200">
                    </div>
                    <div>
                        <label class="block text-sm font-semibold text-slate-900 mb-2">Desired Job Type</label>
                        <select id="jobType" class="w-full px-4 py-3 rounded-lg border border-slate-200 bg-white">
                            <option value="Full-time">Full-Time Job</option>
                            <option value="Part-time">Part-Time Job</option>
                            <option value="Internship">Internship</option>
                            <option value="Freelance">Freelancing</option>
                        </select>
                    </div>"""

content = content.replace(old_form_inputs, new_form_inputs)

# 2. Add job_type to handleResumeUpload
old_handle_upload = """            const formData = new FormData();
            // Original app.py expects 'resume' instead of 'resume_file'
            formData.append('resume', file);"""

new_handle_upload = """            const jobType = document.getElementById('jobType').value;
            const formData = new FormData();
            formData.append('resume', file);
            formData.append('job_type', jobType);"""

content = content.replace(old_handle_upload, new_handle_upload)

# 3. Update the mapping to show dynamic scraped vs generated info correctly
old_job_map = """                    appState.jobs = data.jobs.map((job, index) => ({
                        id: index + 1,
                        title: `${data.level} Role - ${job.name}`,
                        company: "Various Companies",
                        source: job.name,
                        matchScore: 90,
                        description: `A great match for your skills: ${data.skills.slice(0,3).join(', ')}`,
                        url: job.url
                    }));"""

new_job_map = """                    appState.jobs = data.jobs.map((job, index) => ({
                        id: index + 1,
                        title: job.title || `${data.level} Role - ${job.name}`,
                        company: job.company || "Various Companies",
                        source: job.name || job.source,
                        matchScore: 90,
                        description: job.description || `A great match for your skills: ${data.skills.slice(0,3).join(', ')}`,
                        url: job.url
                    }));"""

content = content.replace(old_job_map, new_job_map)

# 4. Display Job Type in Resume Screen
old_resume_display = """                        <p class="text-blue-600 font-semibold text-center">${resume.jobTitle || 'Professional Title'}</p>"""

new_resume_display = """                        <p class="text-blue-600 font-semibold text-center">${resume.jobTitle || 'Professional Title'}</p>
                        <p class="text-slate-500 text-xs font-semibold text-center uppercase tracking-wider mt-1">Seeking: ${data.job_type || 'Full-time'}</p>"""

content = content.replace(old_resume_display, new_resume_display)

with open("templates/index.html", "w") as f:
    f.write(content)

print("HTML patched with Phase 4 features")
