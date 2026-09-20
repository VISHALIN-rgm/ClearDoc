const LINKS = [
  { label: 'Home', href: '#home' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Why Doculyze', href: '#why-doculyze' },
  { label: 'Use Cases', href: '#use-cases' },
  { label: 'FAQ', href: '#faq' },
]

export default function TopNav() {
  return (
    <nav className="top-nav">
      {LINKS.map((link) => (
        <a key={link.href} href={link.href} className="top-nav-link">
          {link.label}
        </a>
      ))}
    </nav>
  )
}
