// #Dylaan - 11/30: 
document.addEventListener("DOMContentLoaded", function () {
    // Get the booking ID from the URL parameters
    const bookingId = new URLSearchParams(window.location.search).get("booking_id");

    if (!bookingId) {
        document.getElementById("booking-details").innerHTML = "<p>Booking ID is missing.</p>";
        return;
    }

    // Fetch booking details from the backend
    fetch("/api/booking/confirm", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ booking_id: bookingId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById("booking-details").innerHTML = `<p>${data.error}</p>`;
        } else {
            // Display booking details on the page
            document.getElementById("booking-details").innerHTML = `
                <p><strong>Booking ID:</strong> ${data.booking_id}</p>
                <p><strong>Passenger Name:</strong> ${data.passenger_name}</p>
                <p><strong>Flight Number:</strong> ${data.flight_number}</p>
                <p><strong>Seat:</strong> ${data.seat}</p>
                <p><strong>Total Price:</strong> $${data.total_price.toFixed(2)}</p>
                <p><strong>Booking Date:</strong> ${new Date(data.booking_date).toLocaleString()}</p>
            `;
        }
    })
    .catch(error => {
        document.getElementById("booking-details").innerHTML = `<p>Error fetching booking details: ${error.message}</p>`;
        console.error("Error fetching booking details:", error);
    });
});
