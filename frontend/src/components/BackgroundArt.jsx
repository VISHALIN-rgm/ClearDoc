import bgGlow from '../assets/bg-glow.jpg'

export default function BackgroundArt() {
  return (
    <div
      className="bg-art"
      aria-hidden="true"
      style={{
        backgroundImage: `url(${bgGlow})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      }}
    />
  )
}
