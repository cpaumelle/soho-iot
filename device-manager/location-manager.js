class LocationManager {
    constructor() {
        this.apiBase = 'https://devices.sensemy.cloud/api';
        this.locations = [];
        this.editingLocation = null;
        this.init();
    }

    async init() {
        await this.loadLocations();
        this.renderLocationTree();
        this.setupEventListeners();
    }

    async loadLocations() {
        try {
            const response = await fetch(`${this.apiBase}/locations`);
            if (response.ok) {
                this.locations = await response.json();
                console.log('Loaded locations:', this.locations);
            } else {
                console.error('Failed to load locations:', response.status);
                this.locations = [];
            }
        } catch (error) {
            console.error('Error loading locations:', error);
            this.locations = [];
        }
    }

    renderLocationTree() {
        const treeContainer = document.getElementById("locationTree");
        
        if (this.locations.length === 0) {
            treeContainer.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="bi bi-building display-4 mb-3"></i>
                    <h5>No locations found</h5>
                    <p>Click "Add Location" to get started</p>
                </div>
            `;
            return;
        }

        treeContainer.innerHTML = '';
        
        this.locations.forEach(location => {
            const locationElement = this.createLocationElement(location);
            treeContainer.appendChild(locationElement);
        });
    }

    createLocationElement(location) {
        const div = document.createElement("div");
        div.className = "d-flex justify-content-between align-items-center p-3 mb-2 bg-light rounded border";
        
        // Get icon from location name or use default
        const icon = this.extractIcon(location.name) || '🏢';
        const cleanName = location.name.replace(/^[^\s]+ /, '') || location.name;
        
        div.innerHTML = `
            <div class="d-flex align-items-center">
                <span class="me-3" style="font-size: 1.5rem;">${icon}</span>
                <div>
                    <strong>${cleanName}</strong>
                    ${location.description ? `<small class="text-muted d-block">${location.description}</small>` : ''}
                </div>
            </div>
            <div class="btn-group btn-group-sm">
                <button class="btn btn-outline-primary btn-sm" onclick="locationManager.editLocation(${location.id})">
                    <i class="bi bi-pencil"></i> Edit
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="locationManager.deleteLocation(${location.id})">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </div>
        `;
        
        return div;
    }

    extractIcon(name) {
        const match = name.match(/^(\p{Emoji})/u);
        return match ? match[1] : null;
    }

    setupEventListeners() {
        document.getElementById("addSiteBtn").addEventListener("click", () => {
            this.openLocationModal();
        });

        document.getElementById("saveLocationBtn").addEventListener("click", () => {
            this.saveLocation();
        });
    }

    openLocationModal(location = null) {
        this.editingLocation = location;
        const modal = new bootstrap.Modal(document.getElementById("locationModal"));
        
        // Update modal title
        const title = location ? "Edit Location" : "Add Location";
        document.querySelector("#locationModal .modal-title").textContent = title;
        
        // Pre-populate form if editing
        if (location) {
            const icon = this.extractIcon(location.name);
            const cleanName = location.name.replace(/^[^\s]+ /, '') || location.name;
            
            document.getElementById("locationName").value = cleanName;
            document.getElementById("locationDescription").value = location.description || '';
            if (icon) {
                document.getElementById("locationIcon").value = icon;
            }
        } else {
            document.getElementById("locationForm").reset();
        }
        
        modal.show();
    }

    async saveLocation() {
        const form = document.getElementById("locationForm");
        if (!form.checkValidity()) {
            form.reportValidity();
            return;
        }
        
        const name = document.getElementById("locationName").value;
        const description = document.getElementById("locationDescription").value;
        const icon = document.getElementById("locationIcon").value;
        const fullName = icon ? `${icon} ${name}` : name;
        
        const locationData = {
            name: fullName,
            description: description
        };
        
        console.log("Saving location:", locationData);
        console.log("Editing location:", this.editingLocation);
        
        try {
            let response;
            
            if (this.editingLocation) {
                console.log("Updating location ID:", this.editingLocation.id);
                response = await fetch(`${this.apiBase}/locations/${this.editingLocation.id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(locationData)
                });
            } else {
                console.log("Creating new location");
                response = await fetch(`${this.apiBase}/locations`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(locationData)
                });
            }
            
            console.log("Response status:", response.status);
            const responseText = await response.text();
            console.log("Response body:", responseText);
            
            if (response.ok) {
                await this.loadLocations();
                this.renderLocationTree();
                bootstrap.Modal.getInstance(document.getElementById("locationModal")).hide();
                this.showNotification("Location saved successfully!", "success");
            } else {
                this.showNotification(`Failed to save location: ${responseText}`, "danger");
            }
        } catch (error) {
            console.error("Error saving location:", error);
            this.showNotification("Error saving location: " + error.message, "danger");
        }
    }
        
        const name = document.getElementById("locationName").value;
        const description = document.getElementById("locationDescription").value;
        const icon = document.getElementById("locationIcon").value;
        const fullName = icon ? `${icon} ${name}` : name;
        
        const locationData = {
            name: fullName,
            description: description
        };

        try {
            let response;
            
            if (this.editingLocation) {
                // Update existing location
                response = await fetch(`${this.apiBase}/locations/${this.editingLocation.id}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(locationData)
                });
            } else {
                // Create new location
                response = await fetch(`${this.apiBase}/locations`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(locationData)
                });
            }

            if (response.ok) {
                await this.loadLocations();
                this.renderLocationTree();
                bootstrap.Modal.getInstance(document.getElementById("locationModal")).hide();
                this.showNotification("Location saved successfully!", "success");
            } else {
                this.showNotification("Failed to save location", "danger");
            }
        } catch (error) {
            console.error('Error saving location:', error);
            this.showNotification("Error saving location", "danger");
        }
    }

    editLocation(id) {
        const location = this.locations.find(l => l.id === id);
        if (location) {
            this.openLocationModal(location);
        }
    }

    async deleteLocation(id) {
        const location = this.locations.find(l => l.id === id);
        const locationName = location ? location.name : 'this location';
        
        if (!confirm(`Are you sure you want to delete ${locationName}?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/locations/${id}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await this.loadLocations();
                this.renderLocationTree();
                this.showNotification("Location deleted successfully!", "success");
            } else {
                this.showNotification("Failed to delete location", "danger");
            }
        } catch (error) {
            console.error('Error deleting location:', error);
            this.showNotification("Error deleting location", "danger");
        }
    }

    showNotification(message, type = "info") {
        const toast = document.createElement("div");
        toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        toast.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 3000);
    }
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
    window.locationManager = new LocationManager();
});
