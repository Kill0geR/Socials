// static/script.js
document.addEventListener('DOMContentLoaded', () => {
  const linkInput     = document.getElementById('linkInput');
  const formatSection = document.getElementById('formatSection');
  let   selectEl      = document.getElementById('formatSelect');
  const errorMessage  = document.getElementById('errorMessage');

  // create real <select> if missing
  if (!selectEl) {
    selectEl = document.createElement('select');
    selectEl.id   = 'formatSelect';
    selectEl.name = 'format';
    selectEl.style.display = 'none';
    formatSection.appendChild(selectEl);
  }

  // dropdown UI refs
  const wrapper          = document.querySelector('.custom-select-wrapper');
  const trigger          = wrapper.querySelector('.custom-select__trigger');
  const optionsContainer = wrapper.querySelector('.custom-options');
  const current          = document.getElementById('currentOption');

  function rebuildCustomDropdown(platform) {
    optionsContainer.innerHTML = '';
    selectEl.innerHTML = '';
    formats[platform].forEach(opt => {
      const item = document.createElement('div');
      item.classList.add('custom-option');
      item.dataset.value = opt.value;
      item.textContent   = opt.text;
      optionsContainer.appendChild(item);

      const optionEl = document.createElement('option');
      optionEl.value       = opt.value;
      optionEl.textContent = opt.text;
      selectEl.appendChild(optionEl);
    });
    current.textContent = 'Format wählen';
    selectEl.value = '';
  }

  // brand palettes
  const colorPresets = {
    default:   { gradientStart:'#00ffe0', gradientEnd:'#0078ff', bgStart:'#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#00ffe0' },
    youtube:   { gradientStart:'#FF0000', gradientEnd:'#CC0000', bgStart:'#2A2A2A', bgEnd:'#1A1A1A', textColor:'#fff', shadowColor:'#FF0000' },
    instagram: { gradientStart:'#833AB4', gradientEnd:'#FD1D1D', bgStart:'#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#FCAF45' },
    facebook:  { gradientStart:'#1877F2', gradientEnd:'#4267B2', bgStart:'#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#1877F2' },
    tiktok:    { gradientStart:'#69C9D0', gradientEnd:'#EE1D52', bgStart:'#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#69C9D0' }
  };

  let currentPlatform = 'default';

  function crossfadeTo(preset) {
    const root = document.documentElement.style;
    // 1) build overlay
    const overlay = document.createElement('div');
    overlay.className = 'gradient-overlay';
    overlay.style.background =
      `radial-gradient(circle at top, ${preset.bgStart}, ${preset.bgEnd})`;
    document.body.appendChild(overlay);
    // 2) fade overlay in...
    requestAnimationFrame(() => {
      overlay.style.opacity = '1';
    });
    overlay.addEventListener('transitionend', function fadeInDone() {
      overlay.removeEventListener('transitionend', fadeInDone);
      // 3) swap vars underneath
      root.setProperty('--gradient-start',   preset.gradientStart);
      root.setProperty('--gradient-end',     preset.gradientEnd);
      root.setProperty('--bg-gradient',      `radial-gradient(circle at top, ${preset.bgStart}, ${preset.bgEnd})`);
      root.setProperty('--text-color',       preset.textColor);
      root.setProperty('--btn-hover-shadow', preset.shadowColor);
      // 4) fade overlay out
      overlay.style.opacity = '0';
      overlay.addEventListener('transitionend', () => {
        document.body.removeChild(overlay);
      }, { once: true });
    }, { once: true });
  }

  function applyColorScheme(key) {
    const preset = colorPresets[key] || colorPresets.default;
    crossfadeTo(preset);
  }

  // init default look
  applyColorScheme('default');

  // dropdown toggle
  trigger.addEventListener('click', () => {
    wrapper.querySelector('.custom-select').classList.toggle('open');
  });
  window.addEventListener('click', e => {
    if (!wrapper.contains(e.target)) {
      wrapper.querySelector('.custom-select').classList.remove('open');
    }
  });

  // option select
  optionsContainer.addEventListener('click', e => {
    const item = e.target.closest('.custom-option');
    if (!item) return;
    current.textContent = item.textContent;
    optionsContainer.querySelector('.selected')?.classList.remove('selected');
    item.classList.add('selected');
    selectEl.value = item.dataset.value;
    wrapper.querySelector('.custom-select').classList.remove('open');
  });

  // URL typing
  linkInput.addEventListener('input', () => {
    const url      = linkInput.value.trim();
    const platform = detectPlatform(url) || 'default';

    // only on real change
    if (platform !== currentPlatform) {
      currentPlatform = platform;
      applyColorScheme(platform);
    }

    if (!url) {
      formatSection.classList.remove('visible');
      errorMessage.textContent = '';
    }
    else if (platform !== 'default') {
      rebuildCustomDropdown(platform);
      formatSection.classList.add('visible');
      errorMessage.textContent = '';
    }
    else {
      formatSection.classList.remove('visible');
      errorMessage.textContent = 'Unbekannte Plattform.';
    }
  });
});

// formats & detect (unchanged)
const formats = {
  instagram: [ {value:'insta_profile_picture',text:'Profilbild'}, {value:'insta_reels',text:'Reels'}, {value:'insta_photos',text:'Fotos/Video'} ],
  youtube:   [ {value:'yt_mp4',text:'MP4 (Video)'}, {value:'yt_mp3',text:'MP3 (Audio)'} ],
  facebook:  [ {value:'face_profile_picture',text:'Profilbild'}, {value:'face_photos',text:'Fotos/Video'}, {value:'face_reels',text:'Reels'} ],
  tiktok:    [ {value:'tik_profile_picture',text:'Profilbild'}, {value:'tik_videos',text:'Videos'} ]
};
function detectPlatform(u) {
  u = u.toLowerCase();
  if (u.includes('instagram.com')) return 'instagram';
  if (u.includes('youtube.com')||u.includes('youtu.be')) return 'youtube';
  if (u.includes('facebook.com')) return 'facebook';
  if (u.includes('tiktok.com')) return 'tiktok';
  return null;
}
function validateInput() {
  const v = document.getElementById('linkInput').value.trim();
  const e = document.getElementById('errorMessage');
  if (!v) { e.textContent = 'Please insert an URL'; return false; }
  e.textContent = ''; return true;
}
