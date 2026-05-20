import '../styles.css'
import { UIProvider } from '../lib/ui-context'

export default function App({ Component, pageProps }) {
  return (
    <UIProvider>
      <Component {...pageProps} />
    </UIProvider>
  )
}