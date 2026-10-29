// ==========================================
// ROX 3D HUMANOID AI - JAW LIP-SYNC & AUDIO ENGINE
// ==========================================

let scene, camera, renderer, controls;
let avatarGroup, jawGroup, eyeLightLeft, eyeLightRight;
let holoRing1, holoRing2;
let audioCtx, analyser, audioSource, audioElem;
let isSpeaking = false;
let mouthOpenTarget = 0;

// Initialize 3D Scene
function init3D() {
    const container = document.getElementById('canvas-container');
    
    // Scene & Camera
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x060913, 0.05);

    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 0.5, 3.2);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    container.appendChild(renderer.domElement);

    // Controls
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxDistance = 5;
    controls.minDistance = 1.5;
    controls.maxPolarAngle = Math.PI / 2 + 0.1;

    // Lights
    const ambientLight = new THREE.AmbientLight(0x0f172a, 2.0);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0x00f2fe, 2.5);
    dirLight.position.set(2, 4, 3);
    scene.add(dirLight);

    const rimLight = new THREE.DirectionalLight(0xff007f, 2.0);
    rimLight.position.set(-3, 2, -2);
    scene.add(rimLight);

    buildCyberHumanoid();
    createParticleMatrix();

    window.addEventListener('resize', onWindowResize);
}

// Build Articulated 3D Cyber Humanoid
function buildCyberHumanoid() {
    avatarGroup = new THREE.Group();
    avatarGroup.position.set(0, -0.2, 0);

    // Metallic Materials
    const chromeMat = new THREE.MeshStandardMaterial({
        color: 0x1e293b,
        metalness: 0.85,
        roughness: 0.25,
    });

    const glowCyanMat = new THREE.MeshBasicMaterial({
        color: 0x00f2fe
    });

    const darkPlateMat = new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        metalness: 0.9,
        roughness: 0.4
    });

    // 1. Head Cranium
    const headGeo = new THREE.SphereGeometry(0.5, 32, 32);
    headGeo.scale(1, 1.15, 1.05);
    const headMesh = new THREE.Mesh(headGeo, chromeMat);
    avatarGroup.add(headMesh);

    // Face Mask Plate
    const facePlateGeo = new THREE.CylinderGeometry(0.38, 0.32, 0.55, 32, 1, false, 0, Math.PI);
    const facePlate = new THREE.Mesh(facePlateGeo, darkPlateMat);
    facePlate.rotation.y = -Math.PI / 2;
    facePlate.position.set(0, 0.02, 0.35);
    avatarGroup.add(facePlate);

    // 2. Glowing Visor / Eyes
    const visorGeo = new THREE.BoxGeometry(0.48, 0.08, 0.1);
    const visor = new THREE.Mesh(visorGeo, glowCyanMat);
    visor.position.set(0, 0.12, 0.52);
    avatarGroup.add(visor);

    // 3. Articulated Jaw (For Lip-Sync!)
    jawGroup = new THREE.Group();
    jawGroup.position.set(0, -0.15, 0.15); // Pivot point for jaw opening

    const jawGeo = new THREE.BoxGeometry(0.32, 0.22, 0.35);
    const jawMesh = new THREE.Mesh(jawGeo, chromeMat);
    jawMesh.position.set(0, -0.1, 0.15);
    jawGroup.add(jawMesh);

    // Mouth Neon Line
    const mouthLineGeo = new THREE.BoxGeometry(0.22, 0.02, 0.04);
    const mouthLine = new THREE.Mesh(mouthLineGeo, glowCyanMat);
    mouthLine.position.set(0, -0.01, 0.34);
    jawGroup.add(mouthLine);

    avatarGroup.add(jawGroup);

    // 4. Cyber Neck & Torso
    const neckGeo = new THREE.CylinderGeometry(0.18, 0.22, 0.35, 16);
    const neck = new THREE.Mesh(neckGeo, darkPlateMat);
    neck.position.set(0, -0.65, 0);
    avatarGroup.add(neck);

    const chestGeo = new THREE.BoxGeometry(0.9, 0.6, 0.5);
    const chest = new THREE.Mesh(chestGeo, chromeMat);
    chest.position.set(0, -1.05, 0);
    avatarGroup.add(chest);

    // Core Arc Reactor
    const coreGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.08, 32);
    coreGeo.rotateX(Math.PI / 2);
    const coreMesh = new THREE.Mesh(coreGeo, glowCyanMat);
    coreMesh.position.set(0, -0.95, 0.26);
    avatarGroup.add(coreMesh);

    // Holographic Energy Rings
    const ringGeo = new THREE.TorusGeometry(0.9, 0.008, 16, 64);
    holoRing1 = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0x00f2fe, wireframe: true }));
    holoRing1.rotation.x = Math.PI / 2.3;
    avatarGroup.add(holoRing1);

    holoRing2 = new THREE.Mesh(ringGeo, new THREE.MeshBasicMaterial({ color: 0xff007f, wireframe: true }));
    holoRing2.rotation.y = Math.PI / 3;
    holoRing2.scale.set(1.15, 1.15, 1.15);
    avatarGroup.add(holoRing2);

    scene.add(avatarGroup);
}

// Background Particle Matrix
function createParticleMatrix() {
    const count = 600;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);

    for (let i = 0; i < count * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 12;
        positions[i + 1] = (Math.random() - 0.5) * 12;
        positions[i + 2] = (Math.random() - 0.5) * 12;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const material = new THREE.PointsMaterial({
        color: 0x00f2fe,
        size: 0.035,
        transparent: true,
        opacity: 0.6
    });

    const particles = new THREE.Points(geometry, material);
    scene.add(particles);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Animation Loop
let clock = new THREE.Clock();

function animate() {
    requestAnimationFrame(animate);
    const elapsed = clock.getElapsedTime();

    // Idle breathing & floating
    if (avatarGroup) {
        avatarGroup.position.y = -0.2 + Math.sin(elapsed * 1.5) * 0.03;
        avatarGroup.rotation.y = Math.sin(elapsed * 0.5) * 0.08;
    }

    if (holoRing1) holoRing1.rotation.z += 0.008;
    if (holoRing2) holoRing2.rotation.x += 0.006;

    // Real-time Lip-Sync Calculation
    if (isSpeaking && analyser) {
        const freqData = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(freqData);

        // Calculate average speech volume in vocal frequency range (300Hz - 3kHz)
        let sum = 0;
        const binCount = 35;
        for (let i = 2; i < binCount; i++) {
            sum += freqData[i];
        }
        const avg = sum / (binCount - 2);
        
        // Map volume to jaw rotation angle (0 to 0.45 radians)
        mouthOpenTarget = (avg / 255.0) * 0.5;
    } else {
        mouthOpenTarget = 0;
    }

    // Smoothly interpolate jaw movement
    if (jawGroup) {
        jawGroup.rotation.x += (mouthOpenTarget - jawGroup.rotation.x) * 0.35;
    }

    drawWaveform();
    controls.update();
    renderer.render(scene, camera);
}

// Audio Waveform Visualizer
const visualizerCanvas = document.getElementById('visualizer');
const visualizerCtx = visualizerCanvas.getContext('2d');

function drawWaveform() {
    const width = visualizerCanvas.width = visualizerCanvas.offsetWidth;
    const height = visualizerCanvas.height = visualizerCanvas.offsetHeight;
    visualizerCtx.clearRect(0, 0, width, height);

    if (!analyser || !isSpeaking) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteTimeDomainData(dataArray);

    visualizerCtx.lineWidth = 2.5;
    visualizerCtx.strokeStyle = '#00f2fe';
    visualizerCtx.beginPath();

    const sliceWidth = width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = (v * height) / 2;
        if (i === 0) visualizerCtx.moveTo(x, y);
        else visualizerCtx.lineTo(x, y);
        x += sliceWidth;
    }

    visualizerCtx.lineTo(width, height / 2);
    visualizerCtx.stroke();
}

// ==========================================
// VOICE SYNTHESIS (TTS) & AUDIO PLAYBACK
// ==========================================

async function playRoxSpeech(text) {
    try {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === 'suspended') {
            await audioCtx.resume();
        }

        const resp = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });

        if (!resp.ok) throw new Error('TTS network error');

        const blob = await resp.blob();
        const audioUrl = URL.createObjectURL(blob);

        if (audioElem) audioElem.pause();
        audioElem = new Audio(audioUrl);

        if (!audioSource) {
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 256;
            audioSource = audioCtx.createMediaElementSource(audioElem);
            audioSource.connect(analyser);
            analyser.connect(audioCtx.destination);
        }

        audioElem.onplay = () => { isSpeaking = true; };
        audioElem.onended = () => { isSpeaking = false; };
        audioElem.onerror = () => { isSpeaking = false; };

        await audioElem.play();
    } catch (err) {
        console.error("Audio playback error:", err);
        isSpeaking = false;
    }
}

// ==========================================
// CHAT & SPEECH RECOGNITION (STT)
// ==========================================

const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');

function appendMessage(sender, text, isUser = false) {
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${isUser ? 'user' : 'rox'}`;
    bubble.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(bubble);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function handleSendMessage(msg) {
    const text = msg || userInput.value.trim();
    if (!text) return;

    userInput.value = '';
    appendMessage('YOU', text, true);

    try {
        const resp = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await resp.json();
        const reply = data.reply || "Kuch samajh nahi aaya bhai.";

        appendMessage('ROX', reply, false);
        playRoxSpeech(reply);
    } catch (err) {
        appendMessage('ROX', `Network error: ${err.message}`, false);
    }
}

sendBtn.addEventListener('click', () => handleSendMessage());
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendMessage();
});

// Microphone Recognition
let recognition = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'hi-IN'; // Supports Hinglish/Hindi & English

    recognition.onstart = () => {
        micBtn.classList.add('recording');
        micBtn.innerText = '⏹️';
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        handleSendMessage(transcript);
    };

    recognition.onerror = () => {
        micBtn.classList.remove('recording');
        micBtn.innerText = '🎤';
    };

    recognition.onend = () => {
        micBtn.classList.remove('recording');
        micBtn.innerText = '🎤';
    };

    micBtn.addEventListener('click', () => {
        if (micBtn.classList.contains('recording')) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });
} else {
    micBtn.style.display = 'none';
}

// Start 3D Engine on load
window.addEventListener('DOMContentLoaded', () => {
    init3D();
    animate();
});
