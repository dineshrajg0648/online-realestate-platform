document.addEventListener('DOMContentLoaded', function() {
    loadTrips();
    
    const tripForm = document.getElementById('tripForm');
    tripForm.addEventListener('submit', handleTripSubmit);
});

async function loadTrips() {
    try {
        const response = await fetch('/api/trips');
        const trips = await response.json();
        displayTrips(trips);
    } catch (error) {
        console.error('Error loading trips:', error);
    }
}

function displayTrips(trips) {
    const tripsList = document.getElementById('tripsList');
    tripsList.innerHTML = '';
    
    trips.forEach(trip => {
        const tripCard = document.createElement('div');
        tripCard.className = 'col-md-6';
        tripCard.innerHTML = `
            <div class="card trip-card">
                <div class="card-body">
                    <h5 class="card-title">${trip.destination}</h5>
                    <p class="card-text">
                        <strong>Start Date:</strong> ${trip.start_date}<br>
                        <strong>End Date:</strong> ${trip.end_date}<br>
                        ${trip.description}
                    </p>
                </div>
            </div>
        `;
        tripsList.appendChild(tripCard);
    });
}

async function handleTripSubmit(event) {
    event.preventDefault();
    
    const tripData = {
        destination: document.getElementById('destination').value,
        start_date: document.getElementById('startDate').value,
        end_date: document.getElementById('endDate').value,
        description: document.getElementById('description').value
    };
    
    try {
        const response = await fetch('/api/trips', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tripData)
        });
        
        if (response.ok) {
            event.target.reset();
            loadTrips();
        } else {
            console.error('Error creating trip');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}
