const GRINDOSAUR_URL = 'https://www.grindosaur.com/en/games/digimon-story-time-stranger'
const AUTHOR = 'Melodie X'

function Footer() {
  return (
    <footer className="footer">
      Unofficial fan project, not affiliated with Bandai Namco · Data via{' '}
      <a href={GRINDOSAUR_URL} target="_blank" rel="noopener noreferrer">Grindosaur</a>
      {' '}· © {new Date().getFullYear()} {AUTHOR}
    </footer>
  )
}

export default Footer
