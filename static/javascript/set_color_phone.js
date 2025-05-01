const colorPresetsPhone = {
    faq:   { gradientStart:'#0078ff', gradientEnd:'#00ffe0' },
    youtube:   { gradientStart:'#FF0000', gradientEnd:'#CC0000' },
    instagram: { gradientStart:'#833AB4', gradientEnd:'#FD1D1D' },
    facebook:  { gradientStart:'#1877F2', gradientEnd:'#4267B2' },
    tiktok:    { gradientStart:'#69C9D0', gradientEnd:'#EE1D52' },
    twitter:   { gradientStart:'#2c2c2c', gradientEnd:'#444' },
    twitterReal: { gradientStart:'#1DA1F2', gradientEnd:'#0d8ddb' },
    reddit:    { gradientStart:'#FF4500', gradientEnd:'#FF7043' },
    pinterest: { gradientStart:'#E60023', gradientEnd:'#FFCDD2' }
  };

  const linksPhone = document.querySelectorAll('#mobile-menu a');

  linksPhone.forEach(link => {
    const platform = link.dataset.platform;
    if (colorPresetsPhone[platform]) {
      const { gradientStart, gradientEnd } = colorPresetsPhone[platform];
      link.style.background = `linear-gradient(to right, ${gradientStart}, ${gradientEnd})`;
      link.style.color = '#fff';
      link.style.padding = '10px';
      link.style.display = 'block';
      link.style.textDecoration = 'none';
    }
  });