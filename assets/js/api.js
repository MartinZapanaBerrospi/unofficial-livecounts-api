/**
 * Livecounts API Logic ported to JavaScript
 * High performance real-time stats for TikTok, YouTube, Twitter, Twitch
 */

const PROXY = "https://corsproxy.io/?";

const ENDPOINTS = {
    tiktok: {
        search: "https://tiktok.livecounts.io/user/search",
        stats: "https://tiktok.livecounts.io/user/stats"
    },
    youtube: {
        search: "https://api.livecounts.io/youtube-live-subscriber-counter/search",
        stats: "https://api.livecounts.io/youtube-live-subscriber-counter/stats"
    },
    twitter: {
        search: "https://api.livecounts.io/twitter-live-follower-counter/search",
        stats: "https://api.livecounts.io/twitter-live-follower-counter/stats"
    },
    twitch: {
        search: "https://api.livecounts.io/twitch-live-follower-counter/search",
        stats: "https://api.livecounts.io/twitch-live-follower-counter/stats"
    }
};

/**
 * Port of the Midas/Catto/Ajay hashing algorithm
 */
function getHeaders(timestamp) {
    const ajay = timestamp;
    // We assume CryptoJS is loaded in HTML
    const catto = CryptoJS.RIPEMD160(ajay.toString()).toString();
    const midas = CryptoJS.SHA384(CryptoJS.SHA256((ajay + 64).toString()).toString()).toString();

    return {
        "X-Ajay": ajay.toString(),
        "X-Catto": catto,
        "X-Midas": midas,
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://livecounts.io",
        "Referer": "https://livecounts.io/"
    };
}

async function fetchAPI(url, isTikTok = false) {
    const timestamp = Date.now();
    const headers = getHeaders(timestamp);
    
    if (isTikTok) {
        headers["Origin"] = "https://tiktok.livecounts.io";
        headers["Referer"] = "https://tiktok.livecounts.io/";
    }

    const fullUrl = `${PROXY}${encodeURIComponent(url)}`;
    
    try {
        const response = await fetch(fullUrl, {
            method: 'GET',
            headers: headers
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP Error: ${response.status} - ${errorText}`);
        }
        
        const parsed = await response.json();
        
        if (!parsed.success && parsed.success !== undefined) {
            throw new Error("API Unsuccessful");
        }
        return parsed;
    } catch (error) {
        console.error("API Error:", error);
        throw error;
    }
}

const api = {
    async search(platform, query) {
        let url = `${ENDPOINTS[platform].search}/${query}`;
        return await fetchAPI(url, platform === 'tiktok');
    },
    async getStats(platform, id) {
        let url = `${ENDPOINTS[platform].stats}/${id}`;
        return await fetchAPI(url, platform === 'tiktok');
    }
};
