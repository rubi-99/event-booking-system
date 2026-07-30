import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';
import type { Venue } from './EventPages';
import { PlusCircle, Upload, AlertCircle } from 'lucide-react';

export const CreateEventPage: React.FC = () => {
  const navigate = useNavigate();
  const [venues, setVenues] = useState<Venue[]>([]);
  const [loadingVenues, setLoadingVenues] = useState(true);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('concert');
  const [venueId, setVenueId] = useState('');
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [totalTickets, setTotalTickets] = useState(100);
  const [ticketPrice, setTicketPrice] = useState(25.0);
  
  const [posterFile, setPosterFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchVenues = async () => {
      try {
        const res = await apiClient.get<Venue[]>('/venues');
        setVenues(res.data);
        if (res.data.length > 0) setVenueId(res.data[0].id);
      } catch (err) {
        setError('Failed to fetch venue list. Please create a venue first.');
      } finally {
        setLoadingVenues(false);
      }
    };
    fetchVenues();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!venueId) {
      setError('Please select a valid venue.');
      return;
    }

    setLoading(true);
    try {
      // 1. Create Event
      const eventPayload = {
        title,
        description,
        category,
        venue_id: venueId,
        start_time: new Date(startTime).toISOString(),
        end_time: new Date(endTime).toISOString(),
        total_tickets: Number(totalTickets),
        ticket_price: Number(ticketPrice),
        status: 'published',
      };

      const eventRes = await apiClient.post('/events', eventPayload);
      const createdEventId = eventRes.data.id;

      // 2. Upload Poster Image if selected
      if (posterFile) {
        const formData = new FormData();
        formData.append('file', posterFile);

        await apiClient.post(`/events/${createdEventId}/poster`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      navigate(`/events/${createdEventId}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create event. Please verify inputs.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="glass-panel p-8 rounded-3xl border border-gray-800 shadow-2xl">
        
        <div className="flex items-center space-x-3 mb-8">
          <div className="p-3 rounded-2xl bg-purple-600/20 text-purple-400">
            <PlusCircle className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white font-heading">Host a New Event</h1>
            <p className="text-gray-400 text-xs mt-0.5">Publish event details, schedule times, and upload posters</p>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          
          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Event Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Summer Jazz & Music Festival 2026"
              className="w-full bg-gray-900/90 border border-gray-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-purple-500 text-sm"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Description</label>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe what attendees can expect..."
              className="w-full bg-gray-900/90 border border-gray-800 rounded-xl p-4 text-white focus:outline-none focus:border-purple-500 text-sm"
              required
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Category</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white text-sm"
              >
                <option value="concert">Concert</option>
                <option value="conference">Conference</option>
                <option value="sports">Sports</option>
                <option value="theater">Theater</option>
                <option value="meetup">Meetup</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Venue Selection</label>
              <select
                value={venueId}
                onChange={(e) => setVenueId(e.target.value)}
                disabled={loadingVenues}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white text-sm"
                required
              >
                {venues.map((v) => (
                  <option key={v.id} value={v.id}>
                    {v.name} ({v.capacity} Seats)
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Start Time</label>
              <input
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">End Time</label>
              <input
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white text-sm"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Total Ticket Inventory</label>
              <input
                type="number"
                value={totalTickets}
                onChange={(e) => setTotalTickets(Number(e.target.value))}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white text-sm"
                required
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Ticket Price ($)</label>
              <input
                type="number"
                step="0.01"
                value={ticketPrice}
                onChange={(e) => setTicketPrice(Number(e.target.value))}
                className="w-full bg-gray-900 border border-gray-800 rounded-xl p-2.5 text-white text-sm"
                required
              />
            </div>
          </div>

          {/* Image File Uploader */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Event Poster Image (JPEG, PNG, WebP ≤ 5MB)</label>
            <div className="relative border-2 border-dashed border-gray-800 hover:border-purple-500/50 rounded-2xl p-6 text-center transition-all bg-gray-900/50">
              <Upload className="w-8 h-8 text-purple-400 mx-auto mb-2" />
              <p className="text-xs text-gray-400">
                {posterFile ? posterFile.name : 'Click to browse or drag and drop image file'}
              </p>
              <input
                type="file"
                accept="image/png, image/jpeg, image/webp"
                onChange={(e) => e.target.files && setPosterFile(e.target.files[0])}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 btn-gradient font-bold text-white rounded-xl shadow-xl disabled:opacity-50 mt-4"
          >
            {loading ? 'Publishing Event...' : 'Publish Event & Release Tickets'}
          </button>
        </form>

      </div>
    </div>
  );
};
