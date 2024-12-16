document.addEventListener("DOMContentLoaded", function () {
    const planeContainer = document.getElementById("planeContainer");
    const confirmButton = document.getElementById("confirmButton");
    let selectedSeat = null;

    // Fetch seat availability for the flight
    fetch(`/api/seats/${flightId}`)  // Correctly use flightId
        .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            const { seats } = data;

            seats.forEach(seat => {
                const seatDiv = document.createElement("div");
                seatDiv.className = "seat";
                seatDiv.textContent = seat.seat_number;

                if (!seat.is_available) {
                    seatDiv.classList.add("unavailable");
                } else {
                    seatDiv.addEventListener("click", () => {
                        document.querySelectorAll(".seat.selected").forEach(el => el.classList.remove("selected"));
                        seatDiv.classList.add("selected");
                        selectedSeat = seat.seat_number;
                        confirmButton.disabled = false;
                    });
                }

                planeContainer.appendChild(seatDiv);
            });
        })
        .catch(error => {
            console.error("Error fetching seat data:", error);
            alert("Failed to load seat data. Please try again later.");
        });

    // Handle seat confirmation
    confirmButton.addEventListener("click", () => {
        if (!selectedSeat) {
            alert("No seat selected. Please select a seat before confirming.");
            return;
        }

        fetch(`/api/flights/${flightId}/seats`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ seat_number: selectedSeat }),
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(`Seat ${selectedSeat} reserved successfully!`);
                    window.location.href = `/payment/${flightId}/${selectedSeat}`;  // Redirect to payment
                }
            })
            .catch(error => {
                console.error("Error reserving seat:", error);
                alert("Failed to reserve seat. Please try again later.");
            });
    });
});
