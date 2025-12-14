// Audio playback control for fencing commands

let audioContext = null;
const audioCache = new Map();

// Initialize audio context on user interaction
function initAudio() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    if (audioContext.state === 'suspended') {
        audioContext.resume();
    }
}

// Play audio file
async function playAudio(url) {
    initAudio();

    try {
        // Check cache first
        let audioBuffer = audioCache.get(url);

        if (!audioBuffer) {
            const response = await fetch(url);
            const arrayBuffer = await response.arrayBuffer();
            audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
            audioCache.set(url, audioBuffer);
        }

        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        source.start(0);
    } catch (error) {
        console.warn('Audio playback failed:', error);
        // Fallback to HTML5 Audio
        const audio = new Audio(url);
        audio.play().catch(e => console.warn('Fallback audio failed:', e));
    }
}

// Preload audio files for faster playback
async function preloadAudio(urls) {
    initAudio();

    for (const url of urls) {
        if (!audioCache.has(url)) {
            try {
                const response = await fetch(url);
                const arrayBuffer = await response.arrayBuffer();
                const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
                audioCache.set(url, audioBuffer);
            } catch (error) {
                console.warn('Failed to preload:', url, error);
            }
        }
    }
}

// Initialize audio on first user interaction
document.addEventListener('click', initAudio, { once: true });
document.addEventListener('touchstart', initAudio, { once: true });
