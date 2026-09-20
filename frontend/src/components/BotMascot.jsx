import botMascot from '../assets/bot-mascot.png'

export default function BotMascot() {
  return (
    <div className="bot-wrap" aria-hidden="true">
      <div className="bot-light-column" />
      <div className="bot-glow" />

      <img src={botMascot} alt="AI assistant mascot" className="bot-figure bot-figure-img" />
    </div>
  )
}
