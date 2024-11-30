document.addEventListener("DOMContentLoaded", function () {
    const seatLayout = document.getElementById("seat-layout");
    const confirmBtn = document.getElementById("confirm-btn");
    let selectedSeat = null;

    // Fetch seat availability
    fetch("/api/seats?flight_id=123") // Replace 123 with the actual flight ID
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                alert(data.error);
                return;
            }

            const layout = data.seat_layout;
            const reserved = data.reserved_seats;

            for (const row in layout) {
                const rowDiv = document.createElement("div");
                rowDiv.className = "row";

                layout[row].forEach((col) => {
                    const seat = document.createElement("div");
                    seat.className = "seat";
                    seat.textContent = `${row}${col}`;

                    if (reserved.some((r) => r.row === row && r.col === col)) {
                        seat.classList.add("reserved");
                    } else {
                        seat.addEventListener("click", () => {
                            document.querySelectorAll(".seat.selected").forEach((el) => el.classList.remove("selected"));
                            seat.classList.add("selected");
                            selectedSeat = { row, col };
                            confirmBtn.disabled = false;
                        });
                    }

                    rowDiv.appendChild(seat);
                });

                seatLayout.appendChild(rowDiv);
            }
        })
        .catch((error) => console.error("Error fetching seat layout:", error));

    // Confirm seat selection
    confirmBtn.addEventListener("click", () => {
        if (!selectedSeat) return;

        fetch("/api/seats/reserve", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                flight_id: 123, // Replace with the actual flight ID
                seat: selectedSeat,
            }),
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.error) {
                    alert(data.error);
                } else {
                    alert("Seat reserved successfully!");
                    location.reload();
                }
            })
            .catch((error) => console.error("Error reserving seat:", error));
    });
});
