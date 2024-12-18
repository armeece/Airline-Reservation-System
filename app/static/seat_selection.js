document.addEventListener("DOMContentLoaded", function () {
    const planeContainer = document.getElementById("planeContainer");
    const confirmButton = document.getElementById("confirmButton");
    let selectedSeat = null;

    // Fetch seat list for the flight
    fetch(`/api/flights/${flightId}/seats`)
        .then(response => {
            console.log("Fetching seat list. Response Status:", response.status);
            return response.text().then(text => {
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.error("Invalid JSON response:", text);
                    throw new Error("Server returned invalid JSON");
                }
            });
        })
        .then(data => {
            console.log("Seat Data Received:", data);

            if (data.error) {
                console.error("Error in seat data:", data.error);
                alert(data.error);
                return;
            }

            // Render seat data dynamically
            planeContainer.innerHTML = ""; // Clear previous content
            data.seats.forEach(seat => {
                if (!seat.seat_number || !seat.seat_class) {
                    console.warn("Invalid seat data encountered:", seat);
                    return;
                }

                // Create seat div dynamically
                const seatDiv = document.createElement("div");
                seatDiv.textContent = `${seat.seat_number} (${seat.seat_class})`;

                // Handle seat availability
                if (!seat.is_available) {
                    seatDiv.className = "seat unavailable";
                    seatDiv.style.pointerEvents = "none"; // Non-clickable for unavailable seats
                } else {
                    seatDiv.className = "seat";
                    seatDiv.addEventListener("click", () => {
                        // Deselect previously selected seat
                        document.querySelectorAll(".seat.selected").forEach(el => el.classList.remove("selected"));
                        seatDiv.classList.add("selected");
                        selectedSeat = seat.seat_number;

                        // Enable confirm button after seat selection
                        confirmButton.disabled = false;
                        console.log("Selected Seat:", selectedSeat);
                    });
                }

                planeContainer.appendChild(seatDiv);
            });
        })
        .catch(error => {
            console.error("Error fetching seat data:", error);
            alert("Failed to load seat data. Please refresh the page.");
        });

    // Handle seat confirmation and transition to payment page
    confirmButton.addEventListener("click", () => {
        if (!selectedSeat) {
            alert("Please select a seat before confirming.");
            return;
        }

        console.log("Attempting to reserve seat:", selectedSeat);

        // Corrected URL for POST request
        fetch(`/api/${flightId}/seats/select`, {  // Corrected URL
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ seat_number: selectedSeat }),
        })
            .then(response => {
                console.log("POST Response Status:", response.status);
                return response.text().then(text => {
                    try {
                        return JSON.parse(text);
                    } catch (e) {
                        console.error("Invalid JSON response:", text);
                        throw new Error("Server returned invalid JSON");
                    }
                });
            })
            .then(data => {
                console.log("POST Response Data:", data);

                if (data.error) {
                    console.error("Error during seat reservation:", data.error);
                    alert(`Error: ${data.error}`);
                } else {
                    // Successful reservation, redirect to payment
                    alert(data.message);
                    console.log("Redirecting to payment page...");
                    window.location.href = `/payment/${flightId}/${selectedSeat}`;
                }
            })
            .catch(error => {
                console.error("Error during seat reservation:", error);
                alert("Failed to reserve seat. Please try again.");
            });
    });
});
