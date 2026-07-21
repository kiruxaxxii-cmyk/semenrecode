document.addEventListener('DOMContentLoaded', () => {
  // Deep sunset glowing colors
  const colors = ['#ff8a65', '#ffd54f', '#ff5252', '#b388ff'];
  let lastSpawn = 0;
  
  document.addEventListener('mousemove', (e) => {
    const now = Date.now();
    // Spawn faster for a smoother trail
    if (now - lastSpawn > 20) {
      spawnParticle(e.clientX, e.clientY);
      lastSpawn = now;
    }
  });

  function spawnParticle(x, y) {
    const particle = document.createElement('div');
    particle.className = 'cursor-particle';
    
    // Slightly larger for the glow effect
    const size = Math.random() * 12 + 6;
    particle.style.width = `${size}px`;
    particle.style.height = `${size}px`;
    
    // Tighter scatter for a neat trail
    const offsetX = (Math.random() - 0.5) * 10;
    const offsetY = (Math.random() - 0.5) * 10;
    particle.style.left = `${x + offsetX}px`;
    particle.style.top = `${y + offsetY}px`;
    
    const color = colors[Math.floor(Math.random() * colors.length)];
    particle.style.background = color;
    
    // Heavy blur shadow for an "orb" effect
    particle.style.boxShadow = `0 0 ${size * 3}px ${size}px ${color}`;
    
    document.body.appendChild(particle);
    
    setTimeout(() => {
      particle.remove();
    }, 600);
  }
});
