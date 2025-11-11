const API_BASE = 'http://localhost:4000/api';

/* ========= Page Navigation ========= */
function switchPage(pageId) {
    const pages = document.querySelectorAll('.page');
    const navLinks = document.querySelectorAll('.nav-link');
    
    pages.forEach(page => page.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageId) {
            link.classList.add('active');
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            switchPage(page);
            
            // Load content for specific pages
            if (page === 'scam-tips') loadPublicContent('scam-tips', 'scam-tips-list');
            if (page === 'scam-cases') loadPublicContent('scam-cases', 'scam-cases-list');
            if (page === 'user-manual') loadPublicContent('user-manual', 'user-manual-list');
        });
    });

    switchPage('home');
    
    // Initialize auth UI
    initAuthUI();
    
    // Preload scam tips
    loadPublicContent('scam-tips', 'scam-tips-list');
});

/* ========= AI Image Detection Feature ========= */
const uploadInput = document.getElementById("upload-input");
const previewDiv = document.getElementById("preview");
const detectBtn = document.getElementById("detect-btn");
let selectedFile = null;

if (uploadInput) {
    uploadInput.addEventListener("change", () => {
        const file = uploadInput.files[0];
        if (!file) return;
        
        selectedFile = file;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            if (previewDiv) {
                previewDiv.innerHTML = `
                    <img src="${e.target.result}" alt="Uploaded Image" style="max-width:400px;border-radius:8px;display:block;margin:20px auto;">
                    <p style="text-align:center; color:#aaa;">
                        ${file.name} (${(file.size / 1024).toFixed(1)} KB)
                    </p>
                `;
            }
            // Show detect button
            if (detectBtn) detectBtn.style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
    });
}

if (detectBtn) {
    detectBtn.addEventListener('click', async () => {
        if (!selectedFile) {
            alert('Please select an image first');
            return;
        }
        
        const resultDiv = document.getElementById('detection-result');
        if (!resultDiv) return;
        
        // Show loading
        resultDiv.innerHTML = `
            <div style="text-align:center; padding:40px;">
                <div class="loading"></div>
                <p style="color:#ddd; margin-top:20px;">🔍 Analyzing image for AI artifacts...</p>
            </div>
        `;
        
        try {
            const formData = new FormData();
            formData.append('image', selectedFile);
            
            const token = localStorage.getItem('ps_token');
            const headers = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            
            const response = await fetch(`${API_BASE}/detect-ai-image`, {
                method: 'POST',
                headers,
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                resultDiv.innerHTML = `
                    <div class="result-card">
                        <p style="color:#ff6b6b; text-align:center;">❌ ${data.message || 'Detection failed'}</p>
                    </div>
                `;
                return;
            }
            
            // Display results
            renderDetectionResult(data);
            
        } catch (error) {
            console.error('Detection error:', error);
            resultDiv.innerHTML = `
                <div class="result-card">
                    <p style="color:#ff6b6b; text-align:center;">❌ Network error: ${error.message}</p>
                </div>
            `;
        }
    });
}

function renderDetectionResult(data) {
    const resultDiv = document.getElementById('detection-result');
    if (!resultDiv) return;
    
    const isAI = data.is_ai_generated;
    const cardClass = isAI ? 'ai-generated' : 'likely-real';
    const headerClass = isAI ? 'ai' : 'real';
    const icon = isAI ? '🤖' : '✅';
    const label = isAI ? 'AI-Generated' : 'Likely Real';
    
    resultDiv.innerHTML = `
        <div class="result-card ${cardClass}">
            <div class="result-header ${headerClass}">
                ${icon} ${label}
            </div>
            
            <div class="result-metrics">
                <div class="metric-box">
                    <div class="metric-label">Confidence Score</div>
                    <div class="metric-value">${data.confidence_percent}%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Probability</div>
                    <div class="metric-value">${data.probability_score}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Likely Source</div>
                    <div class="metric-value" style="font-size:16px;">${data.likely_generator}</div>
                </div>
            </div>
            
            <div class="explanation-box">
                <h4>📋 Detailed Analysis</h4>
                <pre>${data.explanation}</pre>
            </div>
            
            <div style="text-align:center; margin-top:20px;">
                <button onclick="document.getElementById('upload-input').click()" 
                        style="padding:10px 20px; background:#3f3e3e; color:#fff; border:none; border-radius:6px; cursor:pointer;">
                    🔄 Analyze Another Image
                </button>
            </div>
        </div>
    `;
}

/* ========= Auth: Register & Login ========= */
const registerForm = document.getElementById('register-form');
const registerMessage = document.getElementById('register-message');
const loginForm = document.getElementById('login-form');
const loginLink = document.getElementById('login-link');
const adminPanelLink = document.getElementById('admin-panel-link');
const loginMessage = document.getElementById('login-message');

function setLoggedIn(user, token) {
    localStorage.setItem('ps_user', JSON.stringify(user));
    localStorage.setItem('ps_token', token);
    if (loginLink) { 
        loginLink.textContent = 'Logout'; 
        loginLink.dataset.loggedIn = '1'; 
    }
    if (user.role === 'admin' && adminPanelLink) {
        adminPanelLink.style.display = 'block';
    }
}

function clearLogin() {
    localStorage.removeItem('ps_user');
    localStorage.removeItem('ps_token');
    if (loginLink) { 
        loginLink.textContent = 'Login'; 
        loginLink.dataset.loggedIn = '0'; 
    }
    if (adminPanelLink) {
        adminPanelLink.style.display = 'none';
    }
}

function getAuthHeader() {
    const token = localStorage.getItem('ps_token');
    return token
        ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
        : { 'Content-Type': 'application/json' };
}

function initAuthUI() {
    const userData = localStorage.getItem('ps_user');
    if (userData) {
        const user = JSON.parse(userData);
        if (loginLink) { 
            loginLink.textContent = 'Logout'; 
            loginLink.dataset.loggedIn = '1'; 
        }
        if (user.role === 'admin' && adminPanelLink) {
            adminPanelLink.style.display = 'block';
        }
    } else {
        clearLogin();
    }
}

if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const password = document.getElementById('reg-password').value;
        const regSecret = document.getElementById('reg-admin-secret').value;
        
        if (!username || !password) {
            registerMessage.style.color = '#ff6b6b';
            registerMessage.textContent = 'Please provide username and password';
            return;
        }

        try {
            const resp = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username,
                    password,
                    role: regSecret ? 'admin' : 'user',
                    reg_secret: regSecret
                })
            });
            
            const data = await resp.json();
            
            if (!resp.ok) {
                registerMessage.style.color = '#ff6b6b';
                registerMessage.textContent = data.message || 'Registration failed';
                return;
            }
            
            registerMessage.style.color = '#6bff6b';
            registerMessage.textContent = 'Account created successfully! Please login.';
            registerForm.reset();
            setTimeout(() => switchPage('login'), 1500);
            
        } catch (err) {
            console.error(err);
            registerMessage.style.color = '#ff6b6b';
            registerMessage.textContent = 'Network error';
        }
    });
}

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            const data = await res.json();
            
            if (!res.ok) {
                loginMessage.textContent = data.message || 'Login failed';
                return;
            }

            setLoggedIn(data.user, data.token);
            loginMessage.style.color = '#6bff6b';
            loginMessage.textContent = `Welcome back, ${data.user.username}!`;
            setTimeout(() => switchPage('home'), 1000);
            
        } catch (err) {
            loginMessage.textContent = 'Network error';
        }
    });
}

if (loginLink) {
    loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        const loggedIn = loginLink.dataset.loggedIn === '1';
        if (loggedIn) {
            clearLogin();
            switchPage('home');
            alert('Logged out successfully');
        } else {
            switchPage('login');
        }
    });
}

/* ========= Admin Panel ========= */
// Show/hide news link field based on selected resource
const uploadResourceSelect = document.getElementById('upload-resource-select');
const newsLinkSection = document.getElementById('news-link-section');

if (uploadResourceSelect && newsLinkSection) {
    uploadResourceSelect.addEventListener('change', function() {
        if (this.value === 'scam-cases') {
            newsLinkSection.style.display = 'block';
        } else {
            newsLinkSection.style.display = 'none';
        }
    });
}

// Load items button
const loadItemsBtn = document.getElementById('load-items');
if (loadItemsBtn) {
    loadItemsBtn.addEventListener('click', async () => {
        const resource = document.getElementById('resource-select').value;
        const container = document.getElementById('admin-items');
        const msgDiv = document.getElementById('admin-msg');
        
        if (!container) return;
        
        container.innerHTML = `
            <div style="text-align:center; padding:30px; color:#aaa;">
                <i class="fa fa-spinner fa-spin" style="font-size:32px; margin-bottom:15px;"></i>
                <p>Loading items...</p>
            </div>
        `;
        
        if (msgDiv) msgDiv.textContent = '';

        try {
            const res = await fetch(`${API_BASE}/content/${resource}`);
            const items = await res.json();
            
            if (!res.ok) {
                throw new Error(items.message || 'Failed to load items');
            }
            
            container.innerHTML = '';

            if (!items || items.length === 0) {
                container.innerHTML = `
                    <div style="text-align:center; padding:40px; background:rgba(0,0,0,0.2); border-radius:12px; margin-top:20px;">
                        <i class="fa fa-inbox" style="font-size:48px; color:#555; margin-bottom:15px;"></i>
                        <p style="color:#aaa; font-size:16px;">No items found. Upload some content to get started!</p>
                    </div>
                `;
                return;
            }

            items.forEach(it => {
                const div = document.createElement('div');
                div.className = 'admin-item';
                
                const displayTitle = it.title || it.headline || 'Untitled';
                const displayPath = it.file_path || it.image_path || it.news_link || '';
                
                div.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: start; gap: 20px;">
                        <div style="flex: 1;">
                            <h4 style="display: flex; align-items: center; gap: 8px;">
                                <i class="fa fa-file"></i> ${displayTitle}
                            </h4>
                            <div style="color:#aaa; font-size:13px; margin-top:8px;">
                                <strong>ID:</strong> ${it.id} | <strong>Path:</strong> ${displayPath || 'N/A'}
                            </div>
                            ${it.created_at ? `<div style="color:#888; font-size:12px; margin-top:5px;"><i class="fa fa-clock"></i> ${new Date(it.created_at).toLocaleString()}</div>` : ''}
                        </div>
                        <div style="display: flex; gap: 10px;">
                            <button data-id="${it.id}" class="edit-item" style="background: linear-gradient(135deg, #1a73e8 0%, #0d47a1 100%); padding: 8px 16px; border: none; border-radius: 8px; color: white; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.3s;">
                                <i class="fa fa-edit"></i> Edit
                            </button>
                            <button data-id="${it.id}" class="delete-item" style="background: linear-gradient(135deg, #d32f2f 0%, #b71c1c 100%); padding: 8px 16px; border: none; border-radius: 8px; color: white; cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all 0.3s;">
                                <i class="fa fa-trash"></i> Delete
                            </button>
                        </div>
                    </div>
                `;
                container.appendChild(div);
            });

            // Delete handlers
            container.querySelectorAll('.delete-item').forEach(btn => {
                btn.addEventListener('click', async (ev) => {
                    if (!confirm('⚠️ Are you sure you want to delete this item? This action cannot be undone.')) return;
                    
                    const id = ev.target.closest('button').dataset.id;
                    const headers = getAuthHeader();
                    
                    try {
                        const resp = await fetch(`${API_BASE}/content/${resource}/${id}`, { 
                            method: 'DELETE', 
                            headers 
                        });
                        
                        if (resp.ok) {
                            ev.target.closest('.admin-item').remove();
                            if (msgDiv) {
                                msgDiv.style.color = '#6bff6b';
                                msgDiv.textContent = '✓ Deleted successfully';
                                setTimeout(() => msgDiv.textContent = '', 3000);
                            }
                        } else {
                            const data = await resp.json();
                            if (msgDiv) {
                                msgDiv.style.color = '#ff6b6b';
                                msgDiv.textContent = '✗ Delete failed: ' + (data.message || 'Unknown error');
                            }
                        }
                    } catch (err) {
                        console.error(err);
                        if (msgDiv) {
                            msgDiv.style.color = '#ff6b6b';
                            msgDiv.textContent = '✗ Network error during delete';
                        }
                    }
                });
            });

            // Edit handlers
            container.querySelectorAll('.edit-item').forEach(btn => {
                btn.addEventListener('click', async (ev) => {
                    const id = ev.target.closest('button').dataset.id;
                    const newTitle = prompt('Enter new title/headline:');
                    if (!newTitle) return;
                    
                    const newBody = prompt('Enter new path/URL:');
                    if (!newBody) return;
                    
                    const headers = getAuthHeader();
                    
                    try {
                        const resp = await fetch(`${API_BASE}/content/${resource}/${id}`, {
                            method: 'PUT',
                            headers,
                            body: JSON.stringify({ title: newTitle, body: newBody })
                        });
                        
                        if (resp.ok) {
                            if (msgDiv) {
                                msgDiv.style.color = '#6bff6b';
                                msgDiv.textContent = '✓ Updated successfully';
                                setTimeout(() => msgDiv.textContent = '', 3000);
                            }
                            loadItemsBtn.click();
                        } else {
                            const data = await resp.json();
                            if (msgDiv) {
                                msgDiv.style.color = '#ff6b6b';
                                msgDiv.textContent = '✗ Update failed: ' + (data.message || 'Unknown error');
                            }
                        }
                    } catch (err) {
                        console.error(err);
                        if (msgDiv) {
                            msgDiv.style.color = '#ff6b6b';
                            msgDiv.textContent = '✗ Network error during update';
                        }
                    }
                });
            });

        } catch (err) {
            container.innerHTML = `
                <div style="color:#ff6b6b; text-align:center; padding:30px; background:rgba(211,47,47,0.1); border-radius:12px; margin-top:20px;">
                    <i class="fa fa-exclamation-triangle" style="font-size:32px; margin-bottom:10px;"></i>
                    <p>Error loading items: ${err.message}</p>
                </div>
            `;
            console.error(err);
        }
    });
}

// Admin upload form
const uploadForm = document.getElementById('admin-upload-form');
if (uploadForm) {
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const resource = document.getElementById('upload-resource-select').value;
        const title = document.getElementById('upload-title').value.trim();
        const fileInput = document.getElementById('upload-file');
        const file = fileInput && fileInput.files && fileInput.files[0];
        const link = document.getElementById('upload-link').value.trim();
        const msgDiv = document.getElementById('admin-msg');

        if (!file) {
            alert('⚠️ Please select a file to upload');
            return;
        }
        
        if (!title) {
            alert('⚠️ Please enter a title/headline');
            return;
        }

        // Validate file type
        const fileExt = file.name.split('.').pop().toLowerCase();
        if (resource === 'user-manual' && fileExt !== 'pdf') {
            alert('⚠️ User manuals must be PDF files');
            return;
        }
        if ((resource === 'scam-tips' || resource === 'scam-cases') && 
            !['jpg', 'jpeg', 'png', 'gif', 'webp', 'avif'].includes(fileExt)) {
            alert('⚠️ Please upload an image file (JPG, PNG, GIF, WEBP, AVIF)');
            return;
        }

        const formData = new FormData();
        formData.append('title', title);
        formData.append('headline', title);
        
        if (resource === 'scam-cases' && link) {
            formData.append('news_link', link);
        }
        
        if (resource === 'user-manual') {
            formData.append('manual', file);
        } else if (resource === 'scam-tips') {
            formData.append('poster', file);
        } else if (resource === 'scam-cases') {
            formData.append('caseImage', file);
        }

        const token = localStorage.getItem('ps_token');
        
        if (!token) {
            alert('⚠️ You must be logged in as admin to upload content');
            return;
        }
        
        const headers = { 'Authorization': `Bearer ${token}` };

        // Show uploading message
        if (msgDiv) {
            msgDiv.style.color = '#4dabf7';
            msgDiv.textContent = '⏳ Uploading... Please wait';
        }

        // Disable submit button
        const submitBtn = uploadForm.querySelector('button[type="submit"]');
        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Uploading...';

        try {
            const resp = await fetch(`${API_BASE}/admin/${resource}`, {
                method: 'POST',
                headers,
                body: formData
            });

            const data = await resp.json();
            
            if (resp.ok) {
                if (msgDiv) {
                    msgDiv.style.color = '#6bff6b';
                    msgDiv.textContent = '✓ ' + (data.message || 'Upload successful!');
                    setTimeout(() => msgDiv.textContent = '', 5000);
                }
                uploadForm.reset();
                alert('✅ ' + (data.message || 'Upload successful!'));
            } else {
                if (msgDiv) {
                    msgDiv.style.color = '#ff6b6b';
                    msgDiv.textContent = '✗ ' + (data.message || 'Upload failed');
                }
                alert('❌ ' + (data.message || 'Upload failed'));
            }
        } catch (err) {
            console.error(err);
            if (msgDiv) {
                msgDiv.style.color = '#ff6b6b';
                msgDiv.textContent = '✗ Network error during upload';
            }
            alert('❌ Network error during upload: ' + err.message);
        } finally {
            // Re-enable submit button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

/* ========= Public Content Display ========= */
async function loadPublicContent(resource, targetId) {
    const container = document.getElementById(targetId);
    if (!container) return;
    container.innerHTML = "<p style='text-align:center;color:#ddd;'>Loading...</p>";

    try {
        const res = await fetch(`${API_BASE}/content/${resource}`);
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.message || "Failed to load");
        if (!Array.isArray(data) || !data.length) {
            let emptyMessage = "";
            if (resource === "scam-tips") {
                emptyMessage = `
                    <div style="text-align:center; padding:40px; background:#2b2b2b; border-radius:8px; margin:20px 0;">
                        <i class="fa fa-info-circle" style="font-size:48px; color:#1a73e8; margin-bottom:20px;"></i>
                        <h3 style="color:#fff; margin-bottom:15px;">No Scam Tips Available Yet</h3>
                        <p style="color:#aaa;">Admin can upload scam awareness posters from the Admin Panel.</p>
                    </div>
                `;
            } else if (resource === "scam-cases") {
                emptyMessage = `
                    <div style="text-align:center; padding:40px; background:#2b2b2b; border-radius:8px; margin:20px 0;">
                        <i class="fa fa-exclamation-triangle" style="font-size:48px; color:#1a73e8; margin-bottom:20px;"></i>
                        <h3 style="color:#fff; margin-bottom:15px;">No Scam Cases Reported Yet</h3>
                        <p style="color:#aaa;">Check back later for Malaysia parcel scam case reports.</p>
                    </div>
                `;
            } else if (resource === "user-manual") {
                emptyMessage = `
                    <div style="text-align:center; padding:40px; background:#2b2b2b; border-radius:8px; margin:20px 0;">
                        <i class="fa fa-book" style="font-size:48px; color:#1a73e8; margin-bottom:20px;"></i>
                        <h3 style="color:#fff; margin-bottom:15px;">No User Manuals Available</h3>
                        <p style="color:#aaa;">Documentation will be uploaded by administrators.</p>
                    </div>
                `;
            }
            container.innerHTML = emptyMessage;
            return;
        }

        let html = "";
        if (resource === "scam-tips") {
            html = data.map(item => `
                <div class="content-item">
                    <h3>${item.title}</h3>
                    ${item.image_path ? `<img src="${item.image_path}" alt="${item.title}">` : ""}
                </div>
            `).join("");
        } else if (resource === "scam-cases") {
            html = data.map(item => `
                <div class="content-item">
                    <h3>${item.headline}</h3>
                    ${item.image_path ? `<img src="${item.image_path}" alt="${item.headline}">` : ""}
                    ${item.news_link ? `<p><a href="${item.news_link}" target="_blank">Read full news article →</a></p>` : ""}
                </div>
            `).join("");
        } else if (resource === "user-manual") {
            html = data.map(item => `
                <div class="content-item">
                    <h3>${item.title}</h3>
                    ${item.file_path ? `<p><a href="${item.file_path}" target="_blank">📄 Open Manual (PDF) →</a></p>` : ""}
                </div>
            `).join("");
        }

        container.innerHTML = html;
    } catch (err) {
        console.error(err);
        container.innerHTML = `<p style="color:red; text-align:center;">Error: ${err.message}</p>`;
    }
}
