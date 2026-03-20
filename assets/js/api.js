/**
 * Livecounts API Logic ported to JavaScript
 * High performance real-time stats for TikTok, YouTube, Twitter, Twitch
 */

const PROXY = "https://corsproxy.io/?";

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
            // headers: headers // Note: corsproxy.io might strip custom headers or fail if we send them in the fetch call directly due to preflight
        });

        if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
        
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
