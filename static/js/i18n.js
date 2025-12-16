// Internationalization (i18n) support for Fencing Drill
// Supports: Japanese (ja), English (en), French (fr)

const TRANSLATIONS = {
    "ja": {
        // Header
        "header.subtitle": "Training Assistant",
        "header.ready": "準備完了",

        // Mode names
        "mode.basic": "基礎反復",
        "mode.basic.desc": "単一動作の反復練習",
        "mode.combination": "コンビネーション",
        "mode.combination.desc": "パターン練習",
        "mode.random": "ランダム",
        "mode.random.desc": "反応速度トレーニング",
        "mode.interval": "インターバル",
        "mode.interval.desc": "高強度トレーニング",

        // Section headers
        "section.training_mode": "Training Mode",
        "section.settings": "Settings",
        "section.command_ref": "Command Reference",
        "section.weapon": "種目",
        "status.current_mode": "Current Mode:",

        // Weapon selection
        "weapon.foil": "フルーレ",
        "weapon.epee": "エペ",
        "weapon.sabre": "サーブル",
        "weapon.hint": "種目によってテンポとコマンドが自動調整されます",

        // Buttons
        "button.start": "開始",
        "button.stop": "停止",

        // Status
        "status.idle": "設定を確認して「開始」を押してください",
        "status.finished": "終了",

        // Settings - Basic
        "settings.action": "動作",
        "settings.tempo": "テンポ",
        "settings.tempo.slow": "ゆっくり",
        "settings.tempo.fast": "速い",
        "settings.reps": "反復回数",
        "settings.reps.times": "回",

        // Settings - Random
        "settings.level": "レベル",
        "settings.level.beginner": "初級（マルシェ、ロンペ）",
        "settings.level.intermediate": "中級（+ ファンドゥ、ルミーズ）",
        "settings.level.advanced": "上級（+ ボンナバン、ボンナリエール、バランセ）",
        "settings.duration": "練習時間",
        "settings.min_interval": "最小間隔",
        "settings.max_interval": "最大間隔",

        // Settings - Combination
        "settings.pattern": "パターン",
        "settings.pattern.a": "A: 前進攻撃",
        "settings.pattern.b": "B: 後退からの反撃",
        "settings.pattern.c": "C: フットワーク強化",

        // Settings - Interval
        "settings.high_intensity": "高強度時間",
        "settings.rest_time": "休憩時間",
        "settings.sets": "セット数",
        "settings.sets.suffix": "セット",

        // Commands - these are local names (not French pronunciation)
        "command.en_garde": "アンギャルド",
        "command.en_garde.desc": "構え",
        "command.marche": "マルシェ",
        "command.marche.desc": "前進",
        "command.rompe": "ロンペ",
        "command.rompe.desc": "後退",
        "command.fendez": "ファンドゥ",
        "command.fendez.desc": "突き",
        "command.allongez": "アロンジェ",
        "command.allongez.desc": "腕",
        "command.remise": "ルミーズ",
        "command.remise.desc": "戻し",
        "command.bond_avant": "ボンナバン",
        "command.bond_avant.desc": "跳躍前進",
        "command.bond_arriere": "ボンナリエール",
        "command.bond_arriere.desc": "跳躍後退",
        "command.balancez": "バランセ",
        "command.balancez.desc": "揺れ動作",
        "command.double_marche": "ドゥブル・マルシェ",
        "command.double_marche.desc": "二歩前進",
        "command.fleche": "フレッシュ",
        "command.fleche.desc": "走り突き",
        "command.rest": "ルポ",
        "command.rest.desc": "休憩",

        // Command options in settings
        "command.option.marche": "マルシェ（前進）",
        "command.option.rompe": "ロンペ（後退）",
        "command.option.fendez": "ファンドゥ（突き）",
        "command.option.bond_avant": "ボンナバン（跳躍前進）",
        "command.option.bond_arriere": "ボンナリエール（跳躍後退）",

        // Units
        "unit.bpm": "BPM",
        "unit.seconds": "秒",
        "unit.minutes": "分",
    },
    "en": {
        // Header
        "header.subtitle": "Training Assistant",
        "header.ready": "Ready",

        // Mode names
        "mode.basic": "Basic",
        "mode.basic.desc": "Single action repetition",
        "mode.combination": "Combination",
        "mode.combination.desc": "Pattern practice",
        "mode.random": "Random",
        "mode.random.desc": "Reaction speed training",
        "mode.interval": "Interval",
        "mode.interval.desc": "High intensity training",

        // Section headers
        "section.training_mode": "Training Mode",
        "section.settings": "Settings",
        "section.command_ref": "Command Reference",
        "section.weapon": "Weapon",
        "status.current_mode": "Current Mode:",

        // Weapon selection
        "weapon.foil": "Foil",
        "weapon.epee": "Épée",
        "weapon.sabre": "Sabre",
        "weapon.hint": "Tempo and commands adjust automatically by weapon",

        // Buttons
        "button.start": "Start",
        "button.stop": "Stop",

        // Status
        "status.idle": "Check settings and press \"Start\"",
        "status.finished": "Finished",

        // Settings - Basic
        "settings.action": "Action",
        "settings.tempo": "Tempo",
        "settings.tempo.slow": "Slow",
        "settings.tempo.fast": "Fast",
        "settings.reps": "Repetitions",
        "settings.reps.times": "times",

        // Settings - Random
        "settings.level": "Level",
        "settings.level.beginner": "Beginner (Marche, Rompe)",
        "settings.level.intermediate": "Intermediate (+ Fendez, Remise)",
        "settings.level.advanced": "Advanced (+ Bond avant, Bond arrière, Balancez)",
        "settings.duration": "Duration",
        "settings.min_interval": "Min interval",
        "settings.max_interval": "Max interval",

        // Settings - Combination
        "settings.pattern": "Pattern",
        "settings.pattern.a": "A: Forward attack",
        "settings.pattern.b": "B: Counter from retreat",
        "settings.pattern.c": "C: Footwork drill",

        // Settings - Interval
        "settings.high_intensity": "High intensity",
        "settings.rest_time": "Rest time",
        "settings.sets": "Sets",
        "settings.sets.suffix": "sets",

        // Commands - English descriptions
        "command.en_garde": "En garde",
        "command.en_garde.desc": "Guard",
        "command.marche": "Advance",
        "command.marche.desc": "Forward",
        "command.rompe": "Retreat",
        "command.rompe.desc": "Back",
        "command.fendez": "Lunge",
        "command.fendez.desc": "Thrust",
        "command.allongez": "Extend",
        "command.allongez.desc": "Arm",
        "command.remise": "Recover",
        "command.remise.desc": "Return",
        "command.bond_avant": "Jump forward",
        "command.bond_avant.desc": "Leap fwd",
        "command.bond_arriere": "Jump back",
        "command.bond_arriere.desc": "Leap back",
        "command.balancez": "Balancez",
        "command.balancez.desc": "Sway",
        "command.double_marche": "Double advance",
        "command.double_marche.desc": "Two steps",
        "command.fleche": "Flèche",
        "command.fleche.desc": "Running attack",
        "command.rest": "Rest",
        "command.rest.desc": "Rest",

        // Command options in settings
        "command.option.marche": "Advance (forward)",
        "command.option.rompe": "Retreat (back)",
        "command.option.fendez": "Lunge (thrust)",
        "command.option.bond_avant": "Jump forward (leap)",
        "command.option.bond_arriere": "Jump back (leap)",

        // Units
        "unit.bpm": "BPM",
        "unit.seconds": "sec",
        "unit.minutes": "min",
    },
    "fr": {
        // Header
        "header.subtitle": "Assistant d'entraînement",
        "header.ready": "Prêt",

        // Mode names
        "mode.basic": "Basique",
        "mode.basic.desc": "Répétition d'un mouvement",
        "mode.combination": "Combinaison",
        "mode.combination.desc": "Pratique de patterns",
        "mode.random": "Aléatoire",
        "mode.random.desc": "Entraînement de réactivité",
        "mode.interval": "Intervalle",
        "mode.interval.desc": "Entraînement haute intensité",

        // Section headers
        "section.training_mode": "Mode d'entraînement",
        "section.settings": "Paramètres",
        "section.command_ref": "Référence des commandes",
        "section.weapon": "Arme",
        "status.current_mode": "Mode actuel :",

        // Weapon selection
        "weapon.foil": "Fleuret",
        "weapon.epee": "Épée",
        "weapon.sabre": "Sabre",
        "weapon.hint": "Le tempo et les commandes s'ajustent selon l'arme",

        // Buttons
        "button.start": "Démarrer",
        "button.stop": "Arrêter",

        // Status
        "status.idle": "Vérifiez les paramètres et appuyez sur « Démarrer »",
        "status.finished": "Terminé",

        // Settings - Basic
        "settings.action": "Action",
        "settings.tempo": "Tempo",
        "settings.tempo.slow": "Lent",
        "settings.tempo.fast": "Rapide",
        "settings.reps": "Répétitions",
        "settings.reps.times": "fois",

        // Settings - Random
        "settings.level": "Niveau",
        "settings.level.beginner": "Débutant (Marchez, Rompez)",
        "settings.level.intermediate": "Intermédiaire (+ Fendez, Remise)",
        "settings.level.advanced": "Avancé (+ Bond en avant, Bond en arrière, Balancez)",
        "settings.duration": "Durée",
        "settings.min_interval": "Intervalle min",
        "settings.max_interval": "Intervalle max",

        // Settings - Combination
        "settings.pattern": "Pattern",
        "settings.pattern.a": "A : Attaque en avançant",
        "settings.pattern.b": "B : Contre-attaque en reculant",
        "settings.pattern.c": "C : Travail de jambes",

        // Settings - Interval
        "settings.high_intensity": "Haute intensité",
        "settings.rest_time": "Temps de repos",
        "settings.sets": "Séries",
        "settings.sets.suffix": "séries",

        // Commands - French (same as fencing terminology)
        "command.en_garde": "En garde",
        "command.en_garde.desc": "Garde",
        "command.marche": "Marchez",
        "command.marche.desc": "Avant",
        "command.rompe": "Rompez",
        "command.rompe.desc": "Arrière",
        "command.fendez": "Fendez",
        "command.fendez.desc": "Fente",
        "command.allongez": "Allongez",
        "command.allongez.desc": "Bras",
        "command.remise": "Remise",
        "command.remise.desc": "Retour",
        "command.bond_avant": "Bond en avant",
        "command.bond_avant.desc": "Saut avant",
        "command.bond_arriere": "Bond en arrière",
        "command.bond_arriere.desc": "Saut arrière",
        "command.balancez": "Balancez",
        "command.balancez.desc": "Balancer",
        "command.double_marche": "Double marchez",
        "command.double_marche.desc": "Deux pas",
        "command.fleche": "Flèche",
        "command.fleche.desc": "Attaque en courant",
        "command.rest": "Repos",
        "command.rest.desc": "Repos",

        // Command options in settings
        "command.option.marche": "Marchez (avancer)",
        "command.option.rompe": "Rompez (reculer)",
        "command.option.fendez": "Fendez (fente)",
        "command.option.bond_avant": "Bond en avant (saut)",
        "command.option.bond_arriere": "Bond en arrière (saut)",

        // Units
        "unit.bpm": "BPM",
        "unit.seconds": "sec",
        "unit.minutes": "min",
    }
};

// Default language
const DEFAULT_LANG = 'ja';
const STORAGE_KEY = 'fencing-drill-lang';

/**
 * Detect browser language and return supported language code
 * @returns {string} Language code (ja, en, or fr)
 */
function detectBrowserLang() {
    const browserLang = navigator.language || navigator.userLanguage;
    const langCode = browserLang.split('-')[0].toLowerCase();

    if (TRANSLATIONS[langCode]) {
        return langCode;
    }
    return 'en'; // Fallback to English
}

/**
 * Get current language from localStorage or detect from browser
 * @returns {string} Language code (ja, en, or fr)
 */
function getCurrentLang() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && TRANSLATIONS[stored]) {
        return stored;
    }
    const detected = detectBrowserLang();
    localStorage.setItem(STORAGE_KEY, detected);
    return detected;
}

/**
 * Set current language and save to localStorage
 * @param {string} lang - Language code (ja, en, or fr)
 */
function setCurrentLang(lang) {
    if (TRANSLATIONS[lang]) {
        localStorage.setItem(STORAGE_KEY, lang);
    }
}

/**
 * Get translation for a key
 * @param {string} key - Translation key (e.g., "mode.basic")
 * @param {string} lang - Language code (optional, uses current if not specified)
 * @returns {string} Translated text or key if not found
 */
function t(key, lang = null) {
    const currentLang = lang || getCurrentLang();
    const translations = TRANSLATIONS[currentLang] || TRANSLATIONS[DEFAULT_LANG];
    return translations[key] || key;
}

/**
 * Apply translations to all elements with data-i18n attribute
 * @param {string} lang - Language code (optional, uses current if not specified)
 */
function applyTranslations(lang = null) {
    const currentLang = lang || getCurrentLang();
    const translations = TRANSLATIONS[currentLang] || TRANSLATIONS[DEFAULT_LANG];

    // Translate elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key]) {
            element.textContent = translations[key];
        }
    });

    // Translate elements with data-i18n-placeholder attribute
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        if (translations[key]) {
            element.placeholder = translations[key];
        }
    });

    // Update modeLabels JavaScript object
    if (typeof modeLabels !== 'undefined') {
        modeLabels.basic = translations['mode.basic'] || modeLabels.basic;
        modeLabels.combination = translations['mode.combination'] || modeLabels.combination;
        modeLabels.random = translations['mode.random'] || modeLabels.random;
        modeLabels.interval = translations['mode.interval'] || modeLabels.interval;
    }

    // Update current mode label if exists
    const currentModeLabel = document.getElementById('current-mode-label');
    if (currentModeLabel && typeof currentMode !== 'undefined' && typeof modeLabels !== 'undefined') {
        currentModeLabel.textContent = modeLabels[currentMode];
    }

    // Update html lang attribute
    document.documentElement.lang = currentLang;

    // Update language selector if exists
    const langSelector = document.getElementById('language-selector');
    if (langSelector) {
        langSelector.value = currentLang;
    }
}

/**
 * Initialize i18n on page load
 */
function initI18n() {
    const lang = getCurrentLang();

    // Apply translations on load
    applyTranslations(lang);

    // Set up language selector event listener
    const langSelector = document.getElementById('language-selector');
    if (langSelector) {
        langSelector.value = lang;
        langSelector.addEventListener('change', function() {
            setCurrentLang(this.value);
            applyTranslations(this.value);
        });
    }

    // Re-apply translations after htmx content swaps
    document.body.addEventListener('htmx:afterSwap', function() {
        applyTranslations();
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initI18n);
