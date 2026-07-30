import React, { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { ShieldAlert, Users, Ticket, DollarSign, RefreshCcw } from 'lucide-react';

interface AdminMetrics {
  total_users: number;
  total_tickets_sold: number;
  total_revenue: number;
}

interface UserItem {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'user' | 'organizer' | 'admin';
}

interface BookingAdminItem {
  id: string;
  user_id: string;
  event_id: string;
  num_tickets: number;
  total_price: string | number;
  status: string;
  created_at: string;
  user?: { email: string; first_name: string; last_name: string };
  event?: { title: string };
}

export const AdminDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [users, setUsers] = useState<UserItem[]>([]);
  const [bookings, setBookings] = useState<BookingAdminItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'users' | 'bookings'>('users');

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [dashRes, usersRes, bookingsRes] = await Promise.all([
        apiClient.get<AdminMetrics>('/admin/dashboard'),
        apiClient.get<UserItem[]>('/admin/users'),
        apiClient.get<BookingAdminItem[]>('/admin/bookings'),
      ]);
      setMetrics(dashRes.data);
      setUsers(usersRes.data);
      setBookings(bookingsRes.data);
    } catch (err: any) {
      // error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const handlePromoteRole = async (userId: string, newRole: string) => {
    try {
      await apiClient.put(`/admin/users/${userId}/role`, { new_role: newRole });
      fetchAdminData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update user role.');
    }
  };

  const handleRefundBooking = async (bookingId: string) => {
    if (!confirm('Are you sure you want to refund this booking?')) return;
    try {
      await apiClient.post(`/admin/bookings/${bookingId}/refund`);
      fetchAdminData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to refund booking.');
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Loading admin metrics & system data...</p>
      </div>
    );
  }

  if (!user || user.role !== 'admin') {
    return (
      <div className="max-w-md mx-auto py-16 text-center">
        <ShieldAlert className="w-16 h-16 text-rose-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Access Forbidden</h2>
        <p className="text-gray-400 text-sm">You must be a system Administrator to view the console.</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-extrabold font-heading text-white flex items-center space-x-3">
            <span>Admin Moderation Console</span>
            <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-3 py-1 rounded-lg">
              SYSTEM ROOT
            </span>
          </h1>
          <p className="text-gray-400 text-sm mt-1">Platform overview, user promotion, and booking refund operations</p>
        </div>

        <button
          onClick={fetchAdminData}
          className="p-2.5 rounded-xl bg-gray-800 text-gray-300 hover:text-white transition-colors"
        >
          <RefreshCcw className="w-5 h-5" />
        </button>
      </div>

      {/* Aggregate Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        
        <div className="glass-panel p-6 rounded-2xl border border-gray-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Registered Users</p>
            <h3 className="text-3xl font-extrabold text-white mt-1">{metrics?.total_users || 0}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-gray-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Tickets Sold</p>
            <h3 className="text-3xl font-extrabold text-white mt-1">{metrics?.total_tickets_sold || 0}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
            <Ticket className="w-6 h-6" />
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl border border-gray-800 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Total Revenue</p>
            <h3 className="text-3xl font-extrabold text-emerald-400 mt-1">${Number(metrics?.total_revenue || 0).toFixed(2)}</h3>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-600/20 text-emerald-400 flex items-center justify-center">
            <DollarSign className="w-6 h-6" />
          </div>
        </div>

      </div>

      {/* Navigation Tabs */}
      <div className="flex space-x-3 mb-6">
        <button
          onClick={() => setActiveTab('users')}
          className={`px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
            activeTab === 'users' ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30' : 'bg-gray-800/60 text-gray-400 hover:text-white'
          }`}
        >
          User Accounts & Roles ({users.length})
        </button>

        <button
          onClick={() => setActiveTab('bookings')}
          className={`px-5 py-2.5 rounded-xl font-bold text-sm transition-all ${
            activeTab === 'bookings' ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30' : 'bg-gray-800/60 text-gray-400 hover:text-white'
          }`}
        >
          Global Bookings ({bookings.length})
        </button>
      </div>

      {/* Tab 1: User Management Table */}
      {activeTab === 'users' && (
        <div className="glass-panel rounded-2xl border border-gray-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-gray-900/90 text-xs uppercase tracking-wider text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">Email</th>
                  <th className="px-6 py-4">Current Role</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-gray-900/50 transition-colors">
                    <td className="px-6 py-4 font-bold text-white">
                      {u.first_name} {u.last_name}
                    </td>
                    <td className="px-6 py-4 text-gray-400">{u.email}</td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-bold uppercase ${
                        u.role === 'admin'
                          ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          : u.role === 'organizer'
                          ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30'
                          : 'bg-gray-800 text-gray-300'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <select
                        value={u.role}
                        onChange={(e) => handlePromoteRole(u.id, e.target.value)}
                        className="bg-gray-900 border border-gray-800 rounded-lg text-xs text-white px-3 py-1.5 focus:outline-none focus:border-purple-500"
                      >
                        <option value="user">User</option>
                        <option value="organizer">Organizer</option>
                        <option value="admin">Admin</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Tab 2: Global Bookings Table */}
      {activeTab === 'bookings' && (
        <div className="glass-panel rounded-2xl border border-gray-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-gray-900/90 text-xs uppercase tracking-wider text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="px-6 py-4">Booking ID</th>
                  <th className="px-6 py-4">Customer</th>
                  <th className="px-6 py-4">Event</th>
                  <th className="px-6 py-4">Tickets</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {bookings.map((b) => (
                  <tr key={b.id} className="hover:bg-gray-900/50 transition-colors">
                    <td className="px-6 py-4 font-mono text-xs text-gray-400">{b.id.slice(0, 8)}...</td>
                    <td className="px-6 py-4 font-semibold text-white">{b.user?.email || b.user_id.slice(0, 8)}</td>
                    <td className="px-6 py-4 text-gray-300">{b.event?.title || b.event_id.slice(0, 8)}</td>
                    <td className="px-6 py-4 font-bold text-white">{b.num_tickets}</td>
                    <td className="px-6 py-4 font-extrabold text-purple-400">${Number(b.total_price).toFixed(2)}</td>
                    <td className="px-6 py-4 uppercase font-bold text-xs">{b.status}</td>
                    <td className="px-6 py-4 text-right">
                      {b.status !== 'refunded' && b.status !== 'cancelled' && (
                        <button
                          onClick={() => handleRefundBooking(b.id)}
                          className="px-3 py-1.5 text-xs font-bold text-rose-400 bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 rounded-lg transition-colors"
                        >
                          Force Refund
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

    </div>
  );
};
