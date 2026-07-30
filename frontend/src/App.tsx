import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { LoginPage, SignupPage } from './pages/AuthPages';
import { EventListPage, EventDetailPage } from './pages/EventPages';
import { MyBookingsPage, ProfilePage } from './pages/BookingPages';
import { VenueListPage, VenueDetailPage } from './pages/VenuePages';
import { AdminDashboardPage } from './pages/AdminDashboard';
import { CreateEventPage } from './pages/OrganizerPages';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-[#0b0f19] text-gray-100 flex flex-col font-sans selection:bg-purple-500/30 selection:text-purple-300">
          <Navbar />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<Navigate to="/events" replace />} />
              <Route path="/events" element={<EventListPage />} />
              <Route path="/events/:id" element={<EventDetailPage />} />

              <Route path="/auth/login" element={<LoginPage />} />
              <Route path="/auth/signup" element={<SignupPage />} />

              <Route path="/me" element={<ProfilePage />} />
              <Route path="/me/bookings" element={<MyBookingsPage />} />

              <Route path="/venues" element={<VenueListPage />} />
              <Route path="/venues/:id" element={<VenueDetailPage />} />

              <Route path="/admin" element={<AdminDashboardPage />} />
              <Route path="/organizer/events/new" element={<CreateEventPage />} />

              <Route path="*" element={<Navigate to="/events" replace />} />
            </Routes>
          </main>
          
          <footer className="glass-panel border-t border-gray-800 py-6 text-center text-xs text-gray-500">
            Eventify Platform • High-Scale Ticket Reservation Engine
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
