
let deferredPrompt;
const pwaOverlay = document.getElementById('pwa-install-overlay');
const installBtn = document.getElementById('pwa-install-btn');
const closeBtn = document.getElementById('pwa-close-modal');
const maybeLaterBtn = document.getElementById('pwa-maybe-later');

console.log('PWA script carregado. Overlay:', pwaOverlay);

window.addEventListener('beforeinstallprompt', (e) => {
    // Impedir que o Chrome mostre o prompt automático
    e.preventDefault();
    // Salvar o evento
    deferredPrompt = e;

    // Verificar se o usuário já dispensou permanentemente
    if (!localStorage.getItem('pwa-modal-dismissed')) {
        showPwaModal();
    }
});

function showPwaModal() {
    if (pwaOverlay) {
        pwaOverlay.classList.add('show');
    }
}

function hidePwaModal(permanent = false) {
    if (pwaOverlay) {
        pwaOverlay.classList.remove('show');
        if (permanent) {
            localStorage.setItem('pwa-modal-dismissed', 'true');
        }
    }
}

if (installBtn) {
    installBtn.addEventListener('click', (e) => {
        if (!deferredPrompt) return;

        deferredPrompt.prompt();

        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('Usuário aceitou a instalação');
                localStorage.setItem('pwa-modal-dismissed', 'true');
            } else {
                console.log('Usuário recusou a instalação');
            }
            deferredPrompt = null;
            hidePwaModal();
        });
    });
}

if (closeBtn) {
    closeBtn.addEventListener('click', () => hidePwaModal(true));
}

if (maybeLaterBtn) {
    maybeLaterBtn.addEventListener('click', () => hidePwaModal(false));
}

window.addEventListener('appinstalled', (evt) => {
    console.log('PWA instalado com sucesso');
    localStorage.setItem('pwa-modal-dismissed', 'true');
    hidePwaModal();
});

// Detecção básica de iOS
const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test(userAgent);
}

const isInStandaloneMode = () => ('standalone' in window.navigator) && (window.navigator.standalone);

if (isIos() && !isInStandaloneMode()) {
    if (!localStorage.getItem('pwa-modal-dismissed')) {
        const iosInstructions = document.getElementById('pwa-ios-instructions');
        const pwaMainContent = document.getElementById('pwa-main-content');

        if (iosInstructions && pwaMainContent) {
            pwaMainContent.style.display = 'none';
            iosInstructions.style.display = 'block';
            showPwaModal();
        }
    }
}
