
let deferredPrompt;
const installBanner = document.getElementById('install-banner');
const installBtn = document.getElementById('install-btn');
const closeBtn = document.getElementById('close-install-banner');

window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent Chrome 67 and earlier from automatically showing the prompt
    e.preventDefault();
    // Stash the event so it can be triggered later.
    deferredPrompt = e;

    // Check if user has already dismissed it in this session or recently
    if (!localStorage.getItem('pwa-banner-dismissed')) {
        showInstallBanner();
    }
});

function showInstallBanner() {
    if (installBanner) {
        installBanner.classList.add('show');
    }
}

if (installBtn) {
    installBtn.addEventListener('click', (e) => {
        if (!deferredPrompt) return;

        // Show the prompt
        deferredPrompt.prompt();

        // Wait for the user to respond to the prompt
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('User accepted the A2HS prompt');
            } else {
                console.log('User dismissed the A2HS prompt');
            }
            deferredPrompt = null;
            hideInstallBanner();
        });
    });
}

if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        hideInstallBanner();
        // Don't show again for 24 hours
        localStorage.setItem('pwa-banner-dismissed', Date.now());
    });
}

function hideInstallBanner() {
    if (installBanner) {
        installBanner.classList.remove('show');
    }
}

window.addEventListener('appinstalled', (evt) => {
    console.log('App foi instalado');
    hideInstallBanner();
});

// iOS basic detection
const isIos = () => {
    const userAgent = window.navigator.userAgent.toLowerCase();
    return /iphone|ipad|ipod/.test(userAgent);
}

const isInStandaloneMode = () => ('standalone' in window.navigator) && (window.navigator.standalone);

if (isIos() && !isInStandaloneMode()) {
    if (!localStorage.getItem('pwa-banner-dismissed')) {
        // Show banner with iOS instructions
        if (installBanner) {
            const bannerText = installBanner.querySelector('.banner-text');
            if (bannerText) {
                bannerText.innerHTML = 'Instale como App: toque em <span class="ios-share-icon"></span> e depois em "Adicionar à Tela de Início"';
            }
            if (installBtn) installBtn.style.display = 'none';
            showInstallBanner();
        }
    }
}
