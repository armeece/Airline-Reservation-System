document.addEventListener("DOMContentLoaded", function () {
    const planeContainer = document.getElementById("planeContainer");
    const confirmButton = document.getElementById("confirmButton");
    let selectedSeat = null;

    // Fetch seat list for the flight
    fetch(`/api/seats/${flightId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }

            data.seats.forEach(seat => {
                if (!seat.seat_number || !seat.seat_class) {
                    console.warn("Invalid seat data:", seat);
                    return;
                }

                const seatDiv = document.createElement("div");
                seatDiv.textContent = `${seat.seat_number} (${seat.seat_class})`;

                if (!seat.is_available) {
                    seatDiv.className = "seat unavailable";
                    seatDiv.style.pointerEvents = "none";
                } else {
                    seatDiv.className = "seat";
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
            alert("Failed to load seat data.");
        });

    // Handle seat confirmation
    confirmButton.addEventListener("click", () => {
        if (!selectedSeat) {
            alert("Please select a seat before confirming.");
            return;
        }

        // Debugging Update: Log errors and responses clearly
fetch(`/api/seats/${flightId}/select`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seat_number: selectedSeat }),
})
    .then(response => {
        console.log("Response Status:", response.status);
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error("Error:", data.error);
            alert(`Error: ${data.error}`);
        } else {
            console.log("Success:", data.message);
            alert(data.message);
            window.location.href = `/payment/${flightId}/${selectedSeat}`;
        }
    })
    .catch(error => {
        console.error("Error reserving seat:", error);
        alert("Failed to reserve seat.");
    });
    });
});
