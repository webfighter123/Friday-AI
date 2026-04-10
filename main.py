<script>
    // --- 1. THE VOICE STABILIZER ---
    let femaleVoice = null;
    const synth = window.speechSynthesis;

    function loadVoices() {
        const voices = synth.getVoices();
        // Priority: Neural Female -> Google Female -> System Female -> Any Female
        femaleVoice = voices.find(v => v.name.includes('Neural') && v.name.includes('Female')) ||
                      voices.find(v => v.name.includes('Google') && v.name.includes('en-US')) ||
                      voices.find(v => v.lang === 'en-US' && v.name.includes('Zira')) ||
                      voices.find(v => v.name.includes('Female'));
    }

    // Chrome and Safari load voices asynchronously
    if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = loadVoices;
    }
    loadVoices();

    // --- 2. 3D CORE (Smooth Rotation) ---
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('canvas3d'), alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    const sphere = new THREE.Mesh(new THREE.IcosahedronGeometry(1.5, 1), new THREE.MeshBasicMaterial({ color: 0x00d4ff, wireframe: true, transparent: true, opacity: 0.3 }));
    scene.add(sphere); camera.position.z = 5;
    function animate() { requestAnimationFrame(animate); sphere.rotation.y += 0.008; renderer.render(scene, camera); }
    animate();

    // --- 3. THE PROFESSIONAL SPEECH ENGINE ---
    async function speak(text, callback) {
        if (!femaleVoice) loadVoices(); // Emergency reload if empty

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.voice = femaleVoice;
        utterance.pitch = 1.15; // Sharper, professional female tone
        utterance.rate = 1.0;   // Natural pace
        
        utterance.onstart = () => {
            document.getElementById('waveCanvas').style.display = 'block';
            document.getElementById('status').innerText = "BUTTER_TRANSMITTING";
        };

        utterance.onend = () => {
            document.getElementById('waveCanvas').style.display = 'none';
            if (callback) callback();
            if (isOnline) startListening(); // Seamless loop
        };

        synth.speak(utterance);
    }

    let isOnline = false;
    async function startListening() {
        if (!isOnline) return;
        const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
        const rec = new SpeechRecognition();
        
        rec.onstart = () => { 
            document.getElementById('status').innerText = "LISTENING_ACTIVE"; 
        };

        rec.onresult = async (e) => {
            const query = e.results[0][0].transcript;
            document.getElementById('status').innerText = "NEURAL_SYNCING";
            
            try {
                const res = await fetch(`/ask?query=${encodeURIComponent(query)}`);
                const data = await res.json();
                document.getElementById('status').innerText = "READY";
                speak(data.reply);
            } catch (err) {
                document.getElementById('status').innerText = "LINK_ERROR";
                setTimeout(startListening, 1000);
            }
        };

        rec.onerror = () => { if(isOnline) rec.start(); }; // Auto-restart if it cuts out
        rec.start();
    }

    function toggleSystem() {
        isOnline = !isOnline;
        const btn = document.getElementById('mic-btn');
        if (isOnline) {
            btn.classList.add('active');
            // We wait 200ms to ensure the voice is ready before the first greeting
            setTimeout(() => speak("Hello Hiccup. Neural link established. How can I assist?"), 200);
        } else {
            btn.classList.remove('active');
            synth.cancel();
            document.getElementById('status').innerText = "NEURAL_IDLE";
        }
    }
</script>
