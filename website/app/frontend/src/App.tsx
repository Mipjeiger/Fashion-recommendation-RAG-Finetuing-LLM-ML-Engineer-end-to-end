import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './store/themeStore'
import EcommercePage from './pages/EcommercePage'
import AdminDashboard from './pages/AdminDashboard'
import Layout from './components/common/Layout'

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<EcommercePage />} />
            <Route path="/admin" element={<AdminDashboard />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  )
}

export default App
