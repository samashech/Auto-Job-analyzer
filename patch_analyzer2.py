import re

with open('/home/samash/Documents/Project RAIoT/analyzer.py', 'r') as f:
    content = f.read()

# Let's fix the multiple job role inference.
old_func = """def infer_job_role(skills):
    if not skills:
        return "Software Developer"
    
    role_scores = {role: 0 for role in ROLE_INFERENCE_MAP}
    skills_lower = [s.lower() for s in skills]
    
    for role, role_skills in ROLE_INFERENCE_MAP.items():
        for rs in role_skills:
            if rs.lower() in skills_lower:
                role_scores[role] += 1
                
    best_role = max(role_scores, key=role_scores.get)
    if role_scores[best_role] > 0:
        return best_role
    return "Software Developer\"""

new_func = """def infer_job_role(skills):
    if not skills:
        return "Software Developer"
    
    role_scores = {role: 0 for role in ROLE_INFERENCE_MAP}
    skills_lower = [s.lower() for s in skills]
    
    for role, role_skills in ROLE_INFERENCE_MAP.items():
        for rs in role_skills:
            if rs.lower() in skills_lower:
                role_scores[role] += 1
                
    # Sort roles by score descending
    sorted_roles = sorted(role_scores.items(), key=lambda item: item[1], reverse=True)
    
    # Get top 3 roles that have a score > 0
    top_roles = [role for role, score in sorted_roles if score > 0][:3]
    
    if top_roles:
        return ",".join(top_roles) # Return comma-separated list of roles
    return "Software Developer\"""

content = content.replace(old_func, new_func)

with open('/home/samash/Documents/Project RAIoT/analyzer.py', 'w') as f:
    f.write(content)
