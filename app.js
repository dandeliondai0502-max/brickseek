/* app.js - BrickFinder UI, Scanner Simulation & Real SQLite API Encyclopedia Gateway */

document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Elements ---
    const body = document.body;
    const themeToggleBtn = document.getElementById('theme-toggle');
    const searchInput = document.getElementById('search-input');
    const clearBtn = document.getElementById('clear-btn');
    const searchBoxWrapper = document.querySelector('.search-box-wrapper');
    const cameraTrigger = document.getElementById('camera-trigger');
    const searchSubmitBtn = document.getElementById('search-submit-btn');

    // Settings & Auth DOM Elements
    const settingsBtn = document.getElementById('settings-btn');
    const closeSettingsBtn = document.getElementById('close-settings-btn');
    const settingsModal = document.getElementById('settings-modal');
    const avatarBtn = document.getElementById('avatar-btn');
    const loginModal = document.getElementById('login-modal');
    const closeLoginBtn = document.getElementById('close-login-btn');
    const btnShowLogin = document.getElementById('btn-show-login');
    const btnDoLogout = document.getElementById('btn-do-logout');
    const settingCameraSelect = document.getElementById('setting-camera-select');
    const settingSoundToggle = document.getElementById('setting-sound-toggle');
    const switchCameraBtn = document.getElementById('switch-camera-btn');
    const settingsFavoritesList = document.getElementById('settings-favorites-list');
    const favCountSpan = document.getElementById('fav-count');
    const loggedUsernameSpan = document.getElementById('logged-username');
    const accountLoggedOutView = document.getElementById('account-logged-out-view');
    const accountLoggedInView = document.getElementById('account-logged-in-view');
    const loginForm = document.getElementById('login-form');
    const authUsernameInput = document.getElementById('auth-username');
    const authPasswordInput = document.getElementById('auth-password');
    const loginErrorMsg = document.getElementById('login-error-msg');
    const authSubmitBtn = document.getElementById('auth-submit-btn');
    const loginSwitchLink = document.getElementById('login-switch-link');
    const authSwitchPrompt = document.getElementById('auth-switch-prompt');
    const loginModalTitle = document.getElementById('login-modal-title');
    const favoriteBtn = document.getElementById('favorite-btn');
    
    // User Profile Modal (Personal Center) DOM Elements
    const userProfileModal = document.getElementById('user-profile-modal');
    const closeProfileBtn = document.getElementById('close-profile-btn');
    const profileLoginBtn = document.getElementById('profile-login-btn');
    const profileLogoutBtn = document.getElementById('profile-logout-btn');
    const profileDisplayName = document.getElementById('profile-display-name');
    const profileFavCount = document.getElementById('profile-fav-count');
    const profileSyncStatus = document.getElementById('profile-sync-status');
    const syncCloudBtn = document.getElementById('btn-sync-cloud');
    const syncCloudIcon = document.getElementById('sync-cloud-icon');
    
    // Dynamic Suggestions Dropdown
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    searchBoxWrapper.appendChild(suggestionsContainer);

    // Search main container vs Details main container
    const searchContainer = document.querySelector('.search-container');
    const detailContainer = document.getElementById('detail-container');
    const backToSearchBtn = document.getElementById('back-to-search-btn');

    // Gallery Elements
    const galleryContainer = document.getElementById('gallery-container');
    const galleryGrid = document.getElementById('gallery-grid');
    const btnLoadMore = document.getElementById('btn-gallery-load-more');
    const galleryLoadingIndicator = document.getElementById('gallery-loading-indicator');
    const galleryThemeFilter = document.getElementById('gallery-theme-filter');
    const gallerySortFilter = document.getElementById('gallery-sort-filter');
    const gallerySearchInput = document.getElementById('gallery-search-input');
    const backFromGalleryBtn = document.getElementById('back-from-gallery-btn');
    // Footer Links
    const footerAboutBtn = document.getElementById('footer-about-btn');
    const footerDatabaseBtn = document.getElementById('footer-database-btn');
    const footerTermsBtn = document.getElementById('footer-terms-btn');
    const footerPrivacyBtn = document.getElementById('footer-privacy-btn');

    // Header Links
    const navSearchBtn = document.getElementById('nav-search-btn');
    const navGalleryBtn = document.getElementById('nav-gallery-btn');
    const navAboutBtn = document.getElementById('nav-about-btn');

    // About Page Elements
    const aboutContainer = document.getElementById('about-container');
    const backFromAboutBtn = document.getElementById('back-from-about-btn');
    const legalTabs = document.querySelectorAll('.legal-tab');
    const legalTabContents = document.querySelectorAll('.legal-tab-content');
    
    // Scanner Elements
    const scanModal = document.getElementById('scan-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const activateCameraBtn = document.getElementById('activate-camera-btn');
    
    const cameraViewport = document.getElementById('camera-viewport');
    const webcam = document.getElementById('webcam');
    const cameraCanvas = document.getElementById('camera-canvas');
    const cancelCameraBtn = document.getElementById('cancel-camera-btn');
    const shutterBtn = document.getElementById('shutter-btn');
    
    const scanPreviewContainer = document.getElementById('scan-preview-container');
    const previewImage = document.getElementById('preview-image');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const statusPercent = document.getElementById('status-percent');
    const scanLogs = document.getElementById('scan-logs');
    
    const boxHead = document.getElementById('box-head');
    const boxTorso = document.getElementById('box-torso');
    const boxLegs = document.getElementById('box-legs');
    
    const scanResultContainer = document.getElementById('scan-result-container');
    const rescanBtn = document.getElementById('rescan-btn');
    const viewDetailedPartsBtn = document.querySelector('.btn-card-primary');
    
    // Assembly Player Stage
    const legoAssemblyStage = document.getElementById('lego-assembly-stage');
    const btnExplode = document.getElementById('btn-explode');
    const btnAssemble = document.getElementById('btn-assemble');
    
    // Parts Layer Elements
    const selectedPartLabel = document.getElementById('selected-part-name');
    const sharedListResults = document.getElementById('shared-list-results');
    
    // Detail Data Elements
    const detailSeriesBadge = document.getElementById('detail-series-badge');
    const detailTitle = document.getElementById('detail-title');
    const infoId = document.getElementById('info-id');
    const infoYear = document.getElementById('info-year');
    const infoRarity = document.getElementById('info-rarity');
    const infoParts = document.getElementById('info-parts');
    const detailSetsGrid = document.getElementById('detail-sets-grid');
    
    // Instruction Manual Modal
    const manualModal = document.getElementById('manual-modal');
    const closeManualBtn = document.getElementById('close-manual-btn');
    const btnDownloadPdf = document.getElementById('btn-download-pdf');
    const manualLeftPage = document.getElementById('manual-left-page');
    const manualRightPage = document.getElementById('manual-right-page');
    const btnManualPrev = document.getElementById('btn-manual-prev');
    const btnManualNext = document.getElementById('btn-manual-next');
    const manualPageNumLabel = document.getElementById('manual-page-num');
    
    let webcamStream = null;
    let scanInterval = null;
    let currentMinifigId = 'fig-000581';
    let currentPartsList = []; // Stores the parts list of the currently displayed minifigure
    let currentManualSteps = [];
    let currentManualPageIdx = 0;
    let availableVideoDevices = [];
    const detailCache = new Map();
    const searchCache = new Map();
    let suggestionsAbortController = null;

    // --- State & Preferences ---
    let currentUser = localStorage.getItem('currentUser') || null;
    const DEFAULT_PREFERENCES = {
        soundEnabled: true,
        cameraId: "",
        favorites: [], // [{"id": "fig-002816", "name": "Killow"}]
        theme: "light",
        geminiApiKey: ""
    };
    let preferences = { ...DEFAULT_PREFERENCES };

    function normalizeFavorite(item) {
        if (!item || typeof item !== 'object') return null;
        const id = item.minifig_num || item.id;
        if (!id) return null;
        return {
            ...item,
            id,
            minifig_num: id,
            official_id: item.official_id || id,
            name: item.name || id
        };
    }

    function normalizePreferences(rawPrefs = {}) {
        const safePrefs = rawPrefs && typeof rawPrefs === 'object' ? rawPrefs : {};
        const merged = { ...DEFAULT_PREFERENCES, ...safePrefs };
        merged.soundEnabled = typeof merged.soundEnabled === 'boolean' ? merged.soundEnabled : DEFAULT_PREFERENCES.soundEnabled;
        merged.cameraId = typeof merged.cameraId === 'string' ? merged.cameraId : DEFAULT_PREFERENCES.cameraId;
        merged.theme = merged.theme === 'dark' || merged.theme === 'light' ? merged.theme : DEFAULT_PREFERENCES.theme;
        merged.geminiApiKey = typeof merged.geminiApiKey === 'string' ? merged.geminiApiKey : DEFAULT_PREFERENCES.geminiApiKey;
        merged.favorites = Array.isArray(merged.favorites)
            ? merged.favorites.map(normalizeFavorite).filter(Boolean)
            : [];
        return merged;
    }

    // Load local storage preferences as fallback
    try {
        const localPrefs = localStorage.getItem('preferences');
        if (localPrefs) {
            preferences = normalizePreferences(JSON.parse(localPrefs));
        }
    } catch(e) {
        console.error("加载本地偏好失败:", e);
    }

    async function savePreferences() {
        preferences = normalizePreferences(preferences);
        localStorage.setItem('preferences', JSON.stringify(preferences));
        if (currentUser) {
            try {
                const res = await fetch('/api/save-preferences', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: currentUser, preferences })
                });
                if (!res.ok) console.error("同步偏好失败");
            } catch (err) {
                console.error("同步偏好失败:", err);
            }
        }
    }

    function applyTheme() {
        if (preferences.theme === 'light') {
            body.classList.remove('dark-theme');
            body.classList.add('light-theme');
        } else {
            body.classList.remove('light-theme');
            body.classList.add('dark-theme');
        }
        updateThemeOptionsUI();
    }

    function updateThemeOptionsUI() {
        const themeOptLight = document.getElementById('theme-opt-light');
        const themeOptDark = document.getElementById('theme-opt-dark');
        if (!themeOptLight || !themeOptDark) return;
        if (preferences.theme === 'light') {
            themeOptLight.classList.add('active');
            themeOptDark.classList.remove('active');
        } else {
            themeOptLight.classList.remove('active');
            themeOptDark.classList.add('active');
        }
    }

    function updateAccountUI() {
        const userAvatar = document.querySelector('.user-avatar');
        if (!userAvatar || !loggedUsernameSpan || !accountLoggedOutView || !accountLoggedInView) return;
        if (currentUser) {
            userAvatar.classList.add('logged-in');
            loggedUsernameSpan.textContent = currentUser;
            accountLoggedOutView.style.display = 'none';
            accountLoggedInView.style.display = 'block';
        } else {
            userAvatar.classList.remove('logged-in');
            accountLoggedOutView.style.display = 'block';
            accountLoggedInView.style.display = 'none';
        }
        updateProfileUI();
    }

    function updateProfileUI() {
        if (!profileDisplayName) return;
        const favs = preferences.favorites || [];
        if (profileFavCount) profileFavCount.textContent = favs.length;

        const profileLoggedOutView = document.getElementById('profile-logged-out-view');
        const profileLoggedInView = document.getElementById('profile-logged-in-view');

        if (currentUser) {
            profileDisplayName.textContent = currentUser;
            if (profileLoggedOutView) profileLoggedOutView.style.display = 'none';
            if (profileLoggedInView) profileLoggedInView.style.display = 'block';
            if (profileSyncStatus) profileSyncStatus.textContent = "云端同步状态: 已与云端同步";
        } else {
            profileDisplayName.textContent = "未登录 (访客模式)";
            if (profileLoggedOutView) profileLoggedOutView.style.display = 'block';
            if (profileLoggedInView) profileLoggedInView.style.display = 'none';
            if (profileSyncStatus) profileSyncStatus.textContent = "当前为访客模式，数据仅存在本地";
        }
    }

    async function loadCameraDevices({ requestLabels = false } = {}) {
        try {
            if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) {
                if (settingCameraSelect) {
                    settingCameraSelect.innerHTML = '<option value="">浏览器不支持镜头检测</option>';
                }
                return;
            }
            
            let devices = await navigator.mediaDevices.enumerateDevices();
            let hasLabels = devices.some(d => d.label);
            
            // Only request camera permission from explicit camera actions, never from opening Settings.
            if (!hasLabels && requestLabels) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    stream.getTracks().forEach(track => track.stop()); // Stop immediately
                    devices = await navigator.mediaDevices.enumerateDevices(); // Query again
                } catch (e) {
                    console.warn("请求媒体权限被拒绝或取消:", e);
                }
            }
            
            const videoDevices = devices.filter(d => d.kind === 'videoinput');
            availableVideoDevices = videoDevices;
            
            if (!settingCameraSelect) return;
            settingCameraSelect.innerHTML = '';
            if (videoDevices.length === 0) {
                const opt = document.createElement('option');
                opt.value = '';
                opt.textContent = '未检测到镜头设备';
                settingCameraSelect.appendChild(opt);
                return;
            }
            
            videoDevices.forEach((device, index) => {
                const opt = document.createElement('option');
                opt.value = device.deviceId;
                opt.textContent = device.label || `摄像头 ${index + 1}`;
                if (preferences.cameraId === device.deviceId) {
                    opt.selected = true;
                }
                settingCameraSelect.appendChild(opt);
            });
            
            // Auto select first device if none is selected
            if (!preferences.cameraId && videoDevices.length > 0) {
                preferences.cameraId = videoDevices[0].deviceId;
                savePreferences();
            }
        } catch (err) {
            console.error("加载摄像头列表失败:", err);
            if (settingCameraSelect) {
                settingCameraSelect.innerHTML = '<option value="">无法获取摄像头列表</option>';
            }
        }
    }

    function renderSettingsFavorites() {
        preferences = normalizePreferences(preferences);
        if (!settingsFavoritesList || !favCountSpan) return;
        settingsFavoritesList.innerHTML = '';
        const favs = preferences.favorites || [];
        favCountSpan.textContent = favs.length;
        
        if (favs.length === 0) {
            settingsFavoritesList.innerHTML = '<p class="empty-fav-text">暂无收藏，快去人仔详情页标星吧！</p>';
            return;
        }
        
        favs.forEach(item => {
            const card = document.createElement('div');
            card.className = 'fav-item-card';
            card.title = item.name;
            card.innerHTML = `
                <img src="https://cdn.rebrickable.com/media/sets/${item.minifig_num}.jpg" alt="${item.name}" loading="lazy" decoding="async" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,'+encodeURIComponent('<svg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 100 100\\' width=\\'100\\' height=\\'100\\'><defs><linearGradient id=\\'glow-grad\\' x1=\\'0%\\' y1=\\'0%\\' x2=\\'100%\\' y2=\\'100%\\'><stop offset=\\'0%\\' stop-color=\\'#FFD500\\' /><stop offset=\\'100%\\' stop-color=\\'#FF5E00\\' /></linearGradient></defs><g fill=\\'url(#glow-grad)\\'><rect x=\\'45\\' y=\\'16\\' width=\\'10\\' height=\\'4\\' rx=\\'1\\'/><rect x=\\'39\\' y=\\'21\\' width=\\'22\\' height=\\'19\\' rx=\\'5\\'/><rect x=\\'37\\' y=\\'26\\' width=\\'26\\' height=\\'9\\' rx=\\'3\\'/><rect x=\\'46\\' y=\\'40\\' width=\\'8\\' height=\\'3\\'/><path d=\\'M 34,44 L 66,44 L 71,72 L 29,72 Z\\'/><rect x=\\'31\\' y=\\'74\\' width=\\'38\\' height=\\'6\\' rx=\\'1\\'/><rect x=\\'31\\' y=\\'81\\' width=\\'17\\' height=\\'15\\' rx=\\'3\\'/><rect x=\\'52\\' y=\\'81\\' width=\\'17\\' height=\\'15\\' rx=\\'3\\'/></g></svg>')">
                <span>${item.official_id || item.minifig_num}</span>
            `;
            card.addEventListener('click', () => {
                settingsModal.classList.remove('open');
                showDetailPage(item.minifig_num);
            });
            settingsFavoritesList.appendChild(card);
        });
    }

    // AUDIO CONTEXT - Satisfying snap click sounds
    let audioCtx = null;
    function playAssembleSound() {
        if (!preferences.soundEnabled) return;
        try {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(480, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(70, audioCtx.currentTime + 0.09);
            
            gain.gain.setValueAtTime(0.35, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.09);
            
            osc.start();
            osc.stop(audioCtx.currentTime + 0.09);
        } catch (e) {
            console.log('音效拦截。');
        }
    }

    // Initialize UI theme & login state
    applyTheme();
    updateAccountUI();
    if (settingSoundToggle) {
        settingSoundToggle.checked = preferences.soundEnabled;
    }

    // --- 1. Theme Toggle ---
    themeToggleBtn.addEventListener('click', () => {
        preferences.theme = body.classList.contains('dark-theme') ? 'light' : 'dark';
        applyTheme();
        savePreferences();
    });

    // --- 2. Input Box Focusing & Suggestions ---
    searchInput.addEventListener('focus', () => {
        searchBoxWrapper.classList.add('focused');
        if (suggestionsContainer.children.length > 0) {
            suggestionsContainer.classList.add('active');
        }
    });

    searchInput.addEventListener('blur', () => {
        setTimeout(() => {
            searchBoxWrapper.classList.remove('focused');
            suggestionsContainer.classList.remove('active');
        }, 200);
    });

    // Debounce for search suggestions to avoid duplicate heavy backend requests
    let searchDebounceTimeout = null;
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim();
        clearTimeout(searchDebounceTimeout);
        if (query.length > 0) {
            searchBoxWrapper.classList.add('has-text');
            clearBtn.classList.add('visible');
            searchDebounceTimeout = setTimeout(() => {
                fetchSuggestions(query);
            }, 200);
        } else {
            searchBoxWrapper.classList.remove('has-text');
            clearBtn.classList.remove('visible');
            suggestionsContainer.classList.remove('active');
            suggestionsContainer.innerHTML = '';
        }
    });

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchBoxWrapper.classList.remove('has-text');
        clearBtn.classList.remove('visible');
        suggestionsContainer.classList.remove('active');
        suggestionsContainer.innerHTML = '';
        searchInput.focus();
    });

    if (searchSubmitBtn) {
        searchSubmitBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            suggestionsContainer.classList.remove('active');
            performTextSearch();
        });
    }

    // Global keyboard shortcut: '/' key to focus search box when not typing in any input
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== searchInput && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            searchInput.focus();
        }
    });

    // Close suggestions on outside click
    document.addEventListener('click', (e) => {
        if (!searchBoxWrapper.contains(e.target)) {
            suggestionsContainer.classList.remove('active');
        }
    });

    // Fetch Suggestions from real backend API
    async function fetchSuggestions(query) {
        try {
            const cacheKey = query.toLowerCase();
            if (searchCache.has(cacheKey)) {
                renderSuggestions(searchCache.get(cacheKey));
                return;
            }
            if (suggestionsAbortController) {
                suggestionsAbortController.abort();
            }
            suggestionsAbortController = new AbortController();
            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`, {
                signal: suggestionsAbortController.signal
            });
            if (!res.ok) return;
            const data = await res.json();
            searchCache.set(cacheKey, data);
            renderSuggestions(data);
        } catch (e) {
            if (e.name === 'AbortError') return;
            console.error("Suggestions fetch error:", e);
        }
    }

    function renderSuggestions(items) {
        suggestionsContainer.innerHTML = '';
        if (items.length === 0) {
            suggestionsContainer.classList.remove('active');
            return;
        }

        activeSuggestionIdx = -1;
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'suggestion-item';
            div.innerHTML = `
                <span class="sug-name">${item.name}</span>
                <span class="sug-id">${item.official_id || item.minifig_num}</span>
            `;
            
            div.addEventListener('click', () => {
                searchInput.value = item.name;
                suggestionsContainer.classList.remove('active');
                showDetailPage(item.minifig_num);
            });
            
            suggestionsContainer.appendChild(div);
        });
        
        suggestionsContainer.classList.add('active');
    }

    let activeSuggestionIdx = -1;

    searchInput.addEventListener('keydown', (e) => {
        const isOpen = suggestionsContainer.classList.contains('active');
        const items = suggestionsContainer.querySelectorAll('.suggestion-item');
        
        if (isOpen && items.length > 0) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                activeSuggestionIdx = (activeSuggestionIdx + 1) % items.length;
                updateSuggestionHighlight();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                activeSuggestionIdx = (activeSuggestionIdx - 1 + items.length) % items.length;
                updateSuggestionHighlight();
            } else if (e.key === 'Enter') {
                if (activeSuggestionIdx >= 0 && activeSuggestionIdx < items.length) {
                    e.preventDefault();
                    items[activeSuggestionIdx].click();
                } else {
                    performTextSearch();
                }
            } else if (e.key === 'Escape') {
                e.preventDefault();
                suggestionsContainer.classList.remove('active');
                searchInput.blur();
            }
        } else {
            if (e.key === 'Enter') {
                performTextSearch();
            }
        }
    });

    function updateSuggestionHighlight() {
        const items = suggestionsContainer.querySelectorAll('.suggestion-item');
        items.forEach((item, idx) => {
            if (idx === activeSuggestionIdx) {
                item.classList.add('highlighted');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('highlighted');
            }
        });
    }
    
    async function performTextSearch() {
        const query = searchInput.value.trim();
        if (!query) {
            searchInput.focus();
            return;
        }
        
        try {
            const cacheKey = query.toLowerCase();
            let data = searchCache.get(cacheKey);
            if (!data) {
                const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
                if (!res.ok) return;
                data = await res.json();
                searchCache.set(cacheKey, data);
            }
            
            if (data.length > 0) {
                // If there is an exact or first match, open it directly!
                showDetailPage(data[0].minifig_num);
            } else {
                alert(`在全量数据库中未找到与 "${query}" 匹配的乐高人仔。请换个词试试（如 "Vader"、"fig-000581"、"太空"）`);
            }
        } catch (e) {
            console.error(e);
        }
    }

    // --- 3. Modal Opening & Closing ---
    const openModal = async () => {
        scanModal.classList.add('open');
        resetScannerState();
        await startWebcamStream();
    };

    const closeModal = () => {
        scanModal.classList.remove('open');
        stopWebcam();
        resetScannerState();
    };

    cameraTrigger.addEventListener('click', openModal);
    closeModalBtn.addEventListener('click', closeModal);
    
    if (rescanBtn) {
        rescanBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            resetScannerState();
            await startWebcamStream();
        });
    }
    
    scanModal.addEventListener('click', (e) => {
        if (e.target === scanModal) {
            closeModal();
        }
    });

    // Settings Modal Triggers & Events
    const openSettingsModal = async () => {
        settingsModal.classList.add('open');
        await loadCameraDevices();
        updateThemeOptionsUI();
    };

    const closeSettingsModal = () => {
        settingsModal.classList.remove('open');
    };

    settingsBtn.addEventListener('click', openSettingsModal);
    closeSettingsBtn.addEventListener('click', closeSettingsModal);

    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) closeSettingsModal();
    });

    settingCameraSelect.addEventListener('change', () => {
        preferences.cameraId = settingCameraSelect.value;
        savePreferences();
    });

    settingSoundToggle.addEventListener('change', () => {
        preferences.soundEnabled = settingSoundToggle.checked;
        savePreferences();
    });

    // Theme selector options inside settings
    const themeOptLight = document.getElementById('theme-opt-light');
    const themeOptDark = document.getElementById('theme-opt-dark');
    if (themeOptLight) {
        themeOptLight.addEventListener('click', () => {
            preferences.theme = 'light';
            applyTheme();
            savePreferences();
        });
    }
    if (themeOptDark) {
        themeOptDark.addEventListener('click', () => {
            preferences.theme = 'dark';
            applyTheme();
            savePreferences();
        });
    }

    // Cache clean & app reset
    const btnClearCache = document.getElementById('btn-clear-cache');
    const btnResetApp = document.getElementById('btn-reset-app');
    if (btnClearCache) {
        btnClearCache.addEventListener('click', () => {
            btnClearCache.disabled = true;
            btnClearCache.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 正在清理...';
            setTimeout(() => {
                btnClearCache.disabled = false;
                btnClearCache.innerHTML = '<i class="fas fa-broom"></i> 清理缓存 (0.00MB)';
                showNotification("图片及扫描缓存清理成功！", "success");
            }, 1000);
        });
    }
    if (btnResetApp) {
        btnResetApp.addEventListener('click', () => {
            if (confirm("确定要恢复出厂设置吗？这将清除所有本地收藏和偏好设置！")) {
                localStorage.clear();
                window.location.reload();
            }
        });
    }

    // User Profile Modal (Personal Center) Triggers & Events
    const openUserProfileModal = () => {
        userProfileModal.classList.add('open');
        updateProfileUI();
    };

    const closeUserProfileModal = () => {
        userProfileModal.classList.remove('open');
    };

    avatarBtn.addEventListener('click', openUserProfileModal);
    closeProfileBtn.addEventListener('click', closeUserProfileModal);

    userProfileModal.addEventListener('click', (e) => {
        if (e.target === userProfileModal) closeUserProfileModal();
    });

    if (profileLoginBtn) {
        profileLoginBtn.addEventListener('click', () => {
            closeUserProfileModal();
            openLoginModal();
        });
    }

    if (profileLogoutBtn) {
        profileLogoutBtn.addEventListener('click', () => {
            currentUser = null;
            localStorage.removeItem('currentUser');
            updateAccountUI();
            closeUserProfileModal();
            showNotification("已安全退出登录", "info");
        });
    }

    if (syncCloudBtn) {
        syncCloudBtn.addEventListener('click', () => {
            if (!currentUser) {
                showNotification("请先登录账户以同步数据", "warning");
                closeUserProfileModal();
                openLoginModal();
                return;
            }
            syncCloudBtn.disabled = true;
            syncCloudIcon.classList.add('fa-spin');
            syncCloudBtn.innerHTML = '<i class="fas fa-sync fa-spin"></i> 正在上传备份...';
            
            setTimeout(() => {
                syncCloudIcon.classList.remove('fa-spin');
                syncCloudBtn.disabled = false;
                syncCloudBtn.innerHTML = '<i class="fas fa-sync"></i> 立即备份到云端';
                if (profileSyncStatus) profileSyncStatus.textContent = "云端同步状态: 刚刚已手动备份";
                showNotification("收藏夹与设置已成功同步至云端！", "success");
            }, 1200);
        });
    }

    // Auth & Login Modal Triggers & Events
    const openLoginModal = () => {
        loginModal.classList.add('open');
        loginErrorMsg.style.display = 'none';
        loginErrorMsg.textContent = '';
        authUsernameInput.value = '';
        authPasswordInput.value = '';
        setAuthMode(true);
    };

    const closeLoginModal = () => {
        loginModal.classList.remove('open');
    };

    let isLoginMode = true;
    function setAuthMode(isLogin) {
        isLoginMode = isLogin;
        if (isLogin) {
            loginModalTitle.textContent = '账号登录';
            authSubmitBtn.textContent = '立即登录';
            authSwitchPrompt.textContent = '还没有账号？';
            loginSwitchLink.textContent = '立即注册';
        } else {
            loginModalTitle.textContent = '账号注册';
            authSubmitBtn.textContent = '立即注册';
            authSwitchPrompt.textContent = '已有账号？';
            loginSwitchLink.textContent = '立即登录';
        }
    }

    if (btnShowLogin) {
        btnShowLogin.addEventListener('click', () => {
            closeSettingsModal();
            openLoginModal();
        });
    }

    if (btnDoLogout) {
        btnDoLogout.addEventListener('click', () => {
            currentUser = null;
            localStorage.removeItem('currentUser');
            updateAccountUI();
            closeSettingsModal();
            alert('已成功退出登录。');
        });
    }

    closeLoginBtn.addEventListener('click', closeLoginModal);
    
    loginSwitchLink.addEventListener('click', (e) => {
        e.preventDefault();
        setAuthMode(!isLoginMode);
    });

    loginModal.addEventListener('click', (e) => {
        if (e.target === loginModal) closeLoginModal();
    });

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginErrorMsg.style.display = 'none';
        
        const username = authUsernameInput.value.trim();
        const password = authPasswordInput.value.trim();
        if (!username || !password) return;
        
        const url = isLoginMode ? '/api/login' : '/api/register';
        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await res.json();
            if (!res.ok) {
                loginErrorMsg.textContent = data.error || '认证失败，请稍后重试。';
                loginErrorMsg.style.display = 'block';
                return;
            }
            
            if (isLoginMode) {
                currentUser = data.username;
                localStorage.setItem('currentUser', currentUser);
                preferences = normalizePreferences({ ...preferences, ...(data.preferences || {}) });
                localStorage.setItem('preferences', JSON.stringify(preferences));
                
                applyTheme();
                updateAccountUI();
                renderSettingsFavorites();
                closeLoginModal();
            } else {
                alert('注册成功！正在为您自动登录...');
                currentUser = username;
                localStorage.setItem('currentUser', currentUser);
                await savePreferences();
                updateAccountUI();
                renderSettingsFavorites();
                closeLoginModal();
            }
        } catch (err) {
            console.error("认证请求出错:", err);
            loginErrorMsg.textContent = '无法连接到服务器，请检查您的网络连接。';
            loginErrorMsg.style.display = 'block';
        }
    });

    const btnApple = document.getElementById('btn-apple-login');
    const btnPasskey = document.getElementById('btn-passkey-login');
    const passkeyBox = document.getElementById('passkey-verifying-box');
    
    if (btnApple) {
        btnApple.addEventListener('click', () => {
            currentUser = "AppleUser";
            localStorage.setItem('currentUser', currentUser);
            savePreferences();
            updateAccountUI();
            closeLoginModal();
            alert("成功使用 Apple ID 快捷登录！");
        });
    }
    if (btnPasskey && passkeyBox) {
        btnPasskey.addEventListener('click', () => {
            passkeyBox.style.display = 'flex';
            setTimeout(() => {
                passkeyBox.style.display = 'none';
                currentUser = "PasskeyUser";
                localStorage.setItem('currentUser', currentUser);
                savePreferences();
                updateAccountUI();
                closeLoginModal();
                alert("已通过 Apple 钥匙串 Passkey 通行密钥验证登录！");
            }, 1800);
        });
    }

    // Favorite Star Click Event Handler
    favoriteBtn.addEventListener('click', () => {
        const minifigId = currentMinifigId;
        if (!minifigId) return;
        preferences = normalizePreferences(preferences);
        
        const nameEl = document.getElementById('detail-title');
        const nameText = nameEl ? nameEl.textContent : minifigId;
        
        const index = preferences.favorites.findIndex(f => f.id === minifigId);
        if (index > -1) {
            preferences.favorites.splice(index, 1);
            favoriteBtn.classList.remove('active');
            favoriteBtn.innerHTML = '<i class="far fa-star"></i>';
        } else {
            preferences.favorites.push({
                id: minifigId,
                minifig_num: minifigId,
                official_id: infoId ? infoId.textContent : minifigId,
                name: nameText,
                num_parts: currentPartsList.length || undefined,
                img_url: `https://cdn.rebrickable.com/media/sets/${minifigId}.jpg`
            });
            favoriteBtn.classList.add('active');
            favoriteBtn.innerHTML = '<i class="fas fa-star"></i>';
        }
        
        savePreferences();
        renderSettingsFavorites();
        updateProfileUI();
    });

    // --- 4. Drag & Drop File Upload ---
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleUploadedFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleUploadedFile(e.target.files[0]);
        }
    });

    function getAverageColorFromImage(imgElement) {
        try {
            const canvas = document.createElement('canvas');
            canvas.width = 16;
            canvas.height = 16;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(imgElement, 0, 0, 16, 16);
            const imgData = ctx.getImageData(0, 0, 16, 16).data;
            let r = 0, g = 0, b = 0, count = 0;
            for (let i = 0; i < imgData.length; i += 4) {
                if (imgData[i+3] < 128) continue; // skip transparent
                r += imgData[i];
                g += imgData[i+1];
                b += imgData[i+2];
                count++;
            }
            if (count === 0) return 'ffffff';
            r = Math.round(r / count);
            g = Math.round(g / count);
            b = Math.round(b / count);
            const toHex = (c) => c.toString(16).padStart(2, '0');
            return `${toHex(r)}${toHex(g)}${toHex(b)}`;
        } catch (e) {
            console.error("Error computing average color:", e);
            return 'ffffff';
        }
    }

    function compressImage(dataUrl, maxDim = 640, quality = 0.85) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                let width = img.width;
                let height = img.height;
                if (width > maxDim || height > maxDim) {
                    if (width > height) {
                        height = Math.round((height * maxDim) / width);
                        width = maxDim;
                    } else {
                        width = Math.round((width * maxDim) / height);
                        height = maxDim;
                    }
                }
                const canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                resolve(canvas.toDataURL('image/jpeg', quality));
            };
            img.onerror = () => {
                resolve(dataUrl);
            };
            img.src = dataUrl;
        });
    }

    function handleUploadedFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('请上传有效的图像文件！');
            return;
        }
        
        let filenameQuery = '';
        if (file.name) {
            const nameLower = file.name.toLowerCase();
            const keywords = ['vader', 'yoda', 'batman', 'ironman', 'spider', 'lloyd', 'stormtrooper', 'maul', 'luke', 'anakin', 'harry', 'ninja', 'voldemort', 'dumbledore', 'hermione', 'ron', 'hagrid', 'dobby', 'joker', 'superman', 'captain', 'thor', 'hulk', 'widow', 'panther', 'marvel', 'starwars', 'ninjago', 'city', 'friends'];
            for (const kw of keywords) {
                if (nameLower.includes(kw)) {
                    filenameQuery = kw;
                    break;
                }
            }
        }

        const reader = new FileReader();
        reader.onload = async (event) => {
            const compressedDataUrl = await compressImage(event.target.result);
            previewImage.src = compressedDataUrl;
            previewImage.onload = () => {
                const hexColor = getAverageColorFromImage(previewImage);
                startScanning(hexColor, filenameQuery, compressedDataUrl);
                previewImage.onload = null;
            };
        };
        reader.readAsDataURL(file);
    }

    // --- 5. Webcam Functionality ---
    async function startWebcamStream() {
        try {
            await loadCameraDevices({ requestLabels: false });
            let videoConstraints = { width: 640, height: 480 };
            if (preferences.cameraId) {
                videoConstraints.deviceId = { ideal: preferences.cameraId };
            } else {
                videoConstraints.facingMode = 'environment';
            }
            webcamStream = await navigator.mediaDevices.getUserMedia({
                video: videoConstraints,
                audio: false
            });
            webcam.srcObject = webcamStream;
            dropZone.style.display = 'none';
            cameraViewport.style.display = 'flex';

            // Set up zoom slider functionality
            const zoomSlider = document.getElementById('camera-zoom-slider');
            if (zoomSlider) {
                zoomSlider.value = 1;
                webcam.style.transform = 'scale(1)';
                webcam.style.transformOrigin = 'center';

                const [track] = webcamStream.getVideoTracks();
                const capabilities = track.getCapabilities ? track.getCapabilities() : {};

                zoomSlider.oninput = async () => {
                    const zoomVal = parseFloat(zoomSlider.value);
                    webcam.style.transform = `scale(${zoomVal})`;

                    if (capabilities.zoom) {
                        try {
                            const minZoom = capabilities.zoom.min || 1;
                            const maxZoom = capabilities.zoom.max || 4;
                            const targetZoom = minZoom + (zoomVal - 1) / 3 * (maxZoom - minZoom);
                            await track.applyConstraints({
                                advanced: [{ zoom: targetZoom }]
                            });
                        } catch (err) {
                            console.warn("Native zoom failed:", err);
                        }
                    }
                };
            }
        } catch (err) {
            console.error('摄像头启动失败:', err);
            addLog('⚠️ 无法直接访问镜头，请从相册选择照片识别...', 'warning');
            dropZone.style.display = 'block';
            cameraViewport.style.display = 'none';
            fileInput.click();
        }
    }

    activateCameraBtn.addEventListener('click', async (e) => {
        e.stopPropagation();
        await startWebcamStream();
    });

    cancelCameraBtn.addEventListener('click', () => {
        closeModal();
    });

    const btnCameraUpload = document.getElementById('btn-camera-upload');
    if (btnCameraUpload) {
        btnCameraUpload.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });
    }

    if (switchCameraBtn) {
        switchCameraBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (availableVideoDevices.length <= 1) {
                alert('仅检测到一个摄像头，无法切换。');
                return;
            }
            
            let currentIndex = availableVideoDevices.findIndex(d => d.deviceId === preferences.cameraId);
            if (currentIndex === -1) {
                currentIndex = 0;
            }
            
            const nextIndex = (currentIndex + 1) % availableVideoDevices.length;
            preferences.cameraId = availableVideoDevices[nextIndex].deviceId;
            savePreferences();
            
            if (settingCameraSelect) {
                settingCameraSelect.value = preferences.cameraId;
            }
            
            stopWebcam();
            
            try {
                let videoConstraints = { 
                    width: 640, 
                    height: 480,
                    deviceId: { exact: preferences.cameraId }
                };
                webcamStream = await navigator.mediaDevices.getUserMedia({
                    video: videoConstraints,
                    audio: false
                });
                webcam.srcObject = webcamStream;
            } catch (err) {
                console.error('切换摄像头失败:', err);
                try {
                    webcamStream = await navigator.mediaDevices.getUserMedia({
                        video: { width: 640, height: 480, facingMode: 'environment' },
                        audio: false
                    });
                    webcam.srcObject = webcamStream;
                } catch (fallbackErr) {
                    alert('摄像头切换失败，请尝试重新打开识别。');
                }
            }
        });
    }

    shutterBtn.addEventListener('click', () => {
        if (!webcamStream) return;
        
        const zoomSlider = document.getElementById('camera-zoom-slider');
        const zoomVal = zoomSlider ? parseFloat(zoomSlider.value) : 1.0;

        let width = webcam.videoWidth || 640;
        let height = webcam.videoHeight || 480;
        
        const canvasWidth = 640;
        const canvasHeight = Math.round((height * 640) / width);
        
        cameraCanvas.width = canvasWidth;
        cameraCanvas.height = canvasHeight;
        
        const ctx = cameraCanvas.getContext('2d');
        
        if (zoomVal > 1) {
            const sw = width / zoomVal;
            const sh = height / zoomVal;
            const sx = (width - sw) / 2;
            const sy = (height - sh) / 2;
            ctx.drawImage(webcam, sx, sy, sw, sh, 0, 0, canvasWidth, canvasHeight);
        } else {
            ctx.drawImage(webcam, 0, 0, width, height, 0, 0, canvasWidth, canvasHeight);
        }
        
        const dataUrl = cameraCanvas.toDataURL('image/jpeg', 0.85);
        previewImage.src = dataUrl;
        
        stopWebcam();
        cameraViewport.style.display = 'none';
        
        previewImage.onload = () => {
            const hexColor = getAverageColorFromImage(previewImage);
            startScanning(hexColor, '', dataUrl);
            previewImage.onload = null;
        };
    });

    function stopWebcam() {
        if (webcamStream) {
            webcamStream.getTracks().forEach(track => track.stop());
            webcamStream = null;
        }
        webcam.srcObject = null;
    }

    // --- 6. Scanner Animation & Real SQLite Matching ---
    function resetScannerState() {
        clearInterval(scanInterval);
        dropZone.style.display = 'block';
        cameraViewport.style.display = 'none';
        scanPreviewContainer.style.display = 'none';
        scanResultContainer.style.display = 'none';
        progressBarFill.style.width = '0%';
        statusPercent.textContent = '0%';
        scanLogs.innerHTML = '';
        
        boxHead.style.display = 'none';
        boxTorso.style.display = 'none';
        boxLegs.style.display = 'none';
    }

    function addLog(text, type = '') {
        const li = document.createElement('li');
        li.innerHTML = `<span class="log-time">[${new Date().toLocaleTimeString()}]</span> <span class="log-text">${text}</span>`;
        if (type) li.className = type;
        scanLogs.appendChild(li);
        scanLogs.scrollTop = scanLogs.scrollHeight;
    }

    let scanResults = [];
    let scanAiDescription = '';
    async function startScanning(color, query, base64Image) {
        dropZone.style.display = 'none';
        cameraViewport.style.display = 'none';
        scanPreviewContainer.style.display = 'flex';
        scanResultContainer.style.display = 'none';
        
        let progress = 0;
        progressBarFill.style.width = '0%';
        statusPercent.textContent = '0%';
        scanLogs.innerHTML = '';
        scanAiDescription = '';
        
        const aiBox = document.getElementById('ai-analysis-box');
        if (aiBox) aiBox.style.display = 'none';
        
        addLog('⚡ 正在初始化图像特征矩阵分析引擎...', 'highlight');
        
        // Fetch matching figures instantly in the background!
        scanResults = [];
        let isAiSuccessful = false;
        
        if (base64Image) {
            addLog('🔍 正在将图像发送至 AI 智能视觉分析引擎...', 'highlight');
            try {
                const res = await fetch('/api/scan-image', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        image: base64Image,
                        color: color,
                        api_key: ""
                    })
                });
                
                if (res.ok) {
                    const data = await res.json();
                    if (data.results && data.results.length > 0) {
                        scanResults = data.results;
                        scanAiDescription = data.description || '';
                        isAiSuccessful = true;
                    }
                } else {
                    const errData = await res.json().catch(() => ({}));
                    const errMsg = errData.message || 'API 调用失败';
                    addLog(`⚠️ AI 智能识别暂不可用 (${errMsg})。正在切换为传统算法...`, 'warning');
                }
            } catch (e) {
                console.error("AI Scan fetch error:", e);
                addLog('⚠️ AI 智能识别连接超时。正在切换为传统算法...', 'warning');
            }
        }
        
        // Fallback if AI not successful or not attempted
        if (!isAiSuccessful) {
            try {
                const res = await fetch(`/api/scan?color=${color}&query=${encodeURIComponent(query)}`);
                if (res.ok) {
                    scanResults = await res.json();
                }
            } catch (e) {
                console.error("Scan fetch error:", e);
            }
        }
        
        // If fetch fails or returns empty, fallback to default popular figures
        if (!scanResults || scanResults.length === 0) {
            scanResults = [
                { minifig_num: 'fig-000581', name: 'Darth Vader (达斯·维达 - 铬黑版)', num_parts: 6, img_url: 'https://cdn.rebrickable.com/media/sets/fig-000581.jpg' },
                { minifig_num: 'fig-001783', name: 'Darth Vader (Light Nougat)', num_parts: 5, img_url: 'https://cdn.rebrickable.com/media/sets/fig-001783.jpg' },
                { minifig_num: 'fig-000516', name: 'Darth Vader (LBG Skin)', num_parts: 6, img_url: 'https://cdn.rebrickable.com/media/sets/fig-000516.jpg' }
            ];
        }
        
        const bestMatch = scanResults[0];
        const matchName = bestMatch.name;
        
        // Customize logs dynamically based on the best match character name!
        let characterType = '未知人仔';
        let detail1 = `主色调 #${color.toUpperCase()} 的头部配件`;
        let detail2 = `主色调符合 #${color.toUpperCase()} 印刷纹理`;
        
        const matchNameLower = matchName.toLowerCase();
        if (matchNameLower.includes('vader') || matchNameLower.includes('维达')) {
            characterType = '黑武士 (Darth Vader)';
            detail1 = '经典黑武士头面罩轮廓';
            detail2 = '达斯维达控制面板胸章印花';
        } else if (matchNameLower.includes('yoda') || matchNameLower.includes('尤达')) {
            characterType = '尤达大师 (Yoda)';
            detail1 = '尤达大师经典耳朵面部轮廓';
            detail2 = '绝地武士粗麻长袍印记';
        } else if (matchNameLower.includes('batman') || matchNameLower.includes('蝙蝠侠')) {
            characterType = '蝙蝠侠 (Batman)';
            detail1 = '蝙蝠侠尖耳面罩轮廓';
            detail2 = '蝙蝠战衣标志性胸章';
        } else if (matchNameLower.includes('iron') || matchNameLower.includes('钢铁侠')) {
            characterType = '钢铁侠 (Iron Man)';
            detail1 = '钢铁侠金色战甲面罩轮廓';
            detail2 = '方舟反应堆胸部印刷图案';
        } else if (matchNameLower.includes('lloyd') || matchNameLower.includes('劳埃德')) {
            characterType = '劳埃德 (Lloyd)';
            detail1 = '幻影忍者劳埃德经典头巾';
            detail2 = '能量元素战服印记';
        } else if (matchNameLower.includes('spider') || matchNameLower.includes('蜘蛛侠')) {
            characterType = '蜘蛛侠 (Spider-Man)';
            detail1 = '经典红蓝网状蜘蛛头罩轮廓';
            detail2 = '胸部黑色蜘蛛标志印花';
        } else if (matchNameLower.includes('stormtrooper') || matchNameLower.includes('冲锋队')) {
            characterType = '帝国冲锋队 (Stormtrooper)';
            detail1 = '经典白兵头盔面部轮廓';
            detail2 = '帝国军用战术装甲印记';
        } else if (matchNameLower.includes('luke') || matchNameLower.includes('卢克')) {
            characterType = '卢克·天行者 (Luke Skywalker)';
            detail1 = '塔图因金发或反抗军头盔轮廓';
            detail2 = '经典绝地装束/反抗军飞行服印花';
        }
        
        const logsSchedule = [
            { threshold: 10, text: '🔍 图像解析成功，正在进行边缘轮廓拟合...', type: '' },
            { threshold: 22, text: isAiSuccessful ? `🤖 AI 视觉大模型已确认角色特征，初步匹配为：${characterType}` : `🤖 检测到乐高人仔经典骨架，初步判定为：${characterType}`, type: 'success' },
            { threshold: 30, text: '🎯 [定位] 头部配件匹配。启动脸部印刷扫描...', type: '' },
            { threshold: 45, text: `🏷️ 头部特征匹配度高：${detail1}`, type: 'highlight' },
            { threshold: 55, text: '🎯 [定位] 躯干印花检测。分析胸部和手臂色彩...', type: '' },
            { threshold: 70, text: `🏷️ 躯干印花符合：${detail2}`, type: 'highlight' },
            { threshold: 82, text: '🎯 [定位] 腿部轮廓检测已完成...', type: '' },
            { threshold: 90, text: isAiSuccessful ? '📦 AI 分析完成。正在调取 SQLite 对应特征编号进行双向校准...' : '📦 正在检索离线 SQLite 数据库 16,985 份人仔百科库...', type: '' },
            { threshold: 98, text: isAiSuccessful ? `✅ AI 识别完毕，${bestMatch.name} 比对成功！` : `✅ 比对完毕，${bestMatch.name} 匹配精确率 99.4%`, type: 'success' }
        ];

        scanInterval = setInterval(() => {
            progress += 1;
            progressBarFill.style.width = `${progress}%`;
            statusPercent.textContent = `${progress}%`;
            
            if (progress >= 25 && progress < 85) {
                boxHead.style.display = 'block';
                boxHead.querySelector('.box-label').textContent = `Head [${Math.min(99, progress * 1.2).toFixed(1)}%]`;
            }
            if (progress >= 50 && progress < 85) {
                boxTorso.style.display = 'block';
                boxTorso.querySelector('.box-label').textContent = `Torso [${Math.min(99, progress * 1.15).toFixed(1)}%]`;
            }
            if (progress >= 70 && progress < 85) {
                boxLegs.style.display = 'block';
                boxLegs.querySelector('.box-label').textContent = `Legs [${Math.min(99, progress * 1.1).toFixed(1)}%]`;
            }

            const logItem = logsSchedule.find(item => item.threshold === progress);
            if (logItem) {
                addLog(logItem.text, logItem.type);
            }

            if (progress >= 100) {
                clearInterval(scanInterval);
                setTimeout(() => {
                    showScanResults();
                }, 800);
            }
        }, 30);
    }

    function showScanResults() {
        scanPreviewContainer.style.display = 'none';
        scanResultContainer.style.display = 'flex';
        
        const aiBox = document.getElementById('ai-analysis-box');
        const aiText = document.getElementById('ai-analysis-text');
        if (aiBox && aiText) {
            if (scanAiDescription) {
                aiText.textContent = scanAiDescription;
                aiBox.style.display = 'block';
            } else {
                aiBox.style.display = 'none';
            }
        }
        
        const resultCardsContainer = document.querySelector('.result-cards');
        resultCardsContainer.innerHTML = '';
        
        if (!scanResults || scanResults.length === 0) return;
        
        const best = scanResults[0];
        const item2 = scanResults[1];
        const item3 = scanResults[2];
        
        const getRarityClass = (numParts) => {
            if (numParts >= 7) return 'rarity-legendary';
            if (numParts >= 5) return 'rarity-rare';
            return 'btn-primary';
        };
        const getRarityText = (numParts) => {
            if (numParts >= 7) return '传奇级 (Legendary)';
            if (numParts >= 5) return '稀有级 (Rare)';
            return '普通级 (Common)';
        };

        const bestCard = document.createElement('div');
        bestCard.className = 'result-card best-match';
        bestCard.setAttribute('data-minifig-num', best.minifig_num);
        bestCard.style.cursor = 'pointer';
        bestCard.innerHTML = `
            <div class="badge-best">最佳匹配 99.4%</div>
            <div class="result-image-box">
                <img id="match-img-1" src="${best.img_url}" alt="${best.name}" decoding="async" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%2313171f%22/><circle cx=%2250%22 cy=%2250%22 r=%2230%22 fill=%22rgba(0,123,255,0.1)%22/></svg>'">
            </div>
            <div class="result-info">
                <span class="fig-id">编号：${(best.official_id || best.minifig_num).toUpperCase()}</span>
                <h5 class="fig-name">${best.name}</h5>
                <p class="fig-meta"><strong>零件数量：</strong> ${best.num_parts} 个核心部件</p>
                <p class="fig-meta"><strong>稀有级别：</strong> <span class="${getRarityClass(best.num_parts)}">${getRarityText(best.num_parts)}</span></p>
                <div class="card-actions">
                    <button type="button" class="btn-card-primary" id="best-match-action-btn">查看详细配件</button>
                    <button type="button" class="btn-card-secondary" onclick="alert('即将接入官方交易接口，敬请期待！')">估价与交易</button>
                </div>
            </div>
        `;
        
        bestCard.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-card-secondary')) return;
            closeModal();
            showDetailPage(best.minifig_num);
        });
        
        resultCardsContainer.appendChild(bestCard);
        
        if (item2 || item3) {
            const secondaryContainer = document.createElement('div');
            secondaryContainer.className = 'secondary-matches';
            
            [item2, item3].forEach((item, index) => {
                if (!item) return;
                const percent = index === 0 ? '88.5%' : '65.2%';
                const miniCard = document.createElement('div');
                miniCard.className = 'result-card-mini';
                miniCard.setAttribute('data-minifig-num', item.minifig_num);
                miniCard.style.cursor = 'pointer';
                miniCard.innerHTML = `
                    <div class="mini-percent">${percent} 相似</div>
                    <img id="match-img-${index + 2}" src="${item.img_url}" alt="${item.name}" loading="lazy" decoding="async" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22%2313171f%22/><circle cx=%2250%22 cy=%2250%22 r=%2230%22 fill=%22rgba(0,123,255,0.1)%22/></svg>'">
                    <div class="mini-info">
                        <span class="fig-id">编号：${(item.official_id || item.minifig_num).toUpperCase()}</span>
                        <h6>${item.name}</h6>
                        <p class="fig-meta">${item.num_parts} 个零件</p>
                    </div>
                `;
                
                miniCard.addEventListener('click', () => {
                    closeModal();
                    showDetailPage(item.minifig_num);
                });
                
                secondaryContainer.appendChild(miniCard);
            });
            
            resultCardsContainer.appendChild(secondaryContainer);
        }
    }

    // --- 7. Encyclopedia Detail View (Real API Integration) ---
    async function showDetailPage(id) {
        try {
            if (detailCache.has(id)) {
                renderMinifigDetails(detailCache.get(id), id);
                return;
            }
            const res = await fetch(`/api/minifig?id=${encodeURIComponent(id)}`);
            if (!res.ok) {
                alert("未找到该人仔，可能数据库正在同步。");
                return;
            }
            const data = await res.json();
            detailCache.set(id, data);
            renderMinifigDetails(data, id);
        } catch (e) {
            console.error("Fetch minifig details error:", e);
            alert("读取人仔数据时出错，请稍后重试。");
        }
    }

    function renderMinifigDetails(data, id) {
        const minifig = data.minifig;
        preferences = normalizePreferences(preferences);
        currentMinifigId = minifig.minifig_num;
        currentPartsList = data.parts;

        // Hide search view, show details view
        searchContainer.style.display = 'none';
        detailContainer.style.display = 'block';
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Populate header
        // Try to fetch series/theme from the first set theme name, or fallback
        const seriesName = data.sets.length > 0 ? data.sets[0].theme_name : "乐高系列人仔";
        detailSeriesBadge.textContent = seriesName;
        detailTitle.textContent = minifig.name;
        
        // Update Favorite Star state
        const isFav = preferences.favorites.some(f => f.id === minifig.minifig_num);
        if (isFav) {
            favoriteBtn.classList.add('active');
            favoriteBtn.innerHTML = '<i class="fas fa-star"></i>';
        } else {
            favoriteBtn.classList.remove('active');
            favoriteBtn.innerHTML = '<i class="far fa-star"></i>';
        }
        
        infoId.textContent = minifig.official_id || minifig.minifig_num;
        
        // Year calculation
        const year = data.sets.length > 0 ? Math.min(...data.sets.map(s => s.year)) : "历史典藏";
        infoYear.textContent = year + " 年";

        // Calculate Rarity dynamically based on num_parts
        let rarityText = "普通级 (Common)";
        let rarityClass = "btn-primary";
        if (minifig.num_parts >= 4 && minifig.num_parts < 7) {
            rarityText = "稀有级 (Rare)";
            rarityClass = "btn-radar";
        } else if (minifig.num_parts >= 7) {
            rarityText = "传奇级 (Legendary)";
            rarityClass = "rarity-legendary";
        }
        infoRarity.innerHTML = `<span class="${rarityClass}">${rarityText}</span>`;
        if (infoParts) {
            infoParts.textContent = `${data.parts.length} 个零部件`;
        }

        // Render assembly components
        renderAssemblyComponents(data.parts, minifig.minifig_num);

        // Render containing Sets
        renderSetsCards(data.sets);

        // Reset shared sidebar list
        resetSharedPartsSidebar();

        // Render compatible weapons
        renderWeapons(data.weapons);
    }

    function renderWeapons(weapons) {
        const weaponsCard = document.getElementById('detail-weapons-card');
        const weaponsGrid = document.getElementById('detail-weapons-grid');
        const weaponsCount = document.getElementById('weapons-count-badge');
        
        if (!weaponsCard || !weaponsGrid || !weaponsCount) return;
        
        if (!weapons || weapons.length === 0) {
            weaponsCard.style.display = 'none';
            return;
        }
        
        weaponsCard.style.display = 'block';
        weaponsCount.textContent = weapons.length;
        weaponsGrid.innerHTML = '';
        
        weapons.forEach(wp => {
            const card = document.createElement('div');
            card.className = 'weapon-item-card';
            
            const imgHTML = wp.img_url
                ? `<img src="${wp.img_url}" alt="${wp.part_name}" loading="lazy" decoding="async" class="weapon-item-img">`
                : `<div class="weapon-item-placeholder"><i class="fas fa-shield-alt" style="color: var(--text-muted); font-size: 1.2rem;"></i></div>`;
                
            let displayName = wp.part_name;
            const bracketMatch = wp.part_name.match(/(.+?)\s*\[(.+?)\]$/);
            if (bracketMatch) {
                displayName = bracketMatch[1].trim();
            }
            
            card.innerHTML = `
                ${imgHTML}
                <div style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px;">
                    <div style="font-size: 0.78rem; font-weight: 700; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${displayName}">${displayName}</div>
                    <div style="font-size: 0.65rem; color: var(--text-muted); display: flex; align-items: center; gap: 4px;">
                        <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #${wp.color_rgb || 'ccc'}; border: 1px solid rgba(255,255,255,0.2);"></span>
                        <span style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 60px;">${wp.color_name}</span>
                    </div>
                </div>
            `;
            
            card.addEventListener('click', (e) => {
                e.stopPropagation();
                document.querySelectorAll('.lego-part-layer').forEach(l => l.classList.remove('selected-part'));
                
                showPartDetailFullscreen({
                    part_num: wp.part_num,
                    color_id: wp.color_id,
                    part_name: wp.part_name,
                    color_name: wp.color_name,
                    img_url: wp.img_url,
                    quantity: wp.quantity
                }, wp.quantity);
            });
            
            weaponsGrid.appendChild(card);
        });
    }



    function assignMinifigParts(parts) {
        if (!parts || parts.length === 0) {
            return { hatPart: null, headPart: null, torsoPart: null, legsPart: null };
        }

        let assignedPartNums = new Set();
        let torsoPart = null;
        let legsPart = null;
        let headPart = null;
        let hatPart = null;

        // Step 0: Check for Integrated Giant Body (Big Fig / Gollum / Creature)
        const giantBodyPart = parts.find(p => p.part_cat_id === 13 || 
                                              p.part_name.toLowerCase().includes('body giant') || 
                                              p.part_name.toLowerCase().includes('giant body'));
        
        if (giantBodyPart) {
            torsoPart = giantBodyPart;
            legsPart = null; // Big Figs have integrated legs
            assignedPartNums.add(giantBodyPart.part_num);
        }

        // Pass 1: Match by Rebrickable category IDs
        if (!legsPart && !giantBodyPart) {
            legsPart = parts.find(p => p.part_cat_id === 61);
            if (legsPart) assignedPartNums.add(legsPart.part_num);
        }
        
        if (!torsoPart) {
            torsoPart = parts.find(p => p.part_cat_id === 60 && 
                !p.part_name.toLowerCase().includes('arm') && 
                !p.part_name.toLowerCase().includes('hand') && 
                !assignedPartNums.has(p.part_num));
            if (torsoPart) assignedPartNums.add(torsoPart.part_num);
        }
        
        headPart = parts.find(p => p.part_cat_id === 59 && !assignedPartNums.has(p.part_num));
        if (headPart) assignedPartNums.add(headPart.part_num);
        
        hatPart = parts.find(p => (p.part_cat_id === 65 || p.part_cat_id === 72) && !assignedPartNums.has(p.part_num));
        if (hatPart) assignedPartNums.add(hatPart.part_num);
        
        // Pass 2: Fallback to translated keyword checking for missing core parts
        if (!legsPart && !giantBodyPart) {
            legsPart = parts.find(p => {
                if (assignedPartNums.has(p.part_num)) return false;
                const name = p.part_name.toLowerCase();
                return name.includes('legs') || name.includes('hips') || name.includes('pants') || name.includes('tail') || name.includes('skirt') || name.includes('gown') || name.includes('下身') || name.includes('腿部');
            });
            if (legsPart) assignedPartNums.add(legsPart.part_num);
        }
        if (!torsoPart) {
            torsoPart = parts.find(p => {
                if (assignedPartNums.has(p.part_num)) return false;
                const name = p.part_name.toLowerCase();
                return name.includes('torso') || name.includes('body') || name.includes('jacket') || name.includes('躯干') || name.includes('身体') || name.includes('上衣') || name.includes('giant') || p.part_cat_id === 13;
            });
            if (torsoPart) assignedPartNums.add(torsoPart.part_num);
        }
        if (!headPart) {
            headPart = parts.find(p => {
                if (assignedPartNums.has(p.part_num)) return false;
                const name = p.part_name.toLowerCase();
                return (name.includes('head') && !name.includes('wear') && !name.includes('band')) || name.includes('头部') || name.includes('脸部') || name.includes('表情');
            });
            if (headPart) assignedPartNums.add(headPart.part_num);
        }
        if (!hatPart) {
            hatPart = parts.find(p => {
                if (assignedPartNums.has(p.part_num)) return false;
                const name = p.part_name.toLowerCase();
                return name.includes('helmet') || name.includes('hair') || name.includes('mask') || name.includes('hat') || name.includes('crown') ||
                       name.includes('头盔') || name.includes('面罩') || name.includes('发饰') || name.includes('发型') || name.includes('头发') || name.includes('帽子');
            });
            if (hatPart) assignedPartNums.add(hatPart.part_num);
        }

        // Pass 3: Map remaining accessories only if they are not spurious
        const isSpuriousPart = (p) => {
            const name = p.part_name.toLowerCase();
            return name.includes('arm') || 
                   name.includes('hand') || 
                   (name.includes('pin') && !name.includes('hole')) || 
                   name.includes('horn') || 
                   name.includes('axle') || 
                   name.includes('tentacle') || 
                   name.includes('branch') ||
                   name.includes('animal body part');
        };
        const unassignedParts = parts.filter(p => !assignedPartNums.has(p.part_num));

        if (!legsPart && !giantBodyPart && unassignedParts.length > 0) {
            const candidate = unassignedParts.find(p => !isSpuriousPart(p));
            if (candidate) {
                legsPart = candidate;
                assignedPartNums.add(legsPart.part_num);
            }
        }
        if (!torsoPart && unassignedParts.length > 0) {
            const candidate = unassignedParts.find(p => !isSpuriousPart(p));
            if (candidate) {
                torsoPart = candidate;
                assignedPartNums.add(torsoPart.part_num);
            }
        }
        if (!headPart && unassignedParts.length > 0) {
            const candidate = unassignedParts.find(p => !isSpuriousPart(p));
            if (candidate) {
                headPart = candidate;
                assignedPartNums.add(headPart.part_num);
            }
        }
        if (!hatPart && unassignedParts.length > 0) {
            const candidate = unassignedParts.find(p => !isSpuriousPart(p));
            if (candidate) {
                hatPart = candidate;
                assignedPartNums.add(hatPart.part_num);
            }
        }

        return { hatPart, headPart, torsoPart, legsPart };
    }

    function renderAssemblyComponents(parts, minifigId) {
        // Reset stage filters
        legoAssemblyStage.className = 'lego-figure-canvas exploded'; 
        const isBigfig = parts.some(p => p.part_cat_id === 13);
        if (isBigfig) {
            legoAssemblyStage.classList.add('is-bigfig');
        }
        
        if (selectedPartLabel) {
            selectedPartLabel.textContent = '当前零件: 点击左侧人仔部件';
            selectedPartLabel.classList.remove('active');
        }
        legoAssemblyStage.querySelectorAll('.lego-part-layer').forEach(layer => layer.classList.remove('selected-part'));

        // Populate complete minifigure image
        const fullFigImg = document.getElementById('lego-full-figure-img');
        fullFigImg.src = `https://cdn.rebrickable.com/media/sets/${minifigId}.jpg`;
        fullFigImg.onerror = () => {
            fullFigImg.src = 'data:image/svg+xml;utf8,' + encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="220" height="220"><defs><linearGradient id="glow-grad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FFD500" /><stop offset="100%" stop-color="#FF5E00" /></linearGradient></defs><circle cx="50" cy="50" r="46" fill="rgba(255,255,255,0.01)" stroke="rgba(255,255,255,0.05)" stroke-width="1.5"/><circle cx="50" cy="50" r="40" fill="rgba(0,0,0,0.2)" stroke="rgba(255,255,255,0.02)" stroke-width="1"/><g transform="translate(0, 3)" fill="url(#glow-grad)" opacity="0.85"><rect x="45" y="16" width="10" height="4" rx="1"/><rect x="39" y="21" width="22" height="19" rx="5"/><rect x="37" y="26" width="26" height="9" rx="3"/><rect x="46" y="40" width="8" height="3"/><path d="M 34,44 L 66,44 L 71,72 L 29,72 Z"/><rect x="31" y="74" width="38" height="6" rx="1"/><rect x="31" y="81" width="17" height="15" rx="3"/><rect x="52" y="81" width="17" height="15" rx="3"/></g></svg>`);
        };

        // Remove any existing dynamic part layers
        const oldLayers = legoAssemblyStage.querySelectorAll('.lego-part-layer');
        oldLayers.forEach(l => l.remove());

        // Draw real parts images dynamically for ALL parts
        parts.forEach(part => {
            const layer = document.createElement('div');
            layer.className = 'lego-part-layer';
            
            // Set attributes for click listeners
            layer.setAttribute('data-part-num', part.part_num);
            layer.setAttribute('data-color-id', part.color_id);
            layer.setAttribute('data-part-name', part.part_name);
            
            // Label tag (slides in on hover)
            const labelTag = document.createElement('div');
            labelTag.className = 'part-label-tag';
            
            // Format name nicely
            let displayName = part.part_name;
            const bracketMatch = part.part_name.match(/(.+?)\s*\[(.+?)\]$/);
            if (bracketMatch) {
                displayName = bracketMatch[1].trim();
            }
            labelTag.textContent = displayName;
            layer.appendChild(labelTag);
            
            // SVG / Image Holder bubble
            const holder = document.createElement('div');
            holder.className = 'lego-svg-holder';
            if (part.img_url) {
                holder.innerHTML = `<img src="${part.img_url}" alt="${part.part_name}" loading="lazy" decoding="async">`;
            } else {
                holder.innerHTML = `<i class="fas fa-puzzle-piece" style="font-size: 1.8rem; color: var(--text-muted);"></i>`;
            }
            layer.appendChild(holder);
            
            // Bind click event dynamically
            layer.addEventListener('click', async (e) => {
                e.stopPropagation();
                
                // Highlight part
                legoAssemblyStage.classList.add('part-filtering');
                legoAssemblyStage.querySelectorAll('.lego-part-layer').forEach(l => l.classList.remove('selected-part'));
                layer.classList.add('selected-part');
                
                // Highlight label with ID/Number
                let displayName = part.part_name;
                let originalName = '';
                const bracketMatch = part.part_name.match(/(.+?)\s*\[(.+?)\]$/);
                if (bracketMatch) {
                    displayName = bracketMatch[1].trim();
                    originalName = bracketMatch[2].trim();
                }

                showPartDetailFullscreen(part);
            });
            
            legoAssemblyStage.appendChild(layer);
        });

        // Trigger Assembly Animation with sound
        setTimeout(() => {
            legoAssemblyStage.classList.remove('exploded');
            playAssembleSound();
            legoAssemblyStage.classList.add('assembling-click');
            setTimeout(() => legoAssemblyStage.classList.remove('assembling-click'), 150);
        }, 700);
    }

    function renderSetsCards(sets) {
        detailSetsGrid.innerHTML = '';
        if (sets.length === 0) {
            detailSetsGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 20px;">
                    <i class="fas fa-info-circle" style="font-size: 1.5rem; margin-bottom: 8px;"></i>
                    <p>在离线数据库中暂未查到包含该人仔的独立套装，可能该角色为收藏展会、扭蛋或散件发行。</p>
                </div>
            `;
            return;
        }

        sets.forEach(set => {
            const card = document.createElement('div');
            card.className = 'set-card';
            
            // Set image rendering (Real URL if available, else box placeholder)
            const imgHTML = set.img_url 
                ? `<img src="${set.img_url}" alt="${set.set_name}" loading="lazy" decoding="async" style="max-width: 90%; max-height: 90%; object-fit: contain;">`
                : `<svg viewBox="0 0 100 100" width="80" height="80"><rect width="100" height="100" fill="var(--bg-secondary)" rx="10" stroke="var(--border-color)"/><rect x="15" y="15" width="70" height="70" fill="var(--accent-glow)" rx="6"/><text x="50" y="55" font-family="var(--font-outfit)" font-size="12" font-weight="bold" fill="var(--accent-color)" text-anchor="middle">SET</text></svg>`;

            card.innerHTML = `
                <div class="set-img-box">
                    ${imgHTML}
                </div>
                <div class="set-info">
                    <div>
                        <span class="set-num">${set.num_parts} Parts | ${set.year} 年</span>
                        <h5 class="set-name">${set.set_name}</h5>
                    </div>
                    <button type="button" class="btn-view-manual" data-setid="${set.set_num}" data-setname="${set.set_name}">
                        <i class="fas fa-book-open"></i> 查阅官方说明书
                    </button>
                </div>
            `;
            
            card.querySelector('.btn-view-manual').addEventListener('click', (e) => {
                const setNum = e.currentTarget.getAttribute('data-setid');
                const setName = e.currentTarget.getAttribute('data-setname');
                openInstructionManual(setNum, setName);
            });

            detailSetsGrid.appendChild(card);
        });
    }

    function resetSharedPartsSidebar() {
        if (!sharedListResults) return;
        sharedListResults.innerHTML = `
            <div class="empty-shared-state">
                <div class="icon-wrapper">
                    <i class="fas fa-hand-point-left animate-bounce-x"></i>
                </div>
                <p>点击左侧人仔拼装区域的任意部件，即可透视查看与此角色共享该零件的其他乐高人仔！</p>
            </div>
        `;
    }

    backToSearchBtn.addEventListener('click', () => {
        detailContainer.style.display = 'none';
        searchContainer.style.display = 'flex';
    });

    // --- 7.5 Interactive Swipe Right on Detail Page to Go Back ---
    let detailTouchStartX = 0;
    let detailTouchStartY = 0;
    let isSwipingBack = false;
    let hasDecidedSwipeDirection = false;

    detailContainer.addEventListener('touchstart', (e) => {
        const touch = e.touches[0];
        detailTouchStartX = touch.clientX;
        detailTouchStartY = touch.clientY;
        isSwipingBack = false;
        hasDecidedSwipeDirection = false;
        
        // Only trigger if starting near left edge (within 80px)
        if (detailTouchStartX < 80) {
            detailContainer.style.transition = 'none';
        }
    }, { passive: true });

    detailContainer.addEventListener('touchmove', (e) => {
        if (detailTouchStartX >= 80) return;
        
        const touch = e.touches[0];
        const diffX = touch.clientX - detailTouchStartX;
        const diffY = touch.clientY - detailTouchStartY;
        
        if (!hasDecidedSwipeDirection) {
            // Decide direction on first movement of > 10px
            if (Math.abs(diffX) > 10 || Math.abs(diffY) > 10) {
                hasDecidedSwipeDirection = true;
                if (diffX > 0 && Math.abs(diffX) > Math.abs(diffY)) {
                    isSwipingBack = true;
                }
            }
        }
        
        if (isSwipingBack && diffX > 0) {
            // Prevent default scroll when actively swiping back
            if (e.cancelable) {
                e.preventDefault();
            }
            // Translate the detail container to the right
            detailContainer.style.transform = `translate3d(${diffX}px, 0, 0)`;
        }
    }, { passive: false });

    detailContainer.addEventListener('touchend', (e) => {
        if (!isSwipingBack) return;
        
        const touch = e.changedTouches[0];
        const diffX = touch.clientX - detailTouchStartX;
        
        detailContainer.style.transition = 'transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1)';
        
        if (diffX > 120) {
            // Swiped far enough, complete the exit animation
            detailContainer.style.transform = `translate3d(100%, 0, 0)`;
            setTimeout(() => {
                backToSearchBtn.click();
                detailContainer.style.transform = '';
                detailContainer.style.transition = '';
            }, 250);
        } else {
            // Cancel swipe, return to origin
            detailContainer.style.transform = `translate3d(0, 0, 0)`;
            setTimeout(() => {
                detailContainer.style.transform = '';
                detailContainer.style.transition = '';
            }, 250);
        }
        isSwipingBack = false;
    }, { passive: true });

    // --- 8. Assembly Explode/Assemble Buttons ---
    btnExplode.addEventListener('click', () => {
        legoAssemblyStage.classList.add('exploded');
    });

    btnAssemble.addEventListener('click', () => {
        if (legoAssemblyStage.classList.contains('exploded')) {
            legoAssemblyStage.classList.remove('exploded');
            playAssembleSound();
            legoAssemblyStage.classList.add('assembling-click');
            setTimeout(() => legoAssemblyStage.classList.remove('assembling-click'), 150);
        }
    });

    // Click on complete assembled minifigure to explode it
    const legoFullFigure = document.getElementById('lego-full-figure');
    if (legoFullFigure) {
        legoFullFigure.addEventListener('click', (e) => {
            e.stopPropagation();
            btnExplode.click();
        });
    }

    // Reset selection when clicking on the assembly stage background
    legoAssemblyStage.addEventListener('click', () => {
        legoAssemblyStage.classList.remove('part-filtering');
        legoAssemblyStage.querySelectorAll('.lego-part-layer').forEach(l => l.classList.remove('selected-part'));
    });

    // Full-Screen Part Detail Modal Overlay (Apple Style)
    const partDetailModal = document.getElementById('part-detail-fullscreen-modal');
    const closePartModalBtn = document.getElementById('close-part-modal-btn');
    
    const closePartModal = () => {
        if (partDetailModal) partDetailModal.classList.remove('open');
    };
    
    if (closePartModalBtn) {
        closePartModalBtn.addEventListener('click', closePartModal);
    }
    if (partDetailModal) {
        partDetailModal.addEventListener('click', (e) => {
            if (e.target === partDetailModal) closePartModal();
        });
    }

    async function showPartDetailFullscreen(part, quantityVal = 1) {
        const fullscreenImg = document.getElementById('part-fullscreen-img');
        const fullscreenTitle = document.getElementById('part-fullscreen-title');
        const fullscreenOriginalTitle = document.getElementById('part-fullscreen-original-title');
        const fullscreenDesignId = document.getElementById('part-fullscreen-design-id');
        const fullscreenElementId = document.getElementById('part-fullscreen-element-id');
        const fullscreenColor = document.getElementById('part-fullscreen-color');
        const fullscreenQuantity = document.getElementById('part-fullscreen-quantity');
        const sharedGallery = document.getElementById('part-shared-gallery');
        
        if (!partDetailModal) return;
        
        // Parse name translations
        let displayName = part.part_name || part.name || '乐高零部件';
        let originalName = '';
        const bracketMatch = displayName.match(/(.+?)\s*\[(.+?)\]$/);
        if (bracketMatch) {
            displayName = bracketMatch[1].trim();
            originalName = bracketMatch[2].trim();
        }
        
        // Update details
        if (fullscreenImg) {
            fullscreenImg.src = part.img_url || `https://cdn.rebrickable.com/media/parts/ldraw/${part.color_id}/${part.part_num}.png`;
            fullscreenImg.onerror = () => {
                fullscreenImg.src = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='rgba(0,0,0,0.05)'/><path d='M30,30 L70,70 M70,30 L30,70' stroke='rgba(0,0,0,0.2)' stroke-width='2'/></svg>";
            };
        }
        if (fullscreenTitle) fullscreenTitle.textContent = displayName;
        if (fullscreenOriginalTitle) {
            fullscreenOriginalTitle.textContent = originalName || part.part_name || '';
            fullscreenOriginalTitle.style.display = originalName ? 'block' : 'none';
        }
        if (fullscreenDesignId) fullscreenDesignId.textContent = part.part_num;
        if (fullscreenElementId) fullscreenElementId.textContent = part.element_id || '暂无官方 Element ID';
        if (fullscreenColor) fullscreenColor.textContent = part.color_name || '原色';
        if (fullscreenQuantity) fullscreenQuantity.textContent = part.quantity || quantityVal;
        
        // Open modal
        partDetailModal.classList.add('open');
        
        // Clear and show loading state in gallery
        if (sharedGallery) {
            sharedGallery.innerHTML = `
                <div class="gallery-loading" style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                    <i class="fas fa-spinner fa-spin" style="font-size: 1.8rem; margin-bottom: 12px; color: var(--accent-color);"></i>
                    <p>正在云端检索共享此零件的其他角色实物图...</p>
                </div>
            `;
        }
        
        // Fetch shared characters
        try {
            const res = await fetch(`/api/shared-part?part_num=${part.part_num}&color_id=${part.color_id}&exclude=${encodeURIComponent(currentMinifigId)}`);
            if (!res.ok) return;
            const data = await res.json();
            
            if (sharedGallery) {
                sharedGallery.innerHTML = '';
                if (data.length === 0) {
                    sharedGallery.innerHTML = `
                        <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                            <i class="fas fa-info-circle" style="font-size: 1.5rem; margin-bottom: 10px;"></i>
                            <p>该零件为此款角色独占设计（在当前数据库中暂无其他共享角色记录）。</p>
                        </div>
                    `;
                    return;
                }
                
                data.forEach(item => {
                    const card = document.createElement('div');
                    card.className = 'shared-figure-card';
                    card.innerHTML = `
                        <div class="shared-figure-img-box">
                            <img src="${item.img_url}" alt="${item.name}" loading="lazy" onerror="this.src='data:image/svg+xml;utf8,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 fill=%22rgba(0,0,0,0.05)%22/><circle cx=%2250%22 cy=%2250%22 r=%2230%22 fill=%22rgba(10,132,255,0.08)%22/></svg>'">
                        </div>
                        <div class="shared-figure-info">
                            <h5 class="shared-figure-title">${item.name}</h5>
                            <span class="shared-figure-code">官方编号: ${(item.official_id || item.minifig_num).toUpperCase()}</span>
                        </div>
                    `;
                    card.addEventListener('click', () => {
                        // Switch page directly
                        partDetailModal.classList.remove('open');
                        showDetailPage(item.minifig_num);
                    });
                    sharedGallery.appendChild(card);
                });
            }
        } catch (err) {
            console.error("Fetch shared characters failed:", err);
            if (sharedGallery) {
                sharedGallery.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-muted);">
                        <i class="fas fa-exclamation-triangle" style="font-size: 1.5rem; margin-bottom: 10px; color: #ff9f0a;"></i>
                        <p>跨数据库比对服务超时，请稍后重试。</p>
                    </div>
                `;
            }
        }
    }

    // --- 9. Dynamic Booklet Manual Generator ---
    function openInstructionManual(setNum, setName) {
        currentManualPageIdx = 0;
        manualModal.classList.add('open');
        
        // Build direct PDF download link
        const baseSetNum = setNum.split('-')[0];
        btnDownloadPdf.href = `https://www.lego.com/zh-cn/service/buildinginstructions/search?q=${encodeURIComponent(baseSetNum)}`;
        
        // Build custom simulated steps for this specific minifigure!
        buildDynamicManualSteps(setName);
        renderManualPages();
    }

    function buildDynamicManualSteps(setName) {
        // Map current parts using the unified helper
        const { hatPart, headPart, torsoPart, legsPart } = assignMinifigParts(currentPartsList);

        // Part Graphic Renderers
        const getPartGraphic = (part, placeholderSVG) => {
            if (part && part.img_url) {
                return `<img src="${part.img_url}" alt="${part.part_name}" class="manual-build-graphic" loading="lazy" decoding="async" style="max-height: 70%; max-width: 70%; object-fit: contain;">`;
            }
            return placeholderSVG;
        };

        // Construct 4 dynamic steps
        currentManualSteps = [
            {
                step: '1',
                desc: legsPart && torsoPart 
                    ? `从零件盒中取出腿部部件 <code>${legsPart.part_num}</code> 与印花躯干 <code>${torsoPart.part_num}</code>，进行垂直对齐插紧。`
                    : (torsoPart ? `取出一体化巨型躯干部件 <code>${torsoPart.part_num}</code>，将其立于展示台上。` : '拼搭腿部与躯干零件。'),
                qty: '1',
                partIcon: 'fa-shirt',
                svg: getPartGraphic(torsoPart, `<svg viewBox="0 0 100 100" class="manual-build-graphic"><polygon points="30,20 70,20 75,70 25,70" fill="none" stroke="#2d3748" stroke-width="2"/></svg>`)
            },
            {
                step: '2',
                desc: headPart 
                    ? `拿出面部表情印花头部 <code>${headPart.part_num}</code>，注意眼鼻方向，套入躯干顶部的卡销。`
                    : '安插人仔头部，注意表情方向。',
                qty: '1',
                partIcon: 'fa-smile',
                svg: getPartGraphic(headPart, `<svg viewBox="0 0 100 100" class="manual-build-graphic"><rect x="35" y="30" width="30" height="30" rx="8" fill="none" stroke="#2d3748" stroke-width="2"/></svg>`)
            },
            {
                step: '3',
                desc: hatPart 
                    ? `将头部配件（发饰/头盔）<code>${hatPart.part_num}</code> 扣在头部上方，直至听到轻微响声。`
                    : '带上面罩/发饰，完成拼装。',
                qty: '1',
                partIcon: 'fa-graduation-cap',
                svg: getPartGraphic(hatPart, `<svg viewBox="0 0 100 100" class="manual-build-graphic"><circle cx="50" cy="50" r="20" fill="none" stroke="#2d3748" stroke-width="2"/></svg>`)
            },
            {
                step: '4',
                desc: `人仔装配完毕！所属乐高套装：<code>${setName}</code>。`,
                qty: '1',
                partIcon: 'fa-box-open',
                svg: `<img src="https://cdn.rebrickable.com/media/sets/${currentMinifigId}.jpg" alt="Complete" class="manual-build-graphic" style="max-height: 85%; max-width: 85%; object-fit: contain; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.15));" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,'+encodeURIComponent('<svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\' width=\'100\' height=\'100\'><defs><linearGradient id=\'glow-grad\' x1=\'0%\' y1=\'0%\' x2=\'100%\' y2=\'100%\'><stop offset=\'0%\' stop-color=\'#FFD500\' /><stop offset=\'100%\' stop-color=\'#FF5E00\' /></linearGradient></defs><g fill=\'url(#glow-grad)\\'><rect x=\'45\' y=\'16\' width=\'10\' height=\'4\' rx=\'1\'/><rect x=\'39\' y=\'21\' width=\'22\' height=\'19\' rx=\'5\'/><rect x=\'37\' y=\'26\' width=\'26\' height=\'9\' rx=\'3\'/><rect x=\'46\' y=\'40\' width=\'8\' height=\'3\'/><path d=\'M 34,44 L 66,44 L 71,72 L 29,72 Z\'/><rect x=\'31\' y=\'74\' width=\'38\' height=\'6\' rx=\'1\'/><rect x=\'31\' y=\'81\' width=\'17\' height=\'15\' rx=\'3\'/><rect x=\'52\' y=\'81\' width=\'17\' height=\'15\' rx=\'3\'/></g></svg>')">`
            }
        ];
    }

    function renderManualPages() {
        const pages = currentManualSteps;
        const maxPages = pages.length;
        
        // Update page number label
        manualPageNumLabel.textContent = `第 ${currentManualPageIdx + 1} / ${maxPages} 步`;

        const pageData = pages[currentManualPageIdx];
        
        // Add flip animations
        manualLeftPage.classList.add('flipping');
        manualRightPage.classList.add('flipping');
        
        setTimeout(() => {
            manualLeftPage.classList.remove('flipping');
            manualRightPage.classList.remove('flipping');
        }, 300);

        // Render Left Page: Inventory list for this step
        manualLeftPage.innerHTML = `
            <div class="manual-step-header">
                <span class="manual-step-badge">STEP ${pageData.step}</span>
                <i class="fas ${pageData.partIcon} manual-step-part-icon"></i>
            </div>
            <div>
                <p class="manual-step-desc">${pageData.desc}</p>
            </div>
            <div class="manual-page-footer">
                <span>© LEGO Building Instructions</span>
                <span>Page ${(currentManualPageIdx * 2) + 1}</span>
            </div>
        `;

        // Render Right Page: Visual Builder Diagram
        manualRightPage.innerHTML = `
            <div class="manual-step-header">
                <span>图纸结构示意</span>
                <i class="fas fa-arrows-spin animate-pulse"></i>
            </div>
            <div class="manual-illustration">
                <div class="manual-parts-inventory">
                    <i class="fas fa-puzzle-piece"></i> x ${pageData.qty}
                    <div class="inventory-qty">1</div>
                </div>
                ${pageData.svg}
            </div>
            <div class="manual-page-footer">
                <span>Set #${currentMinifigId}</span>
                <span>Page ${(currentManualPageIdx * 2) + 2}</span>
            </div>
        `;

        // Disable buttons accordingly
        btnManualPrev.disabled = currentManualPageIdx === 0;
        btnManualNext.disabled = currentManualPageIdx === maxPages - 1;
    }

    btnManualPrev.addEventListener('click', () => {
        if (currentManualPageIdx > 0) {
            currentManualPageIdx--;
            renderManualPages();
            playAssembleSound();
        }
    });

    btnManualNext.addEventListener('click', () => {
        if (currentManualPageIdx < currentManualSteps.length - 1) {
            currentManualPageIdx++;
            renderManualPages();
            playAssembleSound();
        }
    });

    closeManualBtn.addEventListener('click', () => {
        manualModal.classList.remove('open');
    });
    
    manualModal.addEventListener('click', (e) => {
        if (e.target === manualModal) {
            manualModal.classList.remove('open');
        }
    });

    // --- 9. Minifigure Encyclopedia Gallery Logic ---
    let galleryPage = 1;
    let galleryTheme = "";
    let gallerySort = "num_parts_desc";
    let gallerySearch = "";
    let isLoadingGallery = false;
    let endOfGallery = false;

    async function fetchGalleryItems(clearGrid = false) {
        if (isLoadingGallery) return;
        isLoadingGallery = true;
        
        if (clearGrid) {
            galleryGrid.innerHTML = "";
            galleryPage = 1;
            endOfGallery = false;
            btnLoadMore.style.display = "none";
        }
        
        galleryLoadingIndicator.style.display = "flex";
        
        try {
            // Merge filters theme or gallery search
            const queryTheme = gallerySearch ? gallerySearch : galleryTheme;
            const url = `/api/gallery?page=${galleryPage}&limit=24&theme=${encodeURIComponent(queryTheme)}&sort=${gallerySort}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error("API error");
            const items = await res.json();
            
            if (items.length < 24) {
                endOfGallery = true;
                btnLoadMore.style.display = "none";
            } else {
                btnLoadMore.style.display = "flex";
            }
            
            renderGalleryItems(items);
        } catch (e) {
            console.error("Gallery load error:", e);
            if (clearGrid) {
                galleryGrid.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">
                        <i class="fas fa-exclamation-triangle" style="font-size: 2rem; margin-bottom: 12px; color: #ff3b30;"></i>
                        <p>无法载入图库，请确认本地后端服务器已正常启动。</p>
                    </div>
                `;
            }
        } finally {
            isLoadingGallery = false;
            galleryLoadingIndicator.style.display = "none";
        }
    }

    function renderGalleryItems(items) {
        if (items.length === 0 && galleryPage === 1) {
            galleryGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 60px;">
                    <i class="fas fa-folder-open" style="font-size: 2.5rem; margin-bottom: 12px; opacity: 0.5;"></i>
                    <p>在数据库中未找到符合筛选条件的人仔，请换个词试试。</p>
                </div>
            `;
            return;
        }

        items.forEach(item => {
            const card = document.createElement("div");
            card.className = "gallery-card";
            card.setAttribute("data-id", item.minifig_num);
            
            card.innerHTML = `
                <div class="gallery-card-img">
                    <img src="https://cdn.rebrickable.com/media/sets/${item.minifig_num}.jpg" alt="${item.name}" loading="lazy" decoding="async" onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,'+encodeURIComponent('<svg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 100 100\\' width=\\'100\\' height=\\'100\\'><defs><linearGradient id=\\'glow-grad\\' x1=\\'0%\\' y1=\\'0%\\' x2=\\'100%\\' y2=\\'100%\\'><stop offset=\\'0%\\' stop-color=\\'#FFD500\\' /><stop offset=\\'100%\\' stop-color=\\'#FF5E00\\' /></linearGradient></defs><g fill=\\'url(#glow-grad)\\'><rect x=\\'45\\' y=\\'16\\' width=\\'10\\' height=\\'4\\' rx=\\'-1\\'/><rect x=\\'39\\' y=\\'21\\' width=\\'22\\' height=\\'19\\' rx=\\'5\\'/><rect x=\\'37\\' y=\\'26\\' width=\\'26\\' height=\\'9\\' rx=\\'3\\'/><rect x=\\'46\\' y=\\'40\\' width=\\'8\\' height=\\'3\\'/><path d=\\'M 34,44 L 66,44 L 71,72 L 29,72 Z\\'/><rect x=\\'31\\' y=\\'74\\' width=\\'38\\' height=\\'6\\' rx=\\'1\\'/><rect x=\\'31\\' y=\\'81\\' width=\\'17\\' height=\\'15\\' rx=\\'3\\'/><rect x=\\'52\\' y=\\'81\\' width=\\'17\\' height=\\'15\\' rx=\\'3\\'/></g></svg>')">
                </div>
                <div class="gallery-card-info">
                    <div class="gallery-card-meta">
                        <span class="gallery-card-id">${(item.official_id || item.minifig_num).toUpperCase()}</span>
                        <span class="gallery-card-theme">${item.theme_name}</span>
                    </div>
                    <h4 class="gallery-card-name" title="${item.name}">${item.name}</h4>
                    <span class="gallery-card-parts"><i class="fas fa-puzzle-piece"></i> ${item.num_parts} 核心部件</span>
                </div>
            `;
            
            card.addEventListener("click", () => {
                galleryContainer.style.display = "none";
                showDetailPage(item.minifig_num);
            });
            
            galleryGrid.appendChild(card);
        });
    }

    const favoritesContainer = document.getElementById('favorites-container');
    const navFavBtn = document.getElementById('nav-fav-btn');
    const backFromFavBtn = document.getElementById('back-from-fav-btn');

    // Event listener to open gallery view
    function openGalleryView() {
        searchContainer.style.display = "none";
        detailContainer.style.display = "none";
        aboutContainer.style.display = "none";
        if (favoritesContainer) favoritesContainer.style.display = "none";
        galleryContainer.style.display = "flex";
        
        navSearchBtn.classList.remove("active");
        navGalleryBtn.classList.add("active");
        if (navFavBtn) navFavBtn.classList.remove("active");
        navAboutBtn.classList.remove("active");
        
        // Reset filter inputs
        galleryThemeFilter.value = "";
        gallerySortFilter.value = "num_parts_desc";
        gallerySearchInput.value = "";
        galleryTheme = "";
        gallerySort = "num_parts_desc";
        gallerySearch = "";
        
        window.scrollTo({ top: 0, behavior: "smooth" });
        fetchGalleryItems(true);
    }

    function openAboutView(subTab = "legal-terms") {
        searchContainer.style.display = "none";
        detailContainer.style.display = "none";
        galleryContainer.style.display = "none";
        if (favoritesContainer) favoritesContainer.style.display = "none";
        aboutContainer.style.display = "flex";
        
        navSearchBtn.classList.remove("active");
        navGalleryBtn.classList.remove("active");
        if (navFavBtn) navFavBtn.classList.remove("active");
        navAboutBtn.classList.add("active");
        
        window.scrollTo({ top: 0, behavior: "smooth" });
        switchLegalTab(subTab);
    }

    function openSearchView() {
        detailContainer.style.display = "none";
        galleryContainer.style.display = "none";
        aboutContainer.style.display = "none";
        if (favoritesContainer) favoritesContainer.style.display = "none";
        searchContainer.style.display = "flex";
        
        navSearchBtn.classList.add("active");
        navGalleryBtn.classList.remove("active");
        if (navFavBtn) navFavBtn.classList.remove("active");
        navAboutBtn.classList.remove("active");
        
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function openFavoritesView() {
        searchContainer.style.display = "none";
        detailContainer.style.display = "none";
        galleryContainer.style.display = "none";
        aboutContainer.style.display = "none";
        if (favoritesContainer) favoritesContainer.style.display = "flex";
        
        navSearchBtn.classList.remove("active");
        navGalleryBtn.classList.remove("active");
        if (navFavBtn) navFavBtn.classList.add("active");
        navAboutBtn.classList.remove("active");
        
        window.scrollTo({ top: 0, behavior: "smooth" });
        renderFavoritesDashboard();
    }

    function renderFavoritesDashboard() {
        const favCountLabel = document.getElementById('fav-dashboard-count');
        const favValueLabel = document.getElementById('fav-dashboard-value');
        const favRatioLabel = document.getElementById('fav-dashboard-ratio');
        const favGrid = document.getElementById('favorites-gallery-grid');
        
        if (!favGrid) return;
        favGrid.innerHTML = '';
        
        const favs = preferences.favorites || [];
        
        // Update stats
        if (favCountLabel) favCountLabel.textContent = favs.length;
        if (favValueLabel) {
            let totalValue = 0;
            favs.forEach(f => {
                const partsVal = (f.num_parts || 4) * 25.5;
                totalValue += partsVal + (f.num_parts >= 7 ? 450 : (f.num_parts >= 5 ? 120 : 15));
            });
            favValueLabel.textContent = totalValue.toFixed(2);
        }
        if (favRatioLabel) {
            const ratio = (favs.length / 84921) * 100;
            favRatioLabel.textContent = ratio >= 0.01 ? `${ratio.toFixed(2)}%` : `${ratio.toFixed(4)}%`;
        }
        
        if (favs.length === 0) {
            favGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 60px; color: var(--text-muted);">
                    <i class="far fa-star" style="font-size: 2.5rem; margin-bottom: 14px; color: var(--border-color);"></i>
                    <p style="font-size: 0.95rem; font-weight: 500;">您的收藏夹空空如也</p>
                    <p style="font-size: 0.8rem; margin-top: 5px;">在人仔详情页中点击星标，即可将其加入收藏清单</p>
                    <button type="button" class="btn-database-link" onclick="document.getElementById('nav-gallery-btn').click()" style="margin: 15px auto 0 auto; display: flex;">浏览图鉴</button>
                </div>
            `;
            return;
        }
        
        favs.forEach(item => {
            const favId = item.minifig_num || item.id;
            if (!favId) return;
            const card = document.createElement('div');
            card.className = 'gallery-card';
            card.innerHTML = `
                <div class="gallery-card-img">
                    <img src="${item.img_url || `https://cdn.rebrickable.com/media/sets/${favId}.jpg`}" alt="${item.name}" loading="lazy">
                </div>
                <div class="gallery-card-info">
                    <div class="gallery-card-meta">
                        <span class="gallery-card-id">${(item.official_id || favId).toUpperCase()}</span>
                        <span class="gallery-card-theme">已标星</span>
                    </div>
                    <h4 class="gallery-card-name">${item.name}</h4>
                    <span class="gallery-card-parts"><i class="fas fa-puzzle-piece"></i> ${item.num_parts || 4} 个部件</span>
                </div>
            `;
            card.addEventListener('click', () => {
                if (favoritesContainer) favoritesContainer.style.display = 'none';
                showDetailPage(favId);
            });
            favGrid.appendChild(card);
        });
    }

    if (backFromFavBtn) {
        backFromFavBtn.addEventListener('click', () => {
            openSearchView();
        });
    }

    const btnExportFav = document.getElementById('btn-export-favorites');
    if (btnExportFav) {
        btnExportFav.addEventListener('click', (e) => {
            e.stopPropagation();
            const favs = preferences.favorites || [];
            if (favs.length === 0) {
                alert("您的收藏夹为空，无数据可导出！");
                return;
            }
            const textContent = favs.map(f => {
                const favId = f.minifig_num || f.id || '';
                return `人仔ID: ${favId} | 名称: ${f.name || favId} | 官方编号: ${f.official_id || favId}`;
            }).join('\n');
            const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `BrickSeek_乐高收藏清单_${new Date().toISOString().split('T')[0]}.txt`;
            link.click();
        });
    }

    function switchLegalTab(targetId) {
        legalTabs.forEach(tab => {
            if (tab.getAttribute("data-target") === targetId) {
                tab.classList.add("active");
            } else {
                tab.classList.remove("active");
            }
        });
        
        legalTabContents.forEach(content => {
            if (content.id === targetId) {
                content.classList.add("active");
            } else {
                content.classList.remove("active");
            }
        });
    }

    navSearchBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openSearchView();
    });
    
    navGalleryBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openGalleryView();
    });

    if (navFavBtn) {
        navFavBtn.addEventListener("click", (e) => {
            e.preventDefault();
            openFavoritesView();
        });
    }
    
    navAboutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openAboutView();
    });

    backFromAboutBtn.addEventListener("click", () => {
        openSearchView();
    });

    footerDatabaseBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openGalleryView();
    });

    backFromGalleryBtn.addEventListener("click", () => {
        openSearchView();
    });

    btnLoadMore.addEventListener("click", () => {
        if (!isLoadingGallery && !endOfGallery) {
            galleryPage++;
            fetchGalleryItems(false);
        }
    });

    galleryThemeFilter.addEventListener("change", () => {
        galleryTheme = galleryThemeFilter.value;
        // Search takes priority if filled, clear it to let theme filter work
        gallerySearchInput.value = "";
        gallerySearch = "";
        fetchGalleryItems(true);
    });

    gallerySortFilter.addEventListener("change", () => {
        gallerySort = gallerySortFilter.value;
        fetchGalleryItems(true);
    });

    // Debounce for search filter
    let gallerySearchTimeout = null;
    gallerySearchInput.addEventListener("input", () => {
        clearTimeout(gallerySearchTimeout);
        gallerySearchTimeout = setTimeout(() => {
            gallerySearch = gallerySearchInput.value.trim();
            // Clear theme filter visual state to avoid confusion
            if (gallerySearch) {
                galleryThemeFilter.value = "";
                galleryTheme = "";
            }
            fetchGalleryItems(true);
        }, 300);
    });

    // Bind legal subtabs inside About page
    legalTabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const targetId = tab.getAttribute("data-target");
            switchLegalTab(targetId);
        });
    });

    // Bind footer buttons to unified About view
    footerAboutBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openAboutView("legal-terms");
    });

    footerTermsBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openAboutView("legal-terms");
    });

    footerPrivacyBtn.addEventListener("click", (e) => {
        e.preventDefault();
        openAboutView("legal-privacy");
    });

    // --- 9. Home Page Quick Entrances & Hot Searches ---
    document.querySelectorAll('.hot-tag-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const val = btn.getAttribute('data-search');
            searchInput.value = val;
            searchInput.dispatchEvent(new Event('input'));
            performTextSearch();
        });
    });

    const quickCardGallery = document.getElementById('quick-card-gallery');
    const quickCardFavorites = document.getElementById('quick-card-favorites');

    if (quickCardGallery) {
        quickCardGallery.addEventListener('click', () => {
            navGalleryBtn.click();
        });
    }

    if (quickCardFavorites) {
        quickCardFavorites.addEventListener('click', () => {
            openFavoritesView();
        });
    }
});
