// DOM Elements
const situationInput = document.getElementById('situation');
const generateBtn = document.getElementById('generate-btn');
const btnText = document.getElementById('btn-text');
const btnHoverText = document.getElementById('btn-hover-text');
const loadingSpinner = document.getElementById('loading-spinner');
const errorBox = document.getElementById('error-box');
const resultBox = document.getElementById('result-box');
const resultText = document.getElementById('result-text');
const copyBtn = document.getElementById('copy-btn');

// Slider configuration
const sliders = [
    { inputId: 'blame', labelId: 'val-blame' },
    { inputId: 'jargon', labelId: 'val-jargon' },
    { inputId: 'passive', labelId: 'val-passive' },
    { inputId: 'vagueness', labelId: 'val-vagueness' }
];

// Initialize Slider Event Listeners
sliders.forEach(slider => {
    const inputEl = document.getElementById(slider.inputId);
    const labelEl = document.getElementById(slider.labelId);
    
    // Update the label text when slider moves
    inputEl.addEventListener('input', (e) => {
        labelEl.textContent = e.target.value;
    });
});

// Helper: Get slider value as integer
function getSliderVal(id) {
    return parseInt(document.getElementById(id).value, 10);
}

// Helper: Toggle Loading State
function setLoading(isLoading) {
    if (isLoading) {
        generateBtn.disabled = true;
        generateBtn.classList.add('cursor-not-allowed');
        btnText.classList.add('opacity-0');
        btnHoverText.classList.add('hidden');
        loadingSpinner.classList.add('active');
    } else {
        generateBtn.disabled = false;
        generateBtn.classList.remove('cursor-not-allowed');
        btnText.classList.remove('opacity-0');
        btnHoverText.classList.remove('hidden');
        loadingSpinner.classList.remove('active');
    }
}

// Helper: Show/Hide Error
function showError(msg) {
    if (msg) {
        errorBox.textContent = msg;
        errorBox.classList.remove('hidden');
        resultBox.classList.add('hidden');
    } else {
        errorBox.classList.add('hidden');
    }
}

// Generate Function
async function generateExcuse() {
    const situation = situationInput.value.trim();
    
    if (!situation) {
        situationInput.focus();
        showError('Please describe the situation first.');
        return;
    }

    showError(''); // Clear error
    setLoading(true);

    try {
        const blame = getSliderVal('blame');
        const jargon = getSliderVal('jargon');
        const passive = getSliderVal('passive');
        const vagueness = getSliderVal('vagueness');

        
        // Await reply from the server
        const excuse = await submitData(situation, blame, jargon, passive, vagueness)
        
        resultText.textContent = excuse;
        resultBox.classList.remove('hidden'); 
        
        // Trigger reflow for animation
        void resultBox.offsetWidth;
        resultBox.classList.add('fade-in');

    } catch (err) {
        console.error(err);
        // showError('Fabrication failed.');
        showError(err.message);
    } finally {
        setLoading(false);
    }
}

// Copy to Clipboard
copyBtn.addEventListener('click', () => {
    const textToCopy = resultText.textContent;
    navigator.clipboard.writeText(textToCopy);
    
    const span = copyBtn.querySelector('span');
    const originalText = span.textContent;
    span.textContent = 'Copied';
    
    setTimeout(() => {
        span.textContent = originalText;
    }, 2000);
});

// Attach Generate Listener
generateBtn.addEventListener('click', generateExcuse);

// Allow "Enter" key in input to trigger generation
situationInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generateExcuse();
    }
});


// Post the user data to the backend API
function submitData(text, blame, jargon, passive, vagueness) {
    console.log('User clicked generate');
    return fetch('http://127.0.0.1:5000/api/submit', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
            user_input: text, 
            blame,
            jargon, 
            passive, 
            vagueness
        })
    })
    .then(response => {
        console.log('Response received, status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Parsed data:', data);
        // Backend returns { success: true } or { success: false }
        if (!data.success) {
            console.log('Failed to process.');
            throw new Error('Failed: ' + data.error_message); // execution stops
        } 
        return data.excuse;
    });
}