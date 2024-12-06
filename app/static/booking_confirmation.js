// #Dylaan - 11/30
// Updates and improvements by Addison M - 12/04

document.addEventListener("DOMContentLoaded", function () {
    const bookingDetails = document.getElementById("booking-details");

    // Get the booking ID from the URL parameters
    const bookingId = new URLSearchParams(window.location.search).get("booking_id");

    if (!bookingId) {
        bookingDetails.innerHTML = "<p><strong>Error:</strong> Booking ID is missing.</p>";
        return;
    }

    // Show loading indicator
    bookingDetails.innerHTML = "<p>Loading booking details...</p>";

    // Fetch booking details
    fetch("/api/bookings/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ booking_id: bookingId }),
    })
        .then((response) => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then((data) => {
            if (data.error) {
                bookingDetails.innerHTML = `<p><strong>Error:</strong> ${data.error}</p>`;
            } else {
                bookingDetails.innerHTML = `
                    <h2>Booking Confirmation</h2>
                    <p><strong>Booking ID:</strong> ${data.booking_id}</p>
                    <p><strong>Passenger Name:</strong> ${data.passenger_name}</p>
                    <p><strong>Flight Number:</strong> ${data.flight_number}</p>
                    <p><strong>Seat:</strong> ${data.seat || "Not Assigned"}</p>
                    <p><strong>Total Price:</strong> $${data.total_price.toFixed(2)}</p>
                    <p><strong>Booking Date:</strong> ${new Date(data.booking_date).toLocaleString()}</p>
                `;
            }
        })
        .catch((error) => {
            bookingDetails.innerHTML = "<p><strong>Error:</strong> Could not fetch booking details. Please try again later.</p>";
            console.error("Error fetching booking details:", error);
        });
});
