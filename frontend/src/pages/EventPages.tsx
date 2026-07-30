import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Calendar, MapPin, Search, Tag, Ticket, Clock, CheckCircle, AlertCircle, ArrowLeft, ShieldCheck } from 'lucide-react';

export interface Venue {
  id: string;
  name: string;
  location: string;
  capacity: number;
}

export interface Organizer {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface EventItem {
  id: string;
  title: string;
  description: string;
  category: string;
  event_poster_url?: string;
  venue_id: string;
  start_time: string;
  end_time: string;
  total_tickets: number;
  ticket_price: string | number;
  status: string;
  venue?: Venue;
  organizer?: Organizer;
}

export const EventListPage: React.FC = () => {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchEvents = async () => {
    setLoading(true);
    setError('');
    try {
      const params: any = { status: 'published' };
      if (search) params.search_query = search;
      if (category) params.category = category;

      const response = await apiClient.get<EventItem[]>('/events', { params });
      setEvents(response.data);
    } catch (err: any) {
      setError('Failed to load events. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [category]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchEvents();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Hero Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <h1 className="text-4xl sm:text-5xl font-extrabold font-heading text-white tracking-tight">
          Discover Extraordinary <span className="text-gradient">Live Events</span>
        </h1>
        <p className="mt-4 text-lg text-gray-400">
          Reserve tickets instantly with 10-minute hold window protection.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="glass-panel p-4 rounded-2xl mb-10 shadow-xl flex flex-col md:flex-row gap-4 justify-between items-center">
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-96">
          <Search className="w-5 h-5 absolute left-3.5 top-3 text-gray-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search events by title or description..."
            className="w-full bg-gray-900/90 border border-gray-800 rounded-xl pl-11 pr-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-all"
          />
        </form>

        {/* Category Pills */}
        <div className="flex flex-wrap gap-2 w-full md:w-auto justify-start md:justify-end">
          {['', 'concert', 'conference', 'sports', 'theater', 'meetup'].map((cat) => (
            <button
              key={cat}
              onClick={() => setCategory(cat)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all ${
                category === cat
                  ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/30'
                  : 'bg-gray-800/60 text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              {cat === '' ? 'All Categories' : cat}
            </button>
          ))}
        </div>
      </div>

      {/* Content View */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div key={n} className="glass-panel rounded-2xl p-6 h-80 animate-pulse flex flex-col justify-between">
              <div className="w-full h-40 bg-gray-800/60 rounded-xl mb-4" />
              <div className="h-6 bg-gray-800/80 rounded w-3/4 mb-2" />
              <div className="h-4 bg-gray-800/60 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="glass-panel p-12 text-center rounded-2xl max-w-lg mx-auto">
          <AlertCircle className="w-12 h-12 text-rose-400 mx-auto mb-4" />
          <p className="text-rose-300 font-semibold">{error}</p>
          <button onClick={fetchEvents} className="mt-4 px-6 py-2 btn-gradient text-white rounded-xl text-sm font-semibold">
            Retry
          </button>
        </div>
      ) : events.length === 0 ? (
        <div className="glass-panel p-16 text-center rounded-2xl max-w-md mx-auto">
          <Calendar className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-white mb-2">No Events Found</h3>
          <p className="text-gray-400 text-sm">Try clearing filters or searching for something else.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {events.map((evt) => (
            <Link
              key={evt.id}
              to={`/events/${evt.id}`}
              className="glass-panel glass-panel-hover rounded-2xl overflow-hidden flex flex-col group border border-gray-800/80"
            >
              {/* Event Image */}
              <div className="relative h-48 bg-gray-900 overflow-hidden">
                {evt.event_poster_url ? (
                  <img
                    src={evt.event_poster_url}
                    alt={evt.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-900/40 to-indigo-900/40">
                    <Ticket className="w-16 h-16 text-purple-400/40" />
                  </div>
                )}
                
                {/* Category Badge */}
                <div className="absolute top-3 left-3 bg-gray-950/80 backdrop-blur-md px-3 py-1 rounded-lg border border-gray-800 text-xs font-semibold text-purple-400 uppercase tracking-wider flex items-center space-x-1">
                  <Tag className="w-3 h-3" />
                  <span>{evt.category}</span>
                </div>

                {/* Price Tag */}
                <div className="absolute bottom-3 right-3 bg-purple-600 text-white font-extrabold px-3 py-1 rounded-xl text-sm shadow-lg shadow-purple-600/40">
                  ${Number(evt.ticket_price).toFixed(2)}
                </div>
              </div>

              {/* Event Body */}
              <div className="p-6 flex-1 flex flex-col justify-between">
                <div>
                  <h3 className="text-xl font-bold text-white group-hover:text-purple-300 transition-colors line-clamp-1">
                    {evt.title}
                  </h3>
                  <p className="text-gray-400 text-sm mt-2 line-clamp-2 leading-relaxed">
                    {evt.description}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-gray-800/60 space-y-2 text-xs text-gray-400">
                  <div className="flex items-center space-x-2">
                    <Calendar className="w-4 h-4 text-purple-400" />
                    <span>{new Date(evt.start_time).toLocaleString()}</span>
                  </div>
                  {evt.venue && (
                    <div className="flex items-center space-x-2">
                      <MapPin className="w-4 h-4 text-purple-400" />
                      <span className="truncate">{evt.venue.name} • {evt.venue.location}</span>
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export const EventDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [event, setEvent] = useState<EventItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [numTickets, setNumTickets] = useState(1);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [bookingError, setBookingError] = useState('');
  const [bookingSuccess, setBookingSuccess] = useState<any>(null);

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const res = await apiClient.get<EventItem>(`/events/${id}`);
        setEvent(res.data);
      } catch (err: any) {
        setBookingError('Event not found.');
      } finally {
        setLoading(false);
      }
    };
    if (id) fetchDetail();
  }, [id]);

  const handleBookTickets = async () => {
    if (!user) {
      navigate('/auth/login');
      return;
    }

    setBookingLoading(true);
    setBookingError('');

    try {
      const response = await apiClient.post('/bookings', {
        event_id: id,
        num_tickets: numTickets,
      });
      setBookingSuccess(response.data);
    } catch (err: any) {
      setBookingError(err.response?.data?.detail || 'Booking failed. Not enough tickets available.');
    } finally {
      setBookingLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-400">Loading event details...</p>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <AlertCircle className="w-12 h-12 text-rose-400 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-white mb-2">Event Not Found</h3>
        <Link to="/events" className="text-purple-400 font-medium hover:underline">Back to Events</Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      <Link to="/events" className="inline-flex items-center space-x-2 text-sm text-gray-400 hover:text-white mb-8 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Events Catalog</span>
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-10">
        
        {/* Main Event Information */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Banner Poster */}
          <div className="relative h-80 sm:h-96 rounded-3xl overflow-hidden glass-panel border border-gray-800">
            {event.event_poster_url ? (
              <img src={event.event_poster_url} alt={event.title} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-purple-950 to-indigo-950">
                <Ticket className="w-24 h-24 text-purple-400/30" />
              </div>
            )}
            <div className="absolute top-4 left-4 bg-gray-950/80 backdrop-blur-md px-4 py-1.5 rounded-xl border border-gray-800 text-xs font-bold text-purple-400 uppercase tracking-widest">
              {event.category}
            </div>
          </div>

          <div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white font-heading">{event.title}</h1>
            <p className="text-gray-300 mt-4 leading-relaxed whitespace-pre-line">{event.description}</p>
          </div>

          {/* Venue & Organizer Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {event.venue && (
              <div className="glass-panel p-5 rounded-2xl border border-gray-800/80">
                <div className="flex items-center space-x-3 mb-2">
                  <MapPin className="w-5 h-5 text-purple-400" />
                  <h4 className="font-bold text-white">{event.venue.name}</h4>
                </div>
                <p className="text-xs text-gray-400">{event.venue.location}</p>
                <p className="text-xs text-purple-400 font-semibold mt-2">Venue Capacity: {event.venue.capacity} seats</p>
              </div>
            )}

            {event.organizer && (
              <div className="glass-panel p-5 rounded-2xl border border-gray-800/80">
                <div className="flex items-center space-x-3 mb-2">
                  <ShieldCheck className="w-5 h-5 text-purple-400" />
                  <h4 className="font-bold text-white">Organizer Profile</h4>
                </div>
                <p className="text-xs text-gray-300">{event.organizer.first_name} {event.organizer.last_name}</p>
                <p className="text-xs text-gray-400 mt-1">{event.organizer.email}</p>
              </div>
            )}
          </div>
        </div>

        {/* Booking Sidebar Widget */}
        <div className="lg:col-span-1">
          <div className="glass-panel p-6 rounded-3xl border border-gray-800 sticky top-24 shadow-2xl">
            
            <div className="flex justify-between items-baseline mb-6 pb-6 border-b border-gray-800">
              <span className="text-gray-400 text-sm">Ticket Price</span>
              <div className="text-3xl font-extrabold text-white">
                ${Number(event.ticket_price).toFixed(2)}
                <span className="text-xs text-gray-400 font-normal"> / ticket</span>
              </div>
            </div>

            {bookingSuccess ? (
              <div className="space-y-4 text-center">
                <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto" />
                <h3 className="text-xl font-bold text-white">Reservation Hold Active!</h3>
                <p className="text-xs text-emerald-300 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">
                  Your {bookingSuccess.num_tickets} ticket(s) are reserved in PENDING status under a 10-minute hold.
                </p>
                <Link
                  to={`/me/bookings`}
                  className="block w-full py-3 btn-gradient font-bold text-white rounded-xl text-center text-sm shadow-lg"
                >
                  View My Ticket Holds
                </Link>
              </div>
            ) : (
              <div className="space-y-6">
                
                {bookingError && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{bookingError}</span>
                  </div>
                )}

                <div>
                  <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-3">
                    Number of Tickets
                  </label>
                  <div className="flex items-center justify-between bg-gray-900/90 border border-gray-800 rounded-xl p-2">
                    <button
                      onClick={() => setNumTickets(Math.max(1, numTickets - 1))}
                      className="w-10 h-10 rounded-lg bg-gray-800 text-white font-bold hover:bg-gray-700 transition-colors"
                    >
                      -
                    </button>
                    <span className="text-lg font-bold text-white">{numTickets}</span>
                    <button
                      onClick={() => setNumTickets(numTickets + 1)}
                      className="w-10 h-10 rounded-lg bg-gray-800 text-white font-bold hover:bg-gray-700 transition-colors"
                    >
                      +
                    </button>
                  </div>
                </div>

                <div className="pt-2">
                  <div className="flex justify-between text-sm text-gray-400 mb-2">
                    <span>Total Amount:</span>
                    <span className="text-lg font-extrabold text-purple-400">
                      ${(Number(event.ticket_price) * numTickets).toFixed(2)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-xs text-amber-400 bg-amber-500/10 p-2.5 rounded-xl border border-amber-500/20 mb-4">
                    <Clock className="w-4 h-4 shrink-0" />
                    <span>Includes 10-minute hold window guarantee.</span>
                  </div>
                </div>

                <button
                  onClick={handleBookTickets}
                  disabled={bookingLoading}
                  className="w-full py-3.5 btn-gradient font-bold text-white rounded-xl shadow-lg flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <Ticket className="w-5 h-5" />
                  <span>{bookingLoading ? 'Reserving Seats...' : 'Reserve Tickets Now'}</span>
                </button>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
};
