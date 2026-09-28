/**
 * ComicCraft Interactive Client Application
 */

// Preset story briefs
const PRESETS = {
    fox: {
        prompt: "A brave fox explores an enchanted forest to find a legendary star fragment.",
        character: "Ember",
        setting: "Forest",
        tone: "Dramatic",
        style: "Realistic"
    },
    robot: {
        prompt: "Unit-7 the maintenance robot awakens alone on a derelict starship and finds a thriving garden.",
        character: "Unit-7",
        setting: "Deep Space",
        tone: "Whimsical",
        style: "Comic Book"
    },
    samurai: {
        prompt: "A wandering master swordsman defends a secluded mountain temple from ancient shadow beasts.",
        character: "Jin",
        setting: "Medieval Castle",
        tone: "Epic Action",
        style: "Anime / Manga"
    },
    cyberpunk: {
        prompt: "A street-smart cybernetic detective tracks an elusive rogue AI through neon-drenched rainy alleys.",
        character: "Vex",
        setting: "Cyberpunk Metropolis",
        tone: "Dark & Mysterious",
        style: "Cyberpunk"
    }
};

function applyPreset(key) {
    const data = PRESETS[key];
    if (!data) return;

    const promptEl = document.getElementById('story_prompt');
    const charEl = document.getElementById('character_name');
    const settingEl = document.getElementById('setting');
    const toneEl = document.getElementById('tone');
    const styleEl = document.getElementById('art_style');

    if (promptEl) promptEl.value = data.prompt;
    if (charEl) charEl.value = data.character;
    if (settingEl) settingEl.value = data.setting;
    if (toneEl) toneEl.value = data.tone;
    if (styleEl) styleEl.value = data.style;

    // Update active preset pill
    document.querySelectorAll('.preset-pill').forEach(btn => btn.classList.remove('active'));
    if (window.event && window.event.target) {
        window.event.target.classList.add('active');
    }

    // Trigger character counter update
    updateCharCounter();
}

function updateCharCounter() {
    const promptEl = document.getElementById('story_prompt');
    const counterEl = document.getElementById('char-counter');
    if (promptEl && counterEl) {
        const len = promptEl.value.length;
        counterEl.textContent = `${len} / 1000`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const comicForm = document.getElementById('comic-form');
    const loadingOverlay = document.getElementById('loading-overlay');
    const loadingMessage = document.getElementById('loading-message');
    const progressBar = document.getElementById('progress-bar-fill');
    const progressPercent = document.getElementById('progress-percent');
    const promptEl = document.getElementById('story_prompt');

    // Attach char counter listener
    if (promptEl) {
        promptEl.addEventListener('input', updateCharCounter);
        updateCharCounter();
    }

    // Attach submission handling with multi-stage progress
    if (comicForm && loadingOverlay) {
        comicForm.addEventListener('submit', (e) => {
            loadingOverlay.classList.remove('hidden');

            const steps = [
                { id: 'step-1', percent: 25, msg: 'Generating 5-panel storyboard outline with Gemini Flash...', delay: 300 },
                { id: 'step-2', percent: 50, msg: 'Writing rich dialogue, captions & narration with Gemini Pro...', delay: 2800 },
                { id: 'step-3', percent: 75, msg: 'Rendering visual scene illustrations with Stable Diffusion...', delay: 5600 },
                { id: 'step-4', percent: 92, msg: 'Binding layout records & compiling multi-page PDF...', delay: 9200 }
            ];

            steps.forEach((step, index) => {
                setTimeout(() => {
                    if (loadingMessage) loadingMessage.textContent = step.msg;
                    if (progressBar) progressBar.style.width = `${step.percent}%`;
                    if (progressPercent) progressPercent.textContent = `${step.percent}%`;

                    // Mark previous step completed
                    if (index > 0) {
                        const prevEl = document.getElementById(steps[index - 1].id);
                        if (prevEl) {
                            prevEl.classList.remove('active');
                            prevEl.classList.add('completed');
                        }
                    }
                    const curEl = document.getElementById(step.id);
                    if (curEl) {
                        curEl.classList.add('active');
                    }
                }, step.delay);
            });
        });
    }
});
