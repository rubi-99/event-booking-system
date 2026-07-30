import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Ticket, Calendar, MapPin, User, LogOut, ShieldAlert, PlusCircle, Menu, X } from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="sticky top-0 z-50 glass-panel border-b border-gray-800 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="p-2 rounded-xl bg-purple-600/20 text-purple-400 group-hover:bg-purple-600/30 transition-all">
              <Ticket className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold font-heading text-gradient tracking-tight">
              Eventify
            </span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/events" className="flex items-center space-x-1.5 text-gray-300 hover:text-purple-400 text-sm font-medium transition-colors">
              <Calendar className="w-4 h-4" />
              <span>Events</span>
            </Link>

            <Link to="/venues" className="flex items-center space-x-1.5 text-gray-300 hover:text-purple-400 text-sm font-medium transition-colors">
              <MapPin className="w-4 h-4" />
              <span>Venues</span>
            </Link>

            {/* Role Gated Navigation Items */}
            {user && (user.role === 'organizer' || user.role === 'admin') && (
              <Link to="/organizer/events/new" className="flex items-center space-x-1.5 text-purple-400 hover:text-purple-300 text-sm font-medium transition-colors">
                <PlusCircle className="w-4 h-4" />
                <span>Create Event</span>
              </Link>
            )}

            {user && user.role === 'admin' && (
              <Link to="/admin" className="flex items-center space-x-1.5 text-amber-400 hover:text-amber-300 text-sm font-semibold bg-amber-500/10 px-3 py-1.5 rounded-lg border border-amber-500/20 transition-all">
                <ShieldAlert className="w-4 h-4" />
                <span>Admin Console</span>
              </Link>
            )}
          </div>

          {/* Right Action Menu */}
          <div className="hidden md:flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-3">
                <Link to="/me/bookings" className="flex items-center space-x-1.5 text-sm font-medium text-gray-200 hover:text-white px-3 py-1.5 rounded-lg bg-gray-800/60 hover:bg-gray-800 transition-colors border border-gray-700/50">
                  <Ticket className="w-4 h-4 text-purple-400" />
                  <span>My Bookings</span>
                </Link>

                <Link to="/me" className="flex items-center space-x-2 text-sm text-gray-300 hover:text-white px-3 py-1.5 rounded-lg bg-gray-800/40 hover:bg-gray-800/80 transition-colors">
                  <User className="w-4 h-4 text-purple-400" />
                  <span>{user.first_name}</span>
                </Link>

                <button
                  onClick={handleLogout}
                  className="p-2 text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <Link to="/auth/login" className="text-sm font-medium text-gray-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-gray-800 transition-colors">
                  Log In
                </Link>
                <Link to="/auth/signup" className="text-sm font-semibold text-white px-4 py-2 rounded-xl btn-gradient">
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-gray-400 hover:text-white"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden glass-panel border-t border-gray-800 px-4 pt-2 pb-6 space-y-3">
          <Link to="/events" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-gray-200 hover:bg-gray-800">
            Events
          </Link>
          <Link to="/venues" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-gray-200 hover:bg-gray-800">
            Venues
          </Link>
          {user ? (
            <>
              <Link to="/me/bookings" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-purple-400 hover:bg-purple-950/30">
                My Bookings
              </Link>
              <Link to="/me" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-gray-200 hover:bg-gray-800">
                Profile ({user.first_name})
              </Link>
              {user.role === 'admin' && (
                <Link to="/admin" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-md text-base font-medium text-amber-400 hover:bg-amber-950/30">
                  Admin Console
                </Link>
              )}
              <button onClick={() => { handleLogout(); setMobileMenuOpen(false); }} className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-rose-400 hover:bg-rose-950/30">
                Log Out
              </button>
            </>
          ) : (
            <div className="pt-2 flex flex-col space-y-2">
              <Link to="/auth/login" onClick={() => setMobileMenuOpen(false)} className="w-full text-center py-2 rounded-lg bg-gray-800 text-white font-medium">
                Log In
              </Link>
              <Link to="/auth/signup" onClick={() => setMobileMenuOpen(false)} className="w-full text-center py-2 rounded-lg btn-gradient text-white font-semibold">
                Sign Up
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};
