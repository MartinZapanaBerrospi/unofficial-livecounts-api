/**
 * Main UI Logic for Livecounts Dashboard Pro
 */

let activeInterval = null;
let lastCount = 0;

const platformSelect = document.getElementById('platformSelect');
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const dashboard = document.getElementById('dashboard');

searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') performSearch();
});

async function performSearch() {
    const platform = platformSelect.value;
    const query = searchInput.value;

    if (!query) return;

    // Show loading or clear dashboard
    dashboard.innerHTML = '<div style="text-align:center; padding: 4rem;">Cargando...</div>';
    
    if (activeInterval) clearInterval(activeInterval);

    try {
        const results = await api.search(platform, query);
        let targetId = '';
        let displayName = '';

        if (platform === 'youtube' && results.userData.length > 0) {
            targetId = results.userData[0].id;
            displayName = results.userData[0].username;
        } else if (platform === 'twitter' && results.userData.length > 0) {
            targetId = query; // Twitter stats usually take query/username
            displayName = results.userData[0].username;
        } else if (platform === 'twitch' && results.userData.length > 0) {
            targetId = results.userData[0].id;
            displayName = results.userData[0].username;
        } else if (platform === 'tiktok' && results.userData.length > 0) {
            targetId = results.userData[0].userId;
            displayName = results.userData[0].username;
        }

        if (targetId) {
            initStats(platform, targetId, displayName);
        } else {
            dashboard.innerHTML = '<div style="text-align:center; padding: 4rem;">No se encontraron resultados.</div>';
        }
    } catch (error) {
        dashboard.innerHTML = `<div style="text-align:center; padding: 4rem; color: #ef4444;">Error: ${error.message}</div>`;
    }
}

async function initStats(platform, id, name) {
    dashboard.innerHTML = `
        <div class="card">
            <span class="platform-badge">${platform}</span>
            <h2 style="margin-bottom: 0.5rem;">${name}</h2>
            <div id="mainCounter" class="count">0</div>
            <p class="label" id="counterLabel">Cargando seguidores...</p>
        </div>
    `;

    updateStats(platform, id);
    activeInterval = setInterval(() => updateStats(platform, id), 3000);
}

async function updateStats(platform, id) {
    try {
        const stats = await api.getStats(platform, id);
        let count = 0;
        let label = 'Seguidores';

        if (platform === 'youtube') {
            count = stats.followerCount;
            label = 'Subscriptores';
        } else if (platform === 'twitter') {
            count = stats.followerCount;
            label = 'Seguidores';
        } else if (platform === 'twitch') {
            count = stats.followerCount;
            label = 'Seguidores';
        } else if (platform === 'tiktok') {
            count = stats.followerCount;
            label = 'Seguidores';
        }

        const counterEl = document.getElementById('mainCounter');
        const labelEl = document.getElementById('counterLabel');

        if (count !== lastCount) {
            counterEl.classList.remove('bump');
            void counterEl.offsetWidth; // Trigger reflow
            counterEl.classList.add('bump');
            lastCount = count;
        }

        counterEl.innerText = count.toLocaleString();
        labelEl.innerText = `${label} en vivo`;
        
    } catch (error) {
        console.error("Update error:", error);
    }
}
