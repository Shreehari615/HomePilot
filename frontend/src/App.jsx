import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useDarkMode } from './hooks/useDarkMode';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Chat from './pages/Chat';
import PropertyDetails from './pages/PropertyDetails';
import History from './pages/History';

export default function App() {
  const { isDark, toggleDark } = useDarkMode();

  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar isDark={isDark} toggleDark={toggleDark} />
        <main style={{ flex: 1, paddingTop: 'var(--navbar-height)' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/property/:id" element={<PropertyDetails />} />
            <Route path="/history" element={<History />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
