// ============================================================
// Particle System 3D — Canvas Background
// ============================================================

interface Particle {
  x: number; y: number; z: number
  vx: number; vy: number; vz: number
  size: number; color: string; opacity: number
  connectionRadius: number
}

export function createParticleBackground(container: HTMLElement): () => void {
  const canvas = document.createElement('canvas')
  canvas.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    pointer-events: none; z-index: 0;
  `
  container.prepend(canvas)

  const ctx = canvas.getContext('2d')!
  const colors = ['#0f766e', '#2563eb', '#0e7490', '#b7791f', '#102233']
  const particles: Particle[] = []
  let animId: number
  let mouse = { x: -9999, y: -9999 }

  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)

  document.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX
    mouse.y = e.clientY
  })

  // Create particles
  for (let i = 0; i < 80; i++) {
    particles.push({
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight,
      z: Math.random() * 500 + 100,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      vz: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 2 + 1,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: Math.random() * 0.6 + 0.2,
      connectionRadius: Math.random() * 150 + 80,
    })
  }

  const project = (p: Particle) => {
    const fov = 500
    const scale = fov / (fov + p.z)
    return {
      x: p.x * scale + (canvas.width / 2) * (1 - scale),
      y: p.y * scale + (canvas.height / 2) * (1 - scale),
      scale,
    }
  }

  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      const pi = project(particles[i])
      for (let j = i + 1; j < particles.length; j++) {
        const pj = project(particles[j])
        const dx = pi.x - pj.x
        const dy = pi.y - pj.y
        const dist = Math.sqrt(dx * dx + dy * dy)

        if (dist < particles[i].connectionRadius) {
          const alpha = (1 - dist / particles[i].connectionRadius) * 0.15
          ctx.beginPath()
          ctx.strokeStyle = `rgba(15, 118, 110, ${alpha})`
          ctx.lineWidth = 0.5
          ctx.moveTo(pi.x, pi.y)
          ctx.lineTo(pj.x, pj.y)
          ctx.stroke()
        }
      }
    }

    // Draw particles
    particles.forEach(p => {
      const { x, y, scale } = project(p)

      // Mouse repulsion
      const mdx = x - mouse.x
      const mdy = y - mouse.y
      const mdist = Math.sqrt(mdx * mdx + mdy * mdy)
      if (mdist < 100) {
        p.vx += (mdx / mdist) * 0.3
        p.vy += (mdy / mdist) * 0.3
      }

      // Damping
      p.vx *= 0.99; p.vy *= 0.99; p.vz *= 0.99

      // Move
      p.x += p.vx; p.y += p.vy; p.z += p.vz

      // Depth oscillation
      if (p.z < 50 || p.z > 800) p.vz *= -1

      // Wrap edges
      if (p.x < 0) p.x = canvas.width
      if (p.x > canvas.width) p.x = 0
      if (p.y < 0) p.y = canvas.height
      if (p.y > canvas.height) p.y = 0

      // Draw glow
      const size = (p.size * scale * 3)
      const gradient = ctx.createRadialGradient(x, y, 0, x, y, size * 3)
      gradient.addColorStop(0, p.color + 'aa')
      gradient.addColorStop(1, p.color + '00')
      ctx.beginPath()
      ctx.fillStyle = gradient
      ctx.arc(x, y, size * 3, 0, Math.PI * 2)
      ctx.fill()

      // Draw core
      ctx.beginPath()
      ctx.fillStyle = p.color
      ctx.globalAlpha = p.opacity * scale
      ctx.arc(x, y, size, 0, Math.PI * 2)
      ctx.fill()
      ctx.globalAlpha = 1
    })

    animId = requestAnimationFrame(animate)
  }

  animate()

  return () => {
    cancelAnimationFrame(animId)
    window.removeEventListener('resize', resize)
    canvas.remove()
  }
}
