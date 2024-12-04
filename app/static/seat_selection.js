// #Dylaan - 11/30: 
// Updates and improvements by Addison M - 12/04

document.addEventListener("DOMContentLoaded", function () {
    const seatLayout = document.getElementById("seat-layout");
    const confirmBtn = document.getElementById("confirm-btn");
    let selectedSeat = null;

    // Replace this with the actual flight ID dynamically
    const flightId = new URLSearchParams(window.location.search).get("flight_id");

    if (!flightId) {
        alert("Flight ID is missing. Unable to load seat layout.");
        return;
    }

    // Fetch seat availability
    fetch(`/api/seats/${flightId}`)
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            if (data.error) {
                alert(data.error);
                return;
            }

            const { total_seats, booked_seats } = data;
            const rows = Math.ceil(total_seats / 6); // Assuming 6 seats per row (A-F)
            const reservedSeats = new Set(booked_seats);

            // Generate seat layout dynamically
            for (let row = 1; row <= rows; row++) {
                const rowDiv = document.createElement("div");
                rowDiv.className = "row";

                for (let col of ["A", "B", "C", "D", "E", "F"]) {
                    const seatNumber = `${row}${col}`;
                    const seat = document.createElement("div");
                    seat.className = "seat";
                    seat.textContent = seatNumber;

                    if (reservedSeats.has(seatNumber)) {
                        seat.classList.add("reserved");
                    } else {
                        seat.addEventListener("click", () => {
                            // Deselect previously selected seat
                            document.querySelectorAll(".seat.selected").forEach((el) => el.classList.remove("selected"));
                            seat.classList.add("selected");
                            selectedSeat = seatNumber;
                            confirmBtn.disabled = false;
                        });
                    }

                    rowDiv.appendChild(seat);
                }

                seatLayout.appendChild(rowDiv);
            }
        })
        .catch((error) => {
            console.error("Error fetching seat layout:", error);
            alert("Failed to load seat layout. Please try again later.");
        });

    // Confirm seat selection
    confirmBtn.addEventListener("click", () => {
        if (!selectedSeat) {
            alert("No seat selected. Please select a seat before confirming.");
            return;
        }

        fetch("/api/seats/reserve", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                flight_id: flightId,
                seat_number: selectedSeat,
            }),
        })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert(`Seat ${selectedSeat} reserved successfully!`);
                    location.reload();
                }
            })
            .catch((error) => {
                console.error("Error reserving seat:", error);
                alert("Failed to reserve seat. Please try again later.");
            });
    });
});
