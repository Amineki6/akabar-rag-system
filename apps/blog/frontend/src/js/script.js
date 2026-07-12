// --- 1. Global State to hold fetched API data ---
let apiArticles = [];

// Keep your existing color palettes
const avatarColors = {
  'SA': 'background:linear-gradient(135deg,#e8c49a,var(--orange))',
  'KL': 'background:linear-gradient(135deg,#9ac4e8,#5a8fbf)',
  'NB': 'background:linear-gradient(135deg,#b8e8a4,#62b87a)',
  'YM': 'background:linear-gradient(135deg,#e8b4d4,#bf6aa0)'
};

const paletteCss = [
  'background:linear-gradient(135deg,#e8c49a,#c47340)',
  'background:linear-gradient(135deg,#9ac4e8,#5a8fbf)',
  'background:linear-gradient(135deg,#b8e8a4,#62b87a)',
  'background:linear-gradient(135deg,#e8b4d4,#bf6aa0)',
  'background:linear-gradient(135deg,#e8e09a,#c8b450)',
  'background:linear-gradient(135deg,#c4a8e8,#8a5abf)'
];

// --- 2. Fetch Data on Load ---
document.addEventListener('DOMContentLoaded', async () => {
    await fetchBlogsFromAPI();
    
    // Check initial route for direct article link
    const path = window.location.pathname;
    if (path !== '/' && path !== '') {
        const slug = path.substring(1).replace(/\/$/, "");
        const idx = apiArticles.findIndex(b => b.slug === slug);
        if (idx !== -1) {
            // Render the specific article without flashing home
            document.getElementById('home-page').style.display = 'none';
            showArticle(null, idx, true); // true = initial load, don't push state
        }
    }
});

async function fetchBlogsFromAPI() {
    try {
        const response = await fetch('/api/blogs/');
        if (!response.ok) throw new Error('Failed to fetch blogs');
        
        apiArticles = await response.json();
        renderBlogLists();
    } catch (error) {
        console.error('API Error:', error);
        document.getElementById('latest-posts-grid').innerHTML = '<p>Unable to load posts.</p>';
    }
}

// --- 3. Render the Lists ---
function renderBlogLists() {
    const featuredContainer = document.getElementById('featured-post-container');
    const gridContainer = document.getElementById('latest-posts-grid');
    const listContainer = document.getElementById('more-reading-list');
    
    if (featuredContainer) featuredContainer.innerHTML = '';
    gridContainer.innerHTML = '';
    listContainer.innerHTML = '';

    if (!apiArticles || apiArticles.length === 0) {
        if (featuredContainer) featuredContainer.innerHTML = '<p style="text-align: center;">No featured articles</p>';
        return;
    }

    let featuredPostIndex = apiArticles.findIndex(p => p.is_featured);
    if (featuredPostIndex === -1) {
        featuredPostIndex = 0; // Fallback to newest
    }

    let renderedGridCount = 0;

    apiArticles.forEach((blog, index) => {
        const dateStr = new Date(blog.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        const bgStyle = paletteCss[index % paletteCss.length];
        const wordCount = blog.content ? blog.content.split(' ').length : 0;
        const readTime = Math.max(1, Math.ceil(wordCount / 200));

        if (index === featuredPostIndex && featuredContainer) {
            featuredContainer.innerHTML = `
      <div class="featured-image">
        <div class="img-geo" style="${bgStyle}; width:100%; height:100%; position:relative;">
          <div class="pattern-overlay"></div>
        </div>
      </div>
          <div class="featured-meta">
            <span class="post-category">${blog.subtitle || 'Highlight'}</span>
            <h2>${blog.title}</h2>
        <p>${blog.excerpt || ''}</p>
        <div class="post-footer">
          <div class="author-row">
            <div class="avatar" style="background:var(--orange);">AD</div>
            <div class="author-info">
              <div class="author-name">Khalil Kina</div>
              <div class="post-date">${dateStr} · ${readTime} min read</div>
            </div>
          </div>
          <button class="featured-read-btn" onclick="showArticle(event, ${index})">
            Read
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>`;
            return; // Skip rendering this in the grid/list
        }

        // The first 3 non-featured posts go to the grid
        if (renderedGridCount < 3) {
            renderedGridCount++;
            gridContainer.innerHTML += `
                <div class="post-card" onclick="showArticle(event, ${index})">
                    <div class="card-img">
                        <div class="card-img-bg" style="${bgStyle};width:100%;height:100%;position:relative;">
                            <div class="pattern-overlay"></div>
                        </div>
                    </div>
                    <div class="card-body">
                        <span class="post-category">${blog.subtitle || 'General'}</span>
                        <h3>${blog.title}</h3>
                        <p>${blog.excerpt || ''}</p>
                        <div class="card-footer">
                            <div class="author-row">
                                <div class="avatar" style="background:var(--orange);">AD</div>
                                <div class="author-info">
                                    <div class="author-name">Khalil Kina</div>
                                    <div class="post-date">${dateStr}</div>
                                </div>
                            </div>
                            <span class="reading-time">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                                ${readTime} min
                            </span>
                        </div>
                    </div>
                </div>
            `;
        } 
        // The rest go to the list below
        else {
            listContainer.innerHTML += `
                <a class="list-post-item" onclick="showArticle(event, ${index})">
                    <div class="list-num">0${index + 1}</div>
                    <div class="list-post-info">
                        <h4>${blog.title}</h4>
                        <span>${blog.subtitle || 'General'} · ${dateStr} · ${readTime} min read</span>
                    </div>
                    <svg class="list-arrow" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </a>
            `;
        }
    });
}

// --- 4. Handle UI Transitions (Adapted for API Data & Routing) ---
function showArticle(e, idx, isInitialLoad = false) {
  if(e) {
      e.preventDefault();
      const slug = apiArticles[idx].slug;
      history.pushState({ idx: idx }, '', `/${slug}`);
  }
  
  const blog = apiArticles[idx];
  const dateStr = new Date(blog.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  const bgStyle = paletteCss[idx % paletteCss.length];

  document.getElementById('art-subtitle').textContent = blog.subtitle || 'General';
  document.getElementById('art-title').textContent = blog.title;
  document.getElementById('art-author').textContent = 'Khalil Kina'; // Update if you add real author names to the DB
  document.getElementById('art-date').textContent = `${dateStr}`;
  document.getElementById('art-avatar').textContent = 'AD';
  document.getElementById('art-avatar').style.cssText = 'background:var(--orange);';
  
  document.getElementById('art-img').style.cssText = bgStyle + ';width:100%;height:100%;position:relative;';
  document.getElementById('art-img').innerHTML = '<div class="pattern-overlay"></div>';
  
  // Format the text content into paragraphs
  const formattedContent = blog.content.split('\n')
      .filter(p => p.trim() !== '')
      .map(p => `<p>${p}</p>`)
      .join('');
      
  document.getElementById('art-body').innerHTML = formattedContent;
  
  // Trigger your existing CSS transition
  document.getElementById('home-page').style.display = 'none';
  const ap = document.getElementById('article-page');
  ap.style.display = 'block';
  ap.classList.remove('page');
  void ap.offsetWidth;
  ap.classList.add('page');
  window.scrollTo({top: 0, behavior: 'smooth'});
}

// Keep your existing showHome, filterTag, and toggleTheme functions exactly as they are below
function showHome(e) {
  if(e) {
      e.preventDefault();
      history.pushState(null, '', '/');
  }
  document.getElementById('article-page').style.display = 'none';
  const hp = document.getElementById('home-page');
  hp.style.display = 'block';
  hp.classList.remove('page');
  void hp.offsetWidth;
  hp.classList.add('page');
  window.scrollTo({top: 0, behavior: 'smooth'});
}

function filterTag(e, tag) {
  e.preventDefault();
  const chips = document.querySelectorAll('.tag-chip');
  chips.forEach(c => c.style.borderColor = '');
  e.currentTarget.style.borderColor = 'var(--orange)';
}

let dark = false;
function toggleTheme() {
  dark = !dark;
  if(dark) {
    document.documentElement.style.setProperty('--cream', '#111110');
    document.documentElement.style.setProperty('--white', '#1c1c1a');
    document.documentElement.style.setProperty('--dark', '#f0ede6');
    document.documentElement.style.setProperty('--muted', '#6b6a67');
    document.documentElement.style.setProperty('--border', '#2e2e2c');
  } else {
    document.documentElement.style.setProperty('--cream', '#f5f2ec');
    document.documentElement.style.setProperty('--white', '#ffffff');
    document.documentElement.style.setProperty('--dark', '#1a1a18');
    document.documentElement.style.setProperty('--muted', '#8a8780');
    document.documentElement.style.setProperty('--border', '#e0dcd4');
  }
}

// --- 5. Reading Progress Bar ---
window.addEventListener('scroll', () => {
  const articlePage = document.getElementById('article-page');
  if (articlePage.style.display !== 'none') {
    const scrollTop = window.scrollY;
    // Calculate total scrollable height
    const docHeight = document.body.scrollHeight;
    const winHeight = window.innerHeight;
    const scrollPercent = scrollTop / (docHeight - winHeight);
    
    // Convert to percentage
    const scrollPercentRounded = Math.min(100, Math.max(0, Math.round(scrollPercent * 100)));
    document.getElementById('progress-bar').style.width = scrollPercentRounded + '%';
  }
});

// Handle browser back and forward buttons
window.addEventListener('popstate', (e) => {
    const path = window.location.pathname;
    if (path === '/' || path === '') {
        showHome(null);
    } else {
        const slug = path.substring(1).replace(/\/$/, "");
        const idx = apiArticles.findIndex(b => b.slug === slug);
        if (idx !== -1) {
            showArticle(null, idx, true);
        } else {
            showHome(null);
        }
    }
});

// --- Subscription Logic ---
function openSubscribeModal() {
    document.getElementById('subscribe-modal').style.display = 'flex';
}

function closeSubscribeModal() {
    document.getElementById('subscribe-modal').style.display = 'none';
}

async function submitSubscribe(source) {
    const isModal = source === 'modal';
    const emailInput = document.getElementById(isModal ? 'modal-email' : 'footer-email');
    const formContainer = document.getElementById(isModal ? 'modal-form-container' : 'footer-form-container');
    const successContainer = document.getElementById(isModal ? 'modal-success' : 'footer-success');
    const submitBtn = document.getElementById(isModal ? 'modal-submit' : 'footer-submit');
    
    const email = emailInput.value.trim();
    if (!email) {
        alert("Please enter a valid email address.");
        return;
    }

    // Disable button to prevent double-click
    const originalText = submitBtn.innerText;
    submitBtn.innerText = 'Sending...';
    submitBtn.disabled = true;

    try {
        const response = await fetch('/api/subscribe/', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ email: email })
        });

        if (response.ok) {
            // Success! Hide the form and show the green check mark layout
            formContainer.style.display = 'none';
            successContainer.style.display = 'block';
        } else {
            const data = await response.json();
            alert(data.detail || "Error subscribing. You might already be on the list!");
            submitBtn.innerText = originalText;
            submitBtn.disabled = false;
        }
    } catch (error) {
        console.error("Subscription error:", error);
        alert("A network error occurred.");
        submitBtn.innerText = originalText;
        submitBtn.disabled = false;
    }
}