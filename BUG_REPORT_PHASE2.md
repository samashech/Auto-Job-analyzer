# Phase 2: Bug Report & Missing Functionality

## Critical Issues Found

### Issue 1: CORS Credentials Mismatch
**Severity**: HIGH  
**File**: `frontend/src/components/providers/app-state-provider.tsx` (line 103)  
**Problem**: `credentials: "omit"` prevents session cookies from being sent  
**Impact**: User sessions won't persist between requests  

**Fix Required**:
```typescript
// Change from:
credentials: "omit"

// To:
credentials: "include"
```

**Note**: Flask backend already has `CORS(app, supports_credentials=True)` configured correctly.

---

### Issue 2: Incomplete Profile Data Mapping on Login
**Severity**: MEDIUM  
**File**: `frontend/src/components/providers/app-state-provider.tsx` (lines 136-140)  
**Problem**: Extended profile fields from backend are ignored  
**Impact**: User's about, projects, achievements, education, certificates, social links not loaded  

**Current Code**:
```typescript
setProfile({
  ...defaultProfile,
  fullName: data.user.name,
  email: data.user.email,
  skills: data.user.skills ? data.user.skills.split(", ") : defaultProfile.skills,
});
```

**Fix Required**:
```typescript
setProfile({
  fullName: data.user.name,
  email: data.user.email,
  phone: data.user.phone || "",
  about: data.user.about || "",
  skills: data.user.skills ? data.user.skills.split(", ") : [],
  projects: data.user.projects ? data.user.projects.split(", ") : [],
  achievements: data.user.achievements ? data.user.achievements.split(", ") : [],
  education: data.user.education ? data.user.education.split(", ") : [],
  positionsOfResponsibility: data.user.positions_of_responsibility 
    ? data.user.positions_of_responsibility.split(", ") 
    : [],
  certificates: data.user.certificates ? data.user.certificates.split(", ") : [],
  photoDataUrl: data.user.photo_data_url || "",
  social: {
    linkedIn: data.user.social_linkedin || "",
    github: data.user.social_github || "",
    portfolio: data.user.social_portfolio || "",
  },
});
```

---

### Issue 3: Jobs Missing Extended Fields
**Severity**: MEDIUM  
**File**: `frontend/src/components/providers/app-state-provider.tsx` (lines 65-77)  
**Problem**: Job data from backend not fully utilized  
**Impact**: Salary, location, skills, region not displayed in jobs  

**Current Code**:
```typescript
const formattedJobs: Job[] = data.jobs.map((j: any) => ({
  id: String(j.id),
  title: j.title,
  company: j.company || "Unknown",
  salary: "Not specified",  // ❌ Should use j.salary
  location: "Remote",        // ❌ Should use j.location
  source: j.source as any || "LinkedIn",
  sourceUrl: j.url,
  skills: [],                // ❌ Should use j.skills
  type: [j.job_type || "Full Time"],
  region: "India",           // ❌ Should use j.region
  stateOrContinent: "All",   // ❌ Should use j.stateOrContinent
}));
```

**Fix Required**:
```typescript
const formattedJobs: Job[] = data.jobs.map((j: any) => ({
  id: String(j.id),
  title: j.title,
  company: j.company || "Unknown",
  salary: j.salary || "Not specified",
  location: j.location || "Remote",
  source: j.source || "LinkedIn",
  sourceUrl: j.url,
  skills: j.skills || [],
  type: j.type || [j.job_type || "Full Time"],
  region: j.region || "India",
  stateOrContinent: j.stateOrContinent || "All",
}));
```

---

### Issue 4: Update Profile Doesn't Send Extended Fields
**Severity**: HIGH  
**File**: `frontend/src/components/providers/app-state-provider.tsx` (lines 170-181)  
**Problem**: Extended profile data not sent to backend  
**Impact**: Profile changes not saved to database  

**Current Code**:
```typescript
await fetch(`${API_URL}/api/update-profile-preferences`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    user_id: userId,
    name: profileData.fullName,
    email: profileData.email,
    skills: profileData.skills.join(", "),
  }),
});
```

**Fix Required**:
```typescript
await fetch(`${API_URL}/api/update-profile-preferences`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    user_id: userId,
    name: profileData.fullName,
    email: profileData.email,
    phone: profileData.phone,
    skills: profileData.skills.join(", "),
    about: profileData.about,
    projects: profileData.projects.join(", "),
    achievements: profileData.achievements.join(", "),
    education: profileData.education.join(", "),
    certificates: profileData.certificates.join(", "),
    positions_of_responsibility: profileData.positionsOfResponsibility.join(", "),
    photoDataUrl: profileData.photoDataUrl,
    social: {
      github: profileData.social.github,
      linkedIn: profileData.social.linkedIn,
      portfolio: profileData.social.portfolio,
    },
  }),
});
```

---

### Issue 5: Session Check Uses LocalStorage Instead of Real Session
**Severity**: MEDIUM  
**File**: `frontend/src/components/providers/app-state-provider.tsx` (lines 97-111)  
**Problem**: Session verification doesn't actually check backend session  
**Impact**: User state may be out of sync with backend  

**Current Code**:
```typescript
const checkSession = async () => {
  try {
    const res = await fetch(`${API_URL}/auth/check-session`, {
      credentials: "omit", // ❌ Wrong
    });
    const storedUserId = localStorage.getItem(STORAGE_KEYS.userId);
    if (storedUserId) {
      setCurrentUser({ fullName: "User", email: "user@example.com", password: "" });
      fetchJobs(storedUserId);
      fetchApplications(storedUserId);
    }
  } catch (e) {
    console.error(e);
  }
};
```

**Fix Required**:
```typescript
const checkSession = async () => {
  try {
    const res = await fetch(`${API_URL}/auth/check-session`, {
      credentials: "include", // ✅ Include credentials
    });
    const data = await res.json();
    if (data.logged_in && data.user) {
      setCurrentUser({
        fullName: data.user.name,
        email: data.user.email,
        password: "",
      });
      localStorage.setItem(STORAGE_KEYS.userId, String(data.user.id));
      fetchJobs(String(data.user.id));
      fetchApplications(String(data.user.id));
    }
  } catch (e) {
    console.error("Session check failed", e);
  }
};
```

---

### Issue 6: Password Not Included in AuthUser Type
**Severity**: LOW  
**File**: `frontend/src/lib/types.ts` (line 48)  
**Problem**: AuthUser includes password field but shouldn't after login  
**Impact**: Password stored in state (security risk)  

**Fix Required**: Change AuthUser to not require password after login, or use separate types for signup vs logged-in state.

---

### Issue 7: Import Error in app.py (FIXED ✅)
**Severity**: HIGH (FIXED)  
**File**: `app.py` (line 9)  
**Problem**: `render_template` imported from `flask_cors` instead of `flask`  
**Status**: ✅ FIXED in Phase 1

---

## Testing Checklist

- [ ] Test signup flow
- [ ] Test login flow  
- [ ] Test session persistence across page reload
- [ ] Test profile update with extended fields
- [ ] Test job listing with extended fields
- [ ] Test saved jobs toggle
- [ ] Test job application tracking
- [ ] Test logout and scraping stop
- [ ] Test CORS headers in browser dev tools

---

## Priority Order for Fixes

1. **HIGH**: Issue 1 - CORS credentials (breaks sessions)
2. **HIGH**: Issue 4 - Update profile extended fields (breaks profile save)
3. **MEDIUM**: Issue 2 - Login profile mapping (data loss on login)
4. **MEDIUM**: Issue 3 - Job field mapping (incomplete job data)
5. **MEDIUM**: Issue 5 - Session check (auth reliability)
6. **LOW**: Issue 6 - AuthUser type (security cleanup)

---

## Summary

**Total Issues Found**: 7 (1 already fixed)  
**High Priority**: 2  
**Medium Priority**: 3  
**Low Priority**: 1  

**Root Cause**: Frontend-backend integration incomplete - data structures exist on both sides but mapping is partial.

**Estimated Fix Time**: 30-45 minutes
**Files to Modify**: 
- `frontend/src/components/providers/app-state-provider.tsx` (5 fixes)
- `frontend/src/lib/types.ts` (1 fix)
