import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { MapPin, Plus, AlertCircle, ArrowLeft, Building2 } from 'lucide-react';
import type { Venue } from './EventPages';

export const VenueListPage: React.FC = () => {
  const [venues, setVenues] = useState<Venue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [capacity, setCapacity] = useState(500);
  const [createLoading, setCreateLoading] = useState(false);

  const fetchVenues = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get<Venue[]>('/venues');
      setVenues(res.data);
    } catch (err: any) {
      setError('Failed to fetch venues catalog.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVenues();
  }, []);

  const handleCreateVenue = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    try {
      await apiClient.post('/venues', { name, location, capacity });
      setShowCreateModal(false);
      setName('');
      setLocation('');
      setCapacity(500);
      fetchVenues();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create venue.');
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-10">
        <div>
          <h1 className="text-3xl font-extrabold font-heading text-white">Event Venues</h1>
          <p className="text-gray-400 text-sm mt-1">Explore concert halls, stadiums, and conference centers</p>
        </div>

        {user && user.role === 'admin' && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2.5 btn-gradient font-bold text-white text-sm rounded-xl shadow-lg"
          >
            <Plus className="w-4 h-4" />
            <span>Add New Venue</span>
          </button>
        )}
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <div key={n} className="glass-panel p-6 rounded-2xl h-40 animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="glass-panel p-8 text-center rounded-2xl text-rose-400">
          <AlertCircle className="w-8 h-8 mx-auto mb-2" />
          <p>{error}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {venues.map((v) => (
            <Link
              key={v.id}
              to={`/venues/${v.id}`}
              className="glass-panel glass-panel-hover p-6 rounded-2xl border border-gray-800 flex flex-col justify-between"
            >
              <div>
                <div className="w-12 h-12 rounded-xl bg-purple-600/20 text-purple-400 flex items-center justify-center mb-4">
                  <Building2 className="w-6 h-6" />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{v.name}</h3>
                <div className="flex items-center space-x-2 text-xs text-gray-400 mb-2">
                  <MapPin className="w-4 h-4 text-purple-400 shrink-0" />
                  <span className="truncate">{v.location}</span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-800/80 flex justify-between items-center text-xs">
                <span className="text-gray-400">Seating Capacity</span>
                <span className="font-extrabold text-purple-400 bg-purple-500/10 px-2.5 py-1 rounded-lg border border-purple-500/20">
                  {v.capacity} Seats
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Admin Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="glass-panel p-8 rounded-3xl max-w-md w-full border border-gray-800">
            <h2 className="text-2xl font-bold text-white mb-6">Create New Venue</h2>
            <form onSubmit={handleCreateVenue} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase mb-2">Venue Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Grand Symphony Hall"
                  className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase mb-2">Location / Address</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="123 Music Ave, NY"
                  className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-300 uppercase mb-2">Seating Capacity</label>
                <input
                  type="number"
                  value={capacity}
                  onChange={(e) => setCapacity(Number(e.target.value))}
                  className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white"
                  required
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="w-1/2 py-2.5 bg-gray-800 text-gray-300 rounded-xl text-sm font-semibold hover:bg-gray-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createLoading}
                  className="w-1/2 py-2.5 btn-gradient text-white rounded-xl text-sm font-bold shadow-lg"
                >
                  {createLoading ? 'Creating...' : 'Create Venue'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export const VenueDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [venue, setVenue] = useState<Venue | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVenue = async () => {
      try {
        const res = await apiClient.get<Venue>(`/venues/${id}`);
        setVenue(res.data);
      } catch (err: any) {
        // handle error
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchVenue();
  }, [id]);

  if (loading) return <div className="p-12 text-center text-gray-400">Loading venue details...</div>;
  if (!venue) return <div className="p-12 text-center text-rose-400">Venue not found.</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <Link to="/venues" className="inline-flex items-center space-x-2 text-sm text-gray-400 hover:text-white mb-6">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Venues</span>
      </Link>

      <div className="glass-panel p-8 rounded-3xl border border-gray-800">
        <div className="w-16 h-16 rounded-2xl bg-purple-600/20 text-purple-400 flex items-center justify-center mb-6">
          <Building2 className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold text-white mb-2">{venue.name}</h1>
        <p className="text-gray-400 text-sm flex items-center space-x-2 mb-6">
          <MapPin className="w-4 h-4 text-purple-400" />
          <span>{venue.location}</span>
        </p>

        <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 inline-block">
          <span className="text-xs text-gray-400 block uppercase tracking-wider mb-1">Max Seating Capacity</span>
          <span className="text-2xl font-bold text-white">{venue.capacity} Seats</span>
        </div>
      </div>
    </div>
  );
};
