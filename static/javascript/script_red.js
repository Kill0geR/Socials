document.addEventListener('DOMContentLoaded', () => {
  const linkInput       = document.getElementById('linkInput');
  const formatSection   = document.getElementById('formatSection');
  let selectEl          = document.getElementById('formatSelect');
  const errorMessage    = document.getElementById('errorMessage');
  const platformDisplay = document.getElementById('platformDisplay');

  platformDisplay.textContent = "Reddit";
  platformDisplay.classList.add('visible');

  const platformNames = {
    instagram: 'Instagram',
    youtube:   'YouTube',
    facebook:  'Facebook',
    tiktok:    'TikTok',
    twitter:   'X',
    twitterReal : "Twitter",
    reddit: "Reddit",
    pinterest: "Pinterest",
  };

  if (!selectEl) {
    selectEl = document.createElement('select');
    selectEl.id   = 'formatSelect';
    selectEl.name = 'format';
    selectEl.style.display = 'none';
    formatSection.appendChild(selectEl);
  }

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
    current.textContent = 'Choose format';
    selectEl.value = '';
  }

   const colorPresets = {
    default:   { gradientStart: '#FF4500', gradientEnd:'#FF7043', bgStart:'#1c1c1c', bgEnd:'#2a2a2a', textColor:'#ffffff', shadowColor:'#FF4500'},
    youtube:   { gradientStart:'#FF0000', gradientEnd:'#CC0000', bgStart:'#2A2A2A', bgEnd:'#1A1A1A', textColor:'#fff', shadowColor:'#FF0000' },
    instagram: { gradientStart:'#833AB4', gradientEnd:'#FD1D1D', bgStart:'#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#FCAF45' },
    facebook:  { gradientStart:'#1877F2', gradientEnd:'#4267B2', bgStart:'#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#1877F2' },
    tiktok:    { gradientStart:'#69C9D0', gradientEnd:'#EE1D52', bgStart:'#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#69C9D0' },
    twitter:   { gradientStart:'#2c2c2c', gradientEnd:'#444', bgStart:'#121212', bgEnd:'#1e1e1e', textColor:'#ffffff', shadowColor:'#1DA1F2' },
    twitterReal: { gradientStart:'#1DA1F2', gradientEnd:'#0d8ddb', bgStart:'#0a0f1c', bgEnd:'#1a2b3c', textColor:'#ffffff', shadowColor:'#1DA1F2' },
    reddit:    { gradientStart: '#FF4500', gradientEnd:'#FF7043', bgStart:'#1c1c1c', bgEnd:'#2a2a2a', textColor:'#ffffff', shadowColor:'#FF4500'},
    pinterest: { gradientStart: '#E60023', gradientEnd:'#FFCDD2', bgStart: '#0d0d0d', bgEnd:'#1a1a1a', textColor:'#fff', shadowColor:'#E60023'}
  };

  let currentPlatform = 'default';

  function crossfadeTo(preset) {
    const root = document.documentElement.style;
    const overlay = document.createElement('div');
    overlay.className = 'gradient-overlay';
    overlay.style.background =
      `radial-gradient(circle at top, ${preset.bgStart}, ${preset.bgEnd})`;
    document.body.appendChild(overlay);
    requestAnimationFrame(() => { overlay.style.opacity = '1'; });
    overlay.addEventListener('transitionend', function fadeInDone() {
      overlay.removeEventListener('transitionend', fadeInDone);
      root.setProperty('--gradient-start',   preset.gradientStart);
      root.setProperty('--gradient-end',     preset.gradientEnd);
      root.setProperty('--bg-gradient',      `radial-gradient(circle at top, ${preset.bgStart}, ${preset.bgEnd})`);
      root.setProperty('--text-color',       preset.textColor);
      root.setProperty('--btn-hover-shadow', preset.shadowColor);
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

  applyColorScheme('default');

  trigger.addEventListener('click', () => {
    wrapper.querySelector('.custom-select').classList.toggle('open');
  });
  window.addEventListener('click', e => {
    if (!wrapper.contains(e.target)) {
      wrapper.querySelector('.custom-select').classList.remove('open');
    }
  });

  optionsContainer.addEventListener('click', e => {
    const item = e.target.closest('.custom-option');
    if (!item) return;
    current.textContent = item.textContent;
    optionsContainer.querySelector('.selected')?.classList.remove('selected');
    item.classList.add('selected');
    selectEl.value = item.dataset.value;
    wrapper.querySelector('.custom-select').classList.remove('open');
  });

  linkInput.addEventListener('input', () => {
    const url      = linkInput.value.trim();
    const platform = detectPlatform(url) || 'default';
    const format   = detectFormat(platform, url) || 'default';

    const displayName = platformNames[platform] || '';
    if (displayName) {
      platformDisplay.textContent = displayName;
      platformDisplay.classList.add('visible');
    }

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
      
      if (format !== 'default') {
        selectEl.value = format;
        const opt = formats[platform].find(opt => opt.value === format);
        current.textContent = opt ? opt.text : 'Choose format';
        optionsContainer.querySelector(`[data-value="${format}"]`)?.classList.add('selected');
      }
    }
    else {
      formatSection.classList.remove('visible');
      errorMessage.textContent = 'Unknown Platform';
    }
  });
});

const formats = {
  instagram: [ {value:'insta_profile_picture',text:'Profile picture'}, {value:'insta_reels',text:'Reels'}, {value:'insta_photos',text:'Photos/Video'} ],
  youtube:   [ {value:'yt_mp4',text:'MP4 (Video)'}, {value:'yt_mp3',text:'MP3 (Audio)'} ],
  facebook:  [ {value:'face_profile_picture',text:'Profile picture'}, {value:'face_photos',text:'Photos/Posts'}, {value:'face_reels',text:'Reels/Video'} ],
  tiktok:    [ {value:'tik_profile_picture',text:'Profile picture'}, {value:'tik_videos',text:'Videos'} ],
  twitter:    [ {value:'twitter_videos',text:'Video/Photos'}, {value:'twitter_profile_picture',text:'Profile picture'} ],
  twitterReal:    [ {value:'twitter_videos',text:'Video/Photos'}, {value:'twitter_profile_picture',text:'Profile picture'} ],
  reddit:    [ {value:'reddit_profile_pic',text:'Profile picture'}, {value:'reddit_photos',text:'Photos/Video'}],
  pinterest:    [ {value:'pin_profile_pic',text:'Profile picture'}, {value:'pin_media',text:'Foto/Video'}]
};

function detectPlatform(u) {
  u = u.toLowerCase();
  // if (u.includes('instagram.com')) return 'instagram';
  // if (u.includes('youtube.com') || u.includes('youtu.be')) return 'youtube';
  // if (u.includes('facebook.com')) return 'facebook';
  // if (u.includes('tiktok.com')) return 'tiktok';
  // if (u.includes('x.com')) return 'twitter';
  // if (u.includes('twitter.com')) return 'twitterReal';
  if (u.includes('reddit.com')) return 'reddit';
  // if (u.includes('pinterest.com')) return 'pinterest';
  // if (u.includes('pin.it')) return 'pinterest';
  return null;
}
function detectFormat(platform, link) {
  link = link.toLowerCase();

  // if (platform === "instagram") {
  //   const parts = link.split('instagram.com/');
  //   const path = parts.at(-1).split("/")[0];
  //
  //   if (!(path === "p" || path === 'reels' || path ==='reel' || link.includes("/p/"))) {
  //     return "insta_profile_picture";
  //   } else if (path ==='reels' || path ==='reel') {
  //     return "insta_reels";
  //   } else {
  //     return 'insta_photos';
  //   }
  // }

  // if (platform === "facebook") {
  //   const parts = link.split('facebook.com/');
  //   const path = parts.at(-1).split("/")[0];
  //
  //   if (!(path === "share" || path === "reels" || path === "reel")) {
  //     return "face_profile_picture";
  //   } else if (path ==='reels' || path ==='reel' || parts.at(-1).split("/")[1] === "v") {
  //     return "face_reels";
  //   } else {
  //     return 'face_photos';
  //   }
  // }
  //
  // if (platform === "twitter") {
  //   const parts = link.split('/');
  //   if (parts.length > 4) {
  //     return 'twitter_videos';
  //   } else {
  //     return 'twitter_profile_picture';
  //   }
  // }

  if (platform === "reddit") {
    const parts = link.split('/');
    if (parts.length <= 6) {
      return 'reddit_profile_pic';
    } else {
      return 'reddit_photos';
    }
  }
  //
  // if (platform === "pinterest") {
  //   if (link.includes("/pin/")) {
  //     return 'pin_media';
  //   } else {
  //     return 'pin_profile_pic';
  //   }
  // }
  //
  if (platform === "tiktok") {
    const parts = link.split('/');
    const path = parts.at(-1);
    console.log(path);
    if (path.includes('@')) {
      return 'tik_profile_picture';
    } else {
      return 'tik_videos';
    }
  }

  return null;
}

function validateInput() {
  const v = document.getElementById('linkInput').value.trim();
  const e = document.getElementById('errorMessage');
  const f = document.getElementById('currentOption').textContent;
  console.log(f);
  if (f === "Choose format") { e.textContent = 'Please select a format'; return false; }

  if (!v) { e.textContent = 'Please insert an URL'; return false; }
  e.textContent = ''; return true;
}


const form = document.getElementById('mainForm');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const submitButton = document.getElementById('submitBtn');

form.addEventListener('submit', (event) => {
  const link = document.getElementById('linkInput').value.trim();
  const format = document.getElementById('currentOption').textContent;

  if (link !== "" && format !== "Choose format") {
    event.preventDefault();

  submitButton.disabled = true;
  submitButton.classList.add('disabled');

  const formData = new FormData(form);

  progressBar.style.display = 'block';
  progressFill.style.width = '0%';

  let width = 0;
  let isFinished = false;
  const randomTimeout = Math.floor(Math.random() * (500 - 250 + 1)) + 250;

  const interval = setInterval(() => {
    if (width >= 90 || isFinished) {
      clearInterval(interval);
    } else {
      width += 2;
      progressFill.style.width = width + '%';
    }
  }, randomTimeout);

  fetch(form.action, {
    method: 'POST',
    body: formData
  })
  .then(response => {
    isFinished = true;
    progressFill.style.width = '100%';

    setTimeout(() => {
      progressBar.style.display = 'none';
      window.location.href = response.url;

      submitButton.disabled = false;
      submitButton.classList.remove('disabled');
    }, 300);
  })
  .catch(error => {
    console.error('Fehler:', error);
    clearInterval(interval);

    submitButton.disabled = false;
    submitButton.classList.remove('disabled');
  });
  }
});
