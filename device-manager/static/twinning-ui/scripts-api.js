class DeviceManager {
    constructor() {
        this.apiBase = 'http://10.44.1.221:9001/api';
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
        console.log('DeviceManager initialized with API connection');
    }
    
    async loadOrphanDevices() {
        try {
            const response = await fetch(`${this.apiBase}/orphans`);
            this.orphanDevices = await response.json();
            console.log('Loaded orphan devices:', this.orphanDevices);
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
        } catch (error) {
            console.error('Error loading locations:', error);
            this.locations = [];
        }
    }
    
    setupCategoryButtons() {
        // Find all category buttons and add click handlers
        const categoryButtons = document.querySelectorAll('[data-category]');
        categoryButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const category = button.getAttribute('data-category') || button.textContent.toLowerCase().trim();
                this.selectCategory(category);
            });
        });
        
        // If no data-category attributes, try to find buttons by content
        if (categoryButtons.length === 0) {
            const buttons = document.querySelectorAll('button');
            buttons.forEach(button => {
                const text = button.textContent.toLowerCase().trim();
                if (['environment', 'motion', 'energy'].includes(text)) {
                    button.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.selectCategory(text);
                    });
                }
            });
        }
        
        console.log('Category buttons setup complete');
    }
    
    selectCategory(category) {
        this.selectedCategory = category.toLowerCase();
        console.log('Selected category:', this.selectedCategory);
        
        // Update button styles
        this.updateCategoryButtonStyles();
        
        // Filter and populate device types for this category
        this.populateDeviceTypesForCategory();
    }
    
    updateCategoryButtonStyles() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            const text = button.textContent.toLowerCase().trim();
            if (['environment', 'motion', 'energy'].includes(text)) {
                if (text === this.selectedCategory) {
                    button.classList.add('active');
                    button.classList.remove('btn-outline-primary');
                    button.classList.add('btn-primary');
                } else {
                    button.classList.remove('active');
                    button.classList.remove('btn-primary');
                    button.classList.add('btn-outline-primary');
                }
            }
        });
    }
    
    populateDeviceTypesForCategory() {
        const select = document.getElementById('deviceModel');
        if (!select) {
            console.error('Device model select not found');
            return;
        }
        
        // Filter device types by selected category
        const filteredTypes = this.deviceTypes.filter(type => 
            type.category.toLowerCase() === this.selectedCategory
        );
        
        if (filteredTypes.length === 0) {
            select.innerHTML = '<option value="">No devices available for this category</option>';
            return;
        }
        
        select.innerHTML = '<option value="">Select device type...</option>' +
            filteredTypes.map(type => `
                <option value="${type.id}">
                    ${type.name}
                </option>
            `).join('');
        
        // Remove existing event listeners and add new one
        select.removeEventListener('change', this.showDeviceTypeDetails.bind(this));
        select.addEventListener('change', this.showDeviceTypeDetails.bind(this));
        
        console.log(`Populated ${filteredTypes.length} device types for category: ${this.selectedCategory}`);
    }
    
    renderOrphanDevices() {
        const container = document.getElementById('orphanDevicesList');
        const countBadge = document.getElementById('orphanCount');
        
        if (!container) {
            console.error('Orphan devices container not found');
            return;
        }
        
        // Update the count badge
        if (countBadge) {
            countBadge.textContent = this.orphanDevices.length;
        }
        
        if (this.orphanDevices.length === 0) {
            container.innerHTML = '<div class="p-3 text-center text-muted">No orphan devices found. All devices have been twinned!</div>';
            return;
        }
        
        // Create list items for each orphan device
        container.innerHTML = this.orphanDevices.map(device => `
            <div class="list-group-item list-group-item-action ${this.selectedDevice?.deveui === device.deveui ? 'active' : ''}" 
                 onclick="deviceManager.selectDevice('${device.deveui}')"
                 style="cursor: pointer;">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1 font-monospace">${device.deveui}</h6>
                    <small class="badge bg-${this.getStatusColor(device.status)}">${device.status}</small>
                </div>
                <p class="mb-1">
                    <small class="text-muted">
                        First seen: ${device.first_seen} • Last seen: ${device.last_seen} • Messages: ${device.payload_count}
                    </small>
                </p>
                <small class="text-muted">
                    Latest: ${JSON.stringify(device.last_payload).substring(0, 100)}...
                </small>
            </div>
        `).join('');
        
        console.log('Orphan devices rendered');
    }
    
    getStatusColor(status) {
        switch(status) {
            case 'active': return 'success';
            case 'recent': return 'warning';
            case 'inactive': return 'danger';
            default: return 'secondary';
        }
    }
    
    selectDevice(deveui) {
        console.log('Selected device:', deveui);
        this.selectedDevice = this.orphanDevices.find(d => d.deveui === deveui);
        
        // Re-render devices to show selection
        this.renderOrphanDevices();
        
        // Update the selected device display
        const selectedDisplay = document.getElementById('selectedDeviceId');
        if (selectedDisplay) {
            selectedDisplay.textContent = deveui;
        }
        
        // Reset category selection
        this.selectedCategory = null;
        this.updateCategoryButtonStyles();
        
        // Clear device model dropdown
        const select = document.getElementById('deviceModel');
        if (select) {
            select.innerHTML = '<option value="">Select a device category first</option>';
        }
        
        // Clear device type details
        const description = document.getElementById('modelDescription');
        if (description) {
            description.innerHTML = 'Select a device category to see available models';
        }
        
        // Populate locations
        this.populateLocations();
        
        // Enable the twin button
        const twinButton = document.getElementById('twinButton');
        if (twinButton) {
            twinButton.disabled = false;
        }
        
        // Update payload preview
        this.updatePayloadPreview();
        
        console.log('Device selected and form populated');
    }
    
    updatePayloadPreview() {
        const payloadPreview = document.getElementById('payloadPreview');
        if (payloadPreview && this.selectedDevice) {
            payloadPreview.textContent = JSON.stringify(this.selectedDevice.last_payload, null, 2);
        }
    }
    
    showDeviceTypeDetails() {
        const select = document.getElementById('deviceModel');
        const description = document.getElementById('modelDescription');
        const decodedPreview = document.getElementById('decodedPreview');
        
        if (!select) return;
        
        const selectedType = this.deviceTypes.find(t => t.id === select.value);
        
        if (!selectedType) {
            if (description) description.innerHTML = 'Select a device type to see details';
            if (decodedPreview) decodedPreview.innerHTML = '<div class="text-muted">Select a device type to see decoded preview</div>';
            return;
        }
        
        if (description) {
            description.innerHTML = `
                <strong>${selectedType.name}</strong><br>
                <em>${selectedType.description}</em><br>
                Decoder: ${selectedType.decoder_version}
            `;
        }
        
        if (decodedPreview) {
            decodedPreview.innerHTML = `
                <h6>Sample Decoded Output:</h6>
                <pre class="small">${JSON.stringify(selectedType.sample_decoded, null, 2)}</pre>
            `;
        }
        
        console.log('Device type details shown');
    }
    
    populateLocations() {
        const siteSelect = document.getElementById('siteSelect');
        if (!siteSelect) {
            console.error('Site select not found');
            return;
        }
        
        siteSelect.innerHTML = '<option value="">Select site...</option>' +
            this.locations.map(site => `
                <option value="${site.id}">${site.name}</option>
            `).join('');
        
        // Remove existing event listeners and add new one
        siteSelect.removeEventListener('change', this.populateFloors.bind(this));
        siteSelect.addEventListener('change', this.populateFloors.bind(this));
        
        console.log('Sites populated');
    }
    
    populateFloors() {
        const siteSelect = document.getElementById('siteSelect');
        const floorSelect = document.getElementById('floorSelect');
        
        if (!siteSelect || !floorSelect) return;
        
        const selectedSite = this.locations.find(s => s.id == siteSelect.value);
        
        if (!selectedSite) {
            floorSelect.innerHTML = '<option value="">Select floor...</option>';
            this.clearRooms();
            return;
        }
        
        floorSelect.innerHTML = '<option value="">Select floor...</option>' +
            selectedSite.floors.map(floor => `
                <option value="${floor.id}">${floor.name}</option>
            `).join('');
        
        floorSelect.removeEventListener('change', this.populateRooms.bind(this));
        floorSelect.addEventListener('change', this.populateRooms.bind(this));
        this.clearRooms();
        
        console.log('Floors populated for site:', selectedSite.name);
    }
    
    populateRooms() {
        const siteSelect = document.getElementById('siteSelect');
        const floorSelect = document.getElementById('floorSelect');
        const roomSelect = document.getElementById('roomSelect');
        
        if (!siteSelect || !floorSelect || !roomSelect) return;
        
        const selectedSite = this.locations.find(s => s.id == siteSelect.value);
        const selectedFloor = selectedSite?.floors.find(f => f.id == floorSelect.value);
        
        if (!selectedFloor) {
            roomSelect.innerHTML = '<option value="">Select room...</option>';
            return;
        }
        
        roomSelect.innerHTML = '<option value="">Select room...</option>' +
            selectedFloor.rooms.map(room => `
                <option value="${room.id}">${room.name}</option>
            `).join('');
        
        console.log('Rooms populated for floor:', selectedFloor.name);
    }
    
    clearRooms() {
        const roomSelect = document.getElementById('roomSelect');
        if (roomSelect) roomSelect.innerHTML = '<option value="">Select room...</option>';
    }
    
    async twinDevice(event) {
        event.preventDefault();
        
        if (!this.selectedDevice) {
            alert('Please select a device first.');
            return;
        }
        
        const deviceType = document.getElementById('deviceModel')?.value;
        const site = document.getElementById('siteSelect')?.value;
        const floor = document.getElementById('floorSelect')?.value;
        const room = document.getElementById('roomSelect')?.value;
        const deviceName = document.getElementById('deviceName')?.value;
        
        if (!deviceType || !site || !floor || !room || !deviceName) {
            alert('Please fill in all required fields.');
            return;
        }
        
        const twinButton = document.getElementById('twinButton');
        if (twinButton) {
            twinButton.disabled = true;
            twinButton.textContent = 'Twinning...';
        }
        
        try {
            const config = {
                deveui: this.selectedDevice.deveui,
                device_type_id: deviceType,
                site_id: parseInt(site),
                floor_id: parseInt(floor),
                room_id: parseInt(room),
                zone_id: null, // No zone select in your HTML
                device_name: deviceName
            };
            
            console.log('Twinning device with config:', config);
            
            const response = await fetch(`${this.apiBase}/twin-device`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                alert(`Success! Device ${this.selectedDevice.deveui} has been twinned as "${deviceName}"`);
                
                // Refresh the orphan devices list
                await this.loadOrphanDevices();
                this.renderOrphanDevices();
                
                // Reset form
                document.getElementById('twinForm').reset();
                document.getElementById('selectedDeviceId').textContent = 'Select a device';
                
                this.selectedDevice = null;
                this.selectedCategory = null;
                this.updateCategoryButtonStyles();
                
                console.log('Device twinned successfully');
            } else {
                alert(`Error: ${result.detail || 'Failed to twin device'}`);
                console.error('Twinning error:', result);
            }
            
        } catch (error) {
            console.error('Error twinning device:', error);
            alert('Error: Failed to twin device. Please check the console for details.');
        } finally {
            if (twinButton) {
                twinButton.disabled = true;
                twinButton.textContent = '🔗 Twin Device';
            }
        }
    }
    
    setupEventListeners() {
        const twinForm = document.getElementById('twinForm');
        if (twinForm) {
            twinForm.addEventListener('submit', (e) => this.twinDevice(e));
            console.log('Twin form event listener added');
        } else {
            console.error('Twin form not found');
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing DeviceManager');
    window.deviceManager = new DeviceManager();
});
