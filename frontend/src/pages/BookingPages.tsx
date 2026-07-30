import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Ticket, Calendar, Clock, AlertCircle, RefreshCcw } from 'lucide-react';

interface BookingItem {
  id: string;
  user_id: string;
  event_id: string;
  num_tickets: number;
  total_price: string | number;
  status: 'pending' | 'confirmed' | 'cancelled' | 'refunded';
  expires_at?: string;
  created_at: string;
  event?: {
    title: string;
    category: string;
    start_time: string;
    ticket_price: string | number;
  };
}

export const MyBookingsPage: React.FC = () => {
  const [bookings, setBookings] = useState<BookingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [webhookLoading, setWebhookLoading] = useState<string | null>(null);

  const fetchMyBookings = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiClient.get<BookingItem[]>('/bookings/my');
      setBookings(res.data);
    } catch (err: any) {
      setError('Failed to fetch ticket bookings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyBookings();
  }, []);

  const handleSimulatePayment = async (bookingId: string) => {
    setWebhookLoading(bookingId);
    try {
      await apiClient.post('/bookings/webhook', {
        booking_id: bookingId,
        status: 'payment_success',
        transaction_id: `tx_${Date.now()}`,
      });
      fetchMyBookings();
    } catch (err: any) {
      alert('Payment processing failed');
    } finally {
      setWebhookLoading(null);
    }
  };

  const handleCancelBooking = async (bookingId: string) => {
    if (!confirm('Are you sure you want to cancel this booking?')) return;
    try {
      await apiClient.post(`/bookings/${bookingId}/cancel`);
      fetchMyBookings();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel booking.');
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold font-heading text-white">My Ticket Reservations</h1>
          <p className="text-gray-400 text-sm mt-1">Manage your active holds and confirmed ticket passes</p>
        </div>
        <button onClick={fetchMyBookings} className="p-2.5 rounded-xl bg-gray-800/80 hover:bg-gray-800 text-gray-300 hover:text-white transition-colors">
          <RefreshCcw className="w-5 h-5" />
        </button>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="glass-panel p-6 rounded-2xl h-32 animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="glass-panel p-8 text-center rounded-2xl text-rose-400">
          <AlertCircle className="w-8 h-8 mx-auto mb-2" />
          <p>{error}</p>
        </div>
      ) : bookings.length === 0 ? (
        <div className="glass-panel p-16 text-center rounded-2xl max-w-md mx-auto">
          <Ticket className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">No Bookings Yet</h3>
          <p className="text-gray-400 text-sm">Browse the events catalog to reserve your first tickets.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {bookings.map((b) => (
            <div key={b.id} className="glass-panel p-6 rounded-2xl border border-gray-800/80 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              
              {/* Event Info */}
              <div className="space-y-2">
                <div className="flex items-center space-x-3">
                  <h3 className="text-lg font-bold text-white">{b.event?.title || 'Event Booking'}</h3>
                  <StatusBadge status={b.status} />
                </div>

                <div className="flex flex-wrap gap-4 text-xs text-gray-400">
                  <div className="flex items-center space-x-1">
                    <Ticket className="w-3.5 h-3.5 text-purple-400" />
                    <span>{b.num_tickets} Ticket(s)</span>
                  </div>

                  <div className="flex items-center space-x-1">
                    <Calendar className="w-3.5 h-3.5 text-purple-400" />
                    <span>{b.event?.start_time ? new Date(b.event.start_time).toLocaleString() : new Date(b.created_at).toLocaleDateString()}</span>
                  </div>

                  <div className="font-semibold text-white">
                    Total: ${Number(b.total_price).toFixed(2)}
                  </div>
                </div>

                {b.status === 'pending' && b.expires_at && (
                  <div className="flex items-center space-x-1.5 text-xs text-amber-400 mt-2">
                    <Clock className="w-3.5 h-3.5" />
                    <span>Hold Expiry: {new Date(b.expires_at).toLocaleTimeString()}</span>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center space-x-3 w-full md:w-auto justify-end">
                {b.status === 'pending' && (
                  <button
                    onClick={() => handleSimulatePayment(b.id)}
                    disabled={webhookLoading === b.id}
                    className="px-4 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-500 rounded-xl transition-colors shadow-lg shadow-emerald-600/30"
                  >
                    {webhookLoading === b.id ? 'Processing...' : 'Complete Payment Now'}
                  </button>
                )}

                {b.status !== 'cancelled' && b.status !== 'refunded' && (
                  <button
                    onClick={() => handleCancelBooking(b.id)}
                    className="px-4 py-2 text-xs font-semibold text-rose-400 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 rounded-xl transition-colors"
                  >
                    Cancel Hold
                  </button>
                )}
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};

export const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [firstName, setFirstName] = useState(user?.first_name || '');
  const [lastName, setLastName] = useState(user?.last_name || '');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg('');
    try {
      const res = await apiClient.put('/auth/me', {
        first_name: firstName,
        last_name: lastName,
      });
      updateUser(res.data);
      setMsg('Profile updated successfully!');
    } catch (err: any) {
      alert('Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) return null;

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="glass-panel p-8 rounded-3xl border border-gray-800">
        
        <div className="flex items-center space-x-4 mb-8">
          <div className="w-16 h-16 rounded-2xl bg-purple-600/20 text-purple-400 flex items-center justify-center font-bold text-2xl">
            {user.first_name[0]}{user.last_name[0]}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">{user.first_name} {user.last_name}</h2>
            <p className="text-xs text-purple-400 font-semibold uppercase tracking-wider mt-0.5">{user.role} Account</p>
          </div>
        </div>

        {msg && (
          <div className="mb-6 p-4 rounded-xl bg-emerald-500/10 text-emerald-400 text-sm">
            {msg}
          </div>
        )}

        <form onSubmit={handleUpdateProfile} className="space-y-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">First Name</label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full bg-gray-900/90 border border-gray-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-purple-500"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Last Name</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full bg-gray-900/90 border border-gray-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-purple-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Email Address</label>
            <input
              type="email"
              value={user.email}
              disabled
              className="w-full bg-gray-950 border border-gray-800 rounded-xl px-4 py-2.5 text-gray-500 cursor-not-allowed"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 btn-gradient font-bold text-white rounded-xl shadow-lg disabled:opacity-50"
          >
            {loading ? 'Saving Changes...' : 'Save Profile Changes'}
          </button>
        </form>

      </div>
    </div>
  );
};

const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  switch (status) {
    case 'confirmed':
      return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">CONFIRMED</span>;
    case 'pending':
      return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse">PENDING HOLD</span>;
    case 'cancelled':
      return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">CANCELLED</span>;
    case 'refunded':
      return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-blue-500/20 text-blue-400 border border-blue-500/30">REFUNDED</span>;
    default:
      return <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-gray-800 text-gray-400">{status}</span>;
  }
};
