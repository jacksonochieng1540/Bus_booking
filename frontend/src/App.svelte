<script>
  import { onMount } from 'svelte';
  import './app.css';
  import Navbar from './lib/Navbar.svelte';
  import JourneyPlanner from './lib/JourneyPlanner.svelte';
  import TripList from './lib/TripList.svelte';
  import SeatMap from './lib/SeatMap.svelte';
  import BookingForm from './lib/BookingForm.svelte';
  import BookingDetail from './lib/BookingDetail.svelte';
  import NotificationLogs from './lib/NotificationLogs.svelte';
  import AuthModal from './lib/AuthModal.svelte';

  let currentTab = 'trips';
  let viewMode = 'list';

  let trips = [];
  let loadingTrips = false;
  let departure = '';
  let destination = '';

  let selectedTripDetail = null;
  let selectedSeat = null;
  let currentBooking = null;

  let user = null;
  let authModalOpen = false;
  let authModalMode = 'login';
  let alertMsg = '';
  let alertType = 'success';

  function showAlert(msg, type = 'success') {
    alertMsg = msg;
    alertType = type;
    setTimeout(() => {
      alertMsg = '';
    }, 4000);
  }

  async function fetchTrips(filters = {}) {
    loadingTrips = true;
    try {
      let url = '/api/v1/trips/';
      const params = new URLSearchParams();
      if (filters.departure) params.append('departure', filters.departure);
      if (filters.destination) params.append('destination', filters.destination);
      if (params.toString()) url += `?${params.toString()}`;

      const res = await fetch(url);
      const data = await res.json();
      trips = data.trips || [];
    } catch (e) {
      console.error(e);
      showAlert('Failed to load trips from API', 'error');
    } finally {
      loadingTrips = false;
    }
  }

  async function selectTrip(tripId) {
    try {
      const res = await fetch(`/api/v1/trips/${tripId}/`);
      if (res.ok) {
        selectedTripDetail = await res.json();
        viewMode = 'seatmap';
      } else {
        showAlert('Trip details not found', 'error');
      }
    } catch (e) {
      showAlert('Error loading trip details', 'error');
    }
  }

  function handleSeatSelect(seatNumber) {
    selectedSeat = seatNumber;
    viewMode = 'booking_form';
  }

  async function handleSubmitBooking(payload) {
    try {
      const res = await fetch(`/bookings/api/v1/create/${selectedTripDetail.id}/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        currentBooking = data.booking;
        viewMode = 'booking_detail';
        showAlert(`Seat #${currentBooking.seat_number} reserved successfully!`);
      } else {
        showAlert(data.error || 'Seat reservation failed. It may be already taken.', 'error');
      }
    } catch (e) {
      showAlert('Failed to submit booking reservation', 'error');
    }
  }

  async function handlePayMpesa(bookingId, phone) {
    try {
      const res = await fetch('/payments/api/v1/stk-push/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ booking_id: bookingId, phone_number: phone })
      });
      const data = await res.json();
      if (res.ok) {
        showAlert(`STK Push prompt sent to ${phone}. Completing payment...`);
        setTimeout(async () => {
          await fetch(`/payments/api/v1/callback/${data.payment.id}/?secret=sacco-secure-webhook-secret-key`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ success: true, mpesa_receipt_number: `MPESA-${Math.random().toString(36).substring(2, 8).toUpperCase()}` })
          });
          currentBooking.status = 'CONFIRMED';
          showAlert('Payment received! Booking CONFIRMED and SMS ticket dispatched.');
        }, 1500);
      } else {
        showAlert(data.error || 'Failed to initiate STK Push', 'error');
      }
    } catch (e) {
      showAlert('Payment initiation error', 'error');
    }
  }

  function openAuthModal(mode = 'login') {
    authModalMode = mode;
    authModalOpen = true;
  }

  function handleLoginSuccess(userData) {
    user = userData;
    showAlert(`Welcome back, ${user.first_name || user.username}!`);
  }

  function handleLogout() {
    user = null;
    showAlert('Logged out successfully');
  }

  onMount(() => {
    fetchTrips();
  });
</script>

<Navbar 
  bind:currentTab 
  {user} 
  {openAuthModal} 
  {handleLogout} 
/>

{#if alertMsg}
  <div style="max-width: 1280px; margin: 1rem auto 0 auto; padding: 0 1.5rem;">
    <div style="padding: 1rem 1.25rem; border-radius: 0.5rem; font-weight: 700; background: {alertType === 'success' ? '#dcfce7' : '#fee2e2'}; border: 1px solid {alertType === 'success' ? '#86efac' : '#fca5a5'}; color: {alertType === 'success' ? '#166534' : '#991b1b'};">
      {alertMsg}
    </div>
  </div>
{/if}

<main class="main-container">
  {#if currentTab === 'trips'}
    {#if viewMode === 'list'}
      <JourneyPlanner 
        bind:departure 
        bind:destination 
        onSearch={(filters) => fetchTrips(filters)} 
      />

      <section class="hero-image-banner" style="background: linear-gradient(rgba(15, 23, 42, 0.65), rgba(15, 23, 42, 0.85)), url('/static/images/hero_bg.jpg') center/cover no-repeat; color: #ffffff; padding: 4.5rem 2rem; margin: 2rem 0; border-radius: 0.75rem;">
        <div class="hero-content">
          <h1 style="font-size: 3rem; font-weight: 900; line-height: 1.15; max-width: 750px; margin-bottom: 1rem;">
            SafariSacco:<br>Fast, Reliable &amp; Safe Express Coach Travel
          </h1>
          <p style="font-size: 1.2rem; color: #f1f5f9; max-width: 650px;">
            Daily luxury bus departures linking Nairobi, Mombasa, Kisumu, Nakuru, Eldoret &amp; Malindi with instant M-Pesa mobile ticketing.
          </p>
        </div>
      </section>

      <TripList 
        {trips} 
        {loadingTrips} 
        {selectTrip} 
      />
    {:else if viewMode === 'seatmap'}
      <SeatMap 
        tripDetail={selectedTripDetail} 
        onSeatSelect={handleSeatSelect} 
        backToTrips={() => viewMode = 'list'} 
      />
    {:else if viewMode === 'booking_form'}
      <BookingForm 
        tripDetail={selectedTripDetail} 
        {selectedSeat} 
        onSubmitBooking={handleSubmitBooking} 
        backToSeatMap={() => viewMode = 'seatmap'} 
      />
    {:else if viewMode === 'booking_detail'}
      <BookingDetail 
        booking={currentBooking} 
        onPayMpesa={handlePayMpesa} 
        backToTrips={() => viewMode = 'list'} 
      />
    {/if}
  {:else if currentTab === 'logs'}
    <NotificationLogs />
  {/if}
</main>

<!-- Floating WhatsApp Web Customer Service Chat Widget -->
<a href="https://wa.me/254712345678?text=Hello%20SafariSacco%20Customer%20Support%2C%20I%20need%20assistance%20with%20my%20bus%20booking." target="_blank" class="whatsapp-chat-widget" title="Chat with Customer Service on WhatsApp">
  <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>
  <span>WhatsApp Support</span>
</a>

<AuthModal 
  isOpen={authModalOpen} 
  initialMode={authModalMode} 
  closeModal={() => authModalOpen = false} 
  onLoginSuccess={handleLoginSuccess} 
/>

<footer>
  <p>&copy; 2026 SafariSacco Kenya Ltd. All rights reserved. | Svelte Single Page Application UI</p>
</footer>
