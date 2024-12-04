// #Dylaan - 11/30
// Updates and improvements by Addison M - 12/04

document.addEventListener("DOMContentLoaded", function () {
    // Get the booking ID from the URL parameters
    const bookingId = new URLSearchParams(window.location.search).get("booking_id");

    // Display an error message if booking ID is missing
    if (!bookingId) {
        document.getElementById("booking-details").innerHTML = "<p><strong>Error:</strong> Booking ID is missing.</p>";
        return;
    }

    // Fetch booking details from the backend
    fetch("/api/bookings/confirm", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ booking_id: bookingId })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                document.getElementById("booking-details").innerHTML = `<p><strong>Error:</strong> ${data.error}</p>`;
            } else {
                // Display booking details on the page
                document.getElementById("booking-details").innerHTML = `
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
        .catch(error => {
            document.getElementById("booking-details").innerHTML = `<p><strong>Error:</strong> Could not fetch booking details. Please try again later.</p>`;
            console.error("Error fetching booking details:", error);
        });
});
