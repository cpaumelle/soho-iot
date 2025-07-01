class DeviceManager {
    constructor() {
        this.apiBase = 'https://devices.sensemy.cloud/api';
        this.orphanDevices = [];
        this.deviceTypes = [];
        this.locations = [];
        this.selectedDevice = null;
        this.selectedCategory = null;

        this.init();
    }

    async init() {
        await this.loadOrphanDevices();
        await this.loadDeviceTypes();
        await this.loadLocations();
        this.renderOrphanDevices();
        this.setupEventListeners();
        this.setupCategoryButtons();
        this.updateTwinFormState();
        console.log('DeviceManager initialized with API connection');
    }

    async loadOrphanDevices() {
        try {
            const response = await fetch(`${this.apiBase}/orphans`);
            this.orphanDevices = await response.json();
            console.log('Loaded orphan devices:', this.orphanDevices);
            
            // Update the count badge
            const badge = document.querySelector('.orphan-count');
            if (badge) {
                badge.textContent = this.orphanDevices.length;
            }
        } catch (error) {
            console.error('Error loading orphan devices:', error);
            this.orphanDevices = [];
        }
    }

    async loadDeviceTypes() {
        try {
            const response = await fetch(`${this.apiBase}/device-types`);
            this.deviceTypes = await response.json();
            console.log('Loaded device types:', this.deviceTypes);
        } catch (error) {
            console.error('Error loading device types:', error);
            this.deviceTypes = [];
        }
    }

    async loadLocations() {
        try {
            const response = await fetch(`${this.apiBase}/locations`);
            this.locations = await response.json();
            console.log('Loaded locations:', this.locations);
            this.populateLocationDropdowns();
        } catch (error) {
            console.error('Error loading locations:', error);
            this.locations = [];
        }
    }

    populateLocationDropdowns() {
        const siteSelect = document.getElementById('siteSelect');
        if (siteSelect && this.locations.length > 0) {
            siteSelect.innerHTML = '<option value="">Select site...</option>' +
                this.locations.map(loc => 
                    `<option value="${loc.id}">${loc.name}</option>`
                ).join('');
        }
    }

    renderOrphanDevices() {
        const container = document.getElementById('orphanDevicesList');
        if (!container) return;

        if (this.orphanDevices.length === 0) {
            container.innerHTML = '<p class="text-gray-500 p-4">No orphan devices found</p>';
            return;
        }

        container.innerHTML = this.orphanDevices.map(device => `
            <div class="orphan-device ${this.selectedDevice?.device_id === device.device_id ? 'selected' : ''}" 
                 data-device-id="${device.device_id}" onclick="window.deviceManager.selectDevice('${device.device_id}')">
                <div class="device-id">${device.device_id}</div>
                <div class="device-info">
                    <div class="device-times">
                        <div>First seen: ${new Date(device.first_seen).toLocaleString()}</div>
                        <div>Last seen: ${new Date(device.last_seen).toLocaleString()}</div>
                    </div>
                    <div class="device-stats">Messages: ${device.message_count}</div>
                    <div class="device-status">Latest: ${device.latest_status}</div>
                </div>
            </div>
        `).join('');
    }

    selectDevice(deviceId) {
        this.selectedDevice = this.orphanDevices.find(d => d.device_id === deviceId);
        console.log('Selected device:', this.selectedDevice);
        this.renderOrphanDevices();
        this.updateTwinFormState();
    }

    setupCategoryButtons() {
        const buttons = document.querySelectorAll('[data-category]');
        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                this.selectCategory(category);
            });
        });
    }

    selectCategory(category) {
        console.log('Selected category:', category);
        this.selectedCategory = category;
        
        // Update button states
        document.querySelectorAll('[data-category]').forEach(btn => {
            btn.classList.remove('selected');
        });
        document.querySelector(`[data-category="${category}"]`).classList.add('selected');
        
        this.populateDeviceTypes(category);
    }

    populateDeviceTypes(category) {
        const select = document.getElementById('deviceModel');
        if (!select) return;

        const filteredTypes = this.deviceTypes.filter(type => 
            type.decoder_function === category
        );

        if (filteredTypes.length === 0) {
            select.innerHTML = '<option value="">No devices available for this category</option>';
            return;
        }

        select.innerHTML = '<option value="">Select a device model</option>' +
            filteredTypes.map(type => 
                `<option value="${type.id}">${type.name} - ${type.manufacturer} ${type.model}</option>`
            ).join('');
    }

    updateTwinFormState() {
        const hasDevice = !!this.selectedDevice;
        
        // Show/hide form sections based on device selection
        const deviceTypeSection = document.getElementById('deviceTypeSection');
        const locationSection = document.getElementById('locationSection');
        const deviceNameSection = document.getElementById('deviceNameSection');
        
        if (deviceTypeSection) {
            deviceTypeSection.style.display = hasDevice ? 'block' : 'none';
        }
        if (locationSection) {
            locationSection.style.display = hasDevice ? 'block' : 'none';
        }
        if (deviceNameSection) {
            deviceNameSection.style.display = hasDevice ? 'block' : 'none';
        }

        // Update step numbers opacity
        document.querySelectorAll('.step-number').forEach((step, index) => {
            if (index === 0 || hasDevice) {
                step.style.opacity = '1';
            } else {
                step.style.opacity = '0.5';
            }
        });
    }

    async twinDevice(e) {
        e.preventDefault();
        
        if (!this.selectedDevice) {
            alert('Please select a device first');
            return;
        }

        const deviceType = document.getElementById('deviceModel')?.value;
        const deviceName = document.getElementById('deviceName')?.value;

        if (!deviceType || !deviceName) {
            alert('Please fill in all required fields');
            return;
        }

        try {
            const config = {
                device_id: this.selectedDevice.device_id,
                device_type_id: parseInt(deviceType),
                name: deviceName
            };

            const response = await fetch(`${this.apiBase}/twin-device`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });

            if (response.ok) {
                alert('Device twinned successfully!');
                this.selectedDevice = null;
                this.selectedCategory = null;
                await this.init(); // Reload everything
            } else {
                const error = await response.text();
                alert(`Failed to twin device: ${error}`);
            }
        } catch (error) {
            console.error('Error twinning device:', error);
            alert('Error twinning device');
        }
    }

    setupEventListeners() {
        const twinForm = document.getElementById('twinForm');
        if (twinForm) {
            twinForm.addEventListener('submit', (e) => this.twinDevice(e));
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing DeviceManager');
    window.deviceManager = new DeviceManager();
});
