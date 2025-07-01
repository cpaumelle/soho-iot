// Sample orphan devices data - this would come from your API
const orphanDevices = [
  {
    id: "sensor-003",
    firstSeen: "2h ago",
    payloadCount: 24,
    status: "new",
    lastPayload: {
      deveui: "sensor-003",
      timestamp: "2025-06-11T14:30:00Z",
      snr: 7.5,
      rssi: -85,
      data: "0A1B2C3D4E5F"
    }
  },
  {
    id: "sensor-007", 
    firstSeen: "6h ago",
    payloadCount: 8,
    status: "active",
    lastPayload: {
      deveui: "sensor-007",
      timestamp: "2025-06-11T12:15:00Z",
      snr: 6.2,
      rssi: -78,
      data: "1A2B3C4D5E6F"
    }
  },
  {
    id: "motion-012",
    firstSeen: "1d ago", 
    payloadCount: 156,
    status: "pending",
    lastPayload: {
      deveui: "motion-012",
      timestamp: "2025-06-10T16:45:00Z",
      snr: 8.1,
      rssi: -72,
      data: "2B3C4D5E6F7A"
    }
  }
];

const siteData = [
  {
    id: 1,
    name: "🏡 Home",
    cleanName: "Home",
    floors: [
      {
        id: 1,
        name: "🧱 Ground Floor",
        cleanName: "Ground Floor",
        rooms: [
          { id: 1, name: "🛋️ Living Room", cleanName: "Living Room" },
          { id: 2, name: "🍳 Kitchen", cleanName: "Kitchen" },
          { id: 3, name: "🚪 Entrance Hall", cleanName: "Entrance Hall" }
        ]
      },
      {
        id: 2,
        name: "📐 First Floor",
        cleanName: "First Floor",
        rooms: [
          { id: 4, name: "🛏️ Master Bedroom", cleanName: "Master Bedroom" },
          { id: 5, name: "🛏️ Guest Bedroom", cleanName: "Guest Bedroom" },
          { id: 6, name: "🚿 Bathroom", cleanName: "Bathroom" }
        ]
      }
    ]
  },
  {
    id: 2,
    name: "🏕️ Cabin",
    cleanName: "Cabin",
    floors: [
      {
        id: 3,
        name: "🪵 Main Floor",
        cleanName: "Main Floor",
        rooms: [
          { id: 7, name: "🔥 Fireplace Area", cleanName: "Fireplace Area" },
          { id: 8, name: "🛌 Loft", cleanName: "Loft" },
          { id: 9, name: "🍽️ Dining Area", cleanName: "Dining Area" }
        ]
      }
    ]
  },
  {
    id: 3,
    name: "🏢 Office",
    cleanName: "Office",
    floors: [
      {
        id: 4,
        name: "🏬 Level 1",
        cleanName: "Level 1",
        rooms: [
          { id: 10, name: "📋 Reception", cleanName: "Reception" },
          { id: 11, name: "🖥️ Open Office", cleanName: "Open Office" },
          { id: 12, name: "🏛️ Conference Room", cleanName: "Conference Room" }
        ]
      }
    ]
  }
];

const deviceModels = {
  environment: [
    { 
      id: "env1", 
      name: "Browan Tabs Healthy Home", 
      desc: "Multi-sensor for temperature, humidity, and ambient light monitoring. Decoder: v1.2",
      payload: '{"deveui": "env-001", "temp": 23.4, "humidity": 67, "light": 450, "battery": 85}',
      decoded: {
        temperature: "23.4°C",
        humidity: "67%", 
        light: "450 lux",
        battery: "85%"
      }
    },
    { 
      id: "env2", 
      name: "Milesight AM107", 
      desc: "Indoor environmental sensor with CO2 monitoring. Decoder: v1.0",
      payload: '{"deveui": "env-002", "temp": 22.1, "humidity": 45, "co2": 650, "battery": 92}',
      decoded: {
        temperature: "22.1°C",
        humidity: "45%",
        co2: "650 ppm",
        battery: "92%"
      }
    },
    {
      id: "env3",
      name: "Dragino LHT65",
      desc: "Temperature and humidity sensor with external probe support. Decoder: v2.1",
      payload: '{"deveui": "env-003", "temp": 24.8, "humidity": 58, "ext_temp": 26.2, "battery": 78}',
      decoded: {
        temperature: "24.8°C",
        humidity: "58%",
        external_temp: "26.2°C",
        battery: "78%"
      }
    }
  ],
  motion: [
    { 
      id: "mot1", 
      name: "Elsys EMS Lite", 
      desc: "Motion detection with temperature monitoring. Decoder: v2.0",
      payload: '{"deveui": "mot-001", "motion": true, "temp": 21.5, "battery": 91}',
      decoded: {
        motion: "Detected",
        temperature: "21.5°C",
        battery: "91%"
      }
    },
    {
      id: "mot2",
      name: "Milesight VS121",
      desc: "PIR motion sensor with configurable detection range. Decoder: v1.3",
      payload: '{"deveui": "mot-002", "occupancy": false, "lux": 120, "battery": 88}',
      decoded: {
        occupancy: "No motion",
        light: "120 lux",
        battery: "88%"
      }
    }
  ],
  energy: [
    { 
      id: "en1", 
      name: "Dragino LDS02", 
      desc: "Door/window sensor for open/close detection. Decoder: v1.5",
      payload: '{"deveui": "en-001", "door_open": false, "battery": 95, "tamper": false}',
      decoded: {
        status: "Closed",
        battery: "95%",
        tamper: "Secure"
      }
    },
    {
      id: "en2",
      name: "Globalsat LT-100",
      desc: "Smart energy meter with power consumption monitoring. Decoder: v2.2",
      payload: '{"deveui": "en-002", "power": 1250, "energy": 15.7, "voltage": 230}',
      decoded: {
        power: "1.25 kW",
        energy: "15.7 kWh",
        voltage: "230V"
      }
    }
  ]
};

let selectedCategory = null;
let selectedOrphanDevice = null;

document.addEventListener("DOMContentLoaded", () => {
  initializeForm();
  setupEventListeners();
  populateOrphanDevices();
});

function initializeForm() {
  populateSiteDropdown();
  // Auto-select environment category on load
  selectCategory("environment");
  // Auto-select first site to trigger the location cascade
  const siteSelect = document.getElementById("siteSelect");
  if (siteSelect.options.length > 1) {
    siteSelect.selectedIndex = 1; // Select first actual option (skip placeholder)
    populateFloorDropdown();
    // Auto-select first floor
    setTimeout(() => {
      const floorSelect = document.getElementById("floorSelect");
      if (floorSelect.options.length > 1) {
        floorSelect.selectedIndex = 1;
        populateRoomDropdown();
        // Auto-select first room
        setTimeout(() => {
          const roomSelect = document.getElementById("roomSelect");
          if (roomSelect.options.length > 1) {
            roomSelect.selectedIndex = 1;
            updateDeviceName();
          }
        }, 10);
      }
    }, 10);
  }
  
  // Disable twin button initially
  updateTwinButtonState();
}

function setupEventListeners() {
  // Device type button listeners
  document.querySelectorAll('.btn-group .btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const category = btn.dataset.category;
      selectCategory(category);
    });
  });

  // Location dropdowns
  document.getElementById("siteSelect").addEventListener("change", () => {
    populateFloorDropdown();
    updateDeviceName();
  });
  document.getElementById("floorSelect").addEventListener("change", () => {
    populateRoomDropdown();
    updateDeviceName();
  });
  document.getElementById("roomSelect").addEventListener("change", updateDeviceName);
  
  // Device model change
  document.getElementById("deviceModel").addEventListener("change", () => {
    updateModelPreview();
    updateDeviceName();
  });
  
  // Form submission
  document.getElementById("twinForm").addEventListener("submit", handleFormSubmit);
  
  // Preview more button
  document.getElementById("previewMoreBtn").addEventListener("click", previewMorePayloads);
}

function selectCategory(category) {
  selectedCategory = category;
  const modelSelect = document.getElementById("deviceModel");
  const desc = document.getElementById("modelDescription");

  // Update button states
  document.querySelectorAll(".btn-group .btn").forEach(btn => {
    btn.classList.remove("active");
    if (btn.dataset.category === category) {
      btn.classList.add("active");
    }
  });

  // Populate device models
  modelSelect.innerHTML = '<option value="">Select a model...</option>';
  const models = deviceModels[category] || [];
  
  models.forEach(model => {
    const opt = document.createElement("option");
    opt.value = model.id;
    opt.textContent = model.name;
    opt.dataset.desc = model.desc;
    modelSelect.appendChild(opt);
  });

  if (models.length > 0) {
    desc.textContent = `${models.length} model(s) available for ${category} devices`;
    // Auto-select first model
    modelSelect.value = models[0].id;
    updateModelPreview();
    updateDeviceName();
  } else {
    desc.textContent = "No models found for this category.";
  }
}

function updateModelPreview() {
  const modelSelect = document.getElementById("deviceModel");
  const desc = document.getElementById("modelDescription");
  const selectedModel = modelSelect.value;
  
  if (!selectedModel || !selectedCategory) return;
  
  const model = deviceModels[selectedCategory]?.find(m => m.id === selectedModel);
  if (model) {
    desc.textContent = model.desc;
    updatePayloadPreview(model);
    updateDecodedPreview(model);
  }
}

function updatePayloadPreview(model) {
  const preview = document.getElementById("payloadPreview");
  if (model.payload) {
    try {
      const parsed = JSON.parse(model.payload);
      preview.textContent = JSON.stringify(parsed, null, 2);
    } catch (e) {
      preview.textContent = model.payload;
    }
  }
}

function updateDecodedPreview(model) {
  const preview = document.getElementById("decodedPreview");
  if (model.decoded) {
    let html = '';
    Object.entries(model.decoded).forEach(([key, value]) => {
      const icon = getIconForKey(key);
      const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      html += `
        <div class="d-flex justify-content-between">
          <span><i class="bi bi-${icon}"></i> ${displayKey}:</span>
          <strong>${value}</strong>
        </div>
      `;
    });
    preview.innerHTML = html;
  }
}

function getIconForKey(key) {
  const iconMap = {
    temperature: 'thermometer text-danger',
    humidity: 'droplet text-info', 
    light: 'sun text-warning',
    battery: 'battery-half text-success',
    motion: 'activity text-primary',
    occupancy: 'person text-primary',
    status: 'door-open text-info',
    power: 'lightning text-warning',
    energy: 'plug text-success',
    voltage: 'cpu text-secondary',
    co2: 'cloud text-muted',
    external_temp: 'thermometer-snow text-info',
    tamper: 'shield-check text-success'
  };
  
  return iconMap[key] || 'circle';
}

function populateSiteDropdown() {
  const siteSelect = document.getElementById("siteSelect");
  siteSelect.innerHTML = '<option value="">Select site...</option>';
  
  siteData.forEach(site => {
    const opt = document.createElement("option");
    opt.value = site.id;
    opt.textContent = site.name;
    siteSelect.appendChild(opt);
  });
}

function populateFloorDropdown() {
  const siteId = parseInt(document.getElementById("siteSelect").value);
  const floorSelect = document.getElementById("floorSelect");
  const roomSelect = document.getElementById("roomSelect");
  
  floorSelect.innerHTML = '<option value="">Select floor...</option>';
  roomSelect.innerHTML = '<option value="">Select room...</option>';

  if (!siteId) return;

  const site = siteData.find(s => s.id === siteId);
  if (!site) return;

  site.floors.forEach(floor => {
    const opt = document.createElement("option");
    opt.value = floor.id;
    opt.textContent = floor.name;
    floorSelect.appendChild(opt);
  });
}

function populateRoomDropdown() {
  const siteId = parseInt(document.getElementById("siteSelect").value);
  const floorId = parseInt(document.getElementById("floorSelect").value);
  const roomSelect = document.getElementById("roomSelect");
  
  roomSelect.innerHTML = '<option value="">Select room...</option>';

  if (!siteId || !floorId) return;

  const site = siteData.find(s => s.id === siteId);
  const floor = site?.floors.find(f => f.id === floorId);
  if (!floor) return;

  floor.rooms.forEach(room => {
    const opt = document.createElement("option");
    opt.value = room.id;
    opt.textContent = room.name;
    roomSelect.appendChild(opt);
  });
}

function previewMorePayloads() {
  // This would typically open a modal or navigate to a detailed view
  alert("This would show more payload examples in a modal or detailed view");
}

function handleFormSubmit(e) {
  e.preventDefault();
  
  // Collect form data
  const formData = {
    deviceType: selectedCategory,
    deviceModel: document.getElementById("deviceModel").value,
    deviceName: document.getElementById("deviceName").value,
    site: document.getElementById("siteSelect").value,
    floor: document.getElementById("floorSelect").value,
    room: document.getElementById("roomSelect").value,
    reprocessData: document.getElementById("reprocessData").checked
  };
  
  // Validate required fields
  if (!formData.deviceModel || !formData.deviceName || !formData.site || !formData.floor || !formData.room) {
    alert("Please fill in all required fields");
    return;
  }
  
  console.log("Device twinning configuration:", formData);
  
  // Here you would normally send to your FastAPI backend
  // For now, show success message
  if (confirm(`Device "${selectedOrphanDevice}" twinned successfully! Would you like to twin another device?`)) {
    // Remove the twinned device from orphan list
    removeOrphanDevice(selectedOrphanDevice);
    // Reset form for next device
    resetTwinningForm();
  }
}

function populateOrphanDevices() {
  const orphanList = document.getElementById("orphanDevicesList");
  const orphanCount = document.getElementById("orphanCount");
  
  orphanList.innerHTML = "";
  orphanCount.textContent = orphanDevices.length;
  
  orphanDevices.forEach(device => {
    const listItem = document.createElement("div");
    listItem.className = "list-group-item orphan-device-item";
    listItem.dataset.deviceId = device.id;
    
    const statusClass = device.status === "new" ? "success" : 
                       device.status === "active" ? "info" : "secondary";
    
    listItem.innerHTML = `
      <div class="d-flex justify-content-between align-items-start">
        <div class="flex-grow-1">
          <div class="device-id">${device.id}</div>
          <div class="device-meta">
            First seen: ${device.firstSeen}<br>
            ${device.payloadCount} payloads received
          </div>
        </div>
        <span class="badge bg-${statusClass} status-badge ${device.status}">${device.status}</span>
      </div>
    `;
    
    listItem.addEventListener("click", () => selectOrphanDevice(device));
    orphanList.appendChild(listItem);
  });
}

function selectOrphanDevice(device) {
  selectedOrphanDevice = device.id;
  
  // Update UI to show selected device
  document.querySelectorAll(".orphan-device-item").forEach(item => {
    item.classList.remove("active");
  });
  document.querySelector(`[data-device-id="${device.id}"]`).classList.add("active");
  
  // Update header
  document.getElementById("selectedDeviceId").textContent = device.id;
  
  // Update payload preview with real device data
  updatePayloadPreview({ payload: JSON.stringify(device.lastPayload, null, 2) });
  
  // Enable twin button
  updateTwinButtonState();
}

function removeOrphanDevice(deviceId) {
  const index = orphanDevices.findIndex(d => d.id === deviceId);
  if (index > -1) {
    orphanDevices.splice(index, 1);
    populateOrphanDevices();
  }
}

function resetTwinningForm() {
  selectedOrphanDevice = null;
  document.getElementById("selectedDeviceId").textContent = "Select a device";
  document.getElementById("twinForm").reset();
  document.querySelectorAll(".orphan-device-item").forEach(item => {
    item.classList.remove("active");
  });
  selectCategory("environment");
  populateSiteDropdown();
  updateTwinButtonState();
}

function updateTwinButtonState() {
  const twinButton = document.getElementById("twinButton");
  twinButton.disabled = !selectedOrphanDevice;
}

function updateDeviceName() {
  const deviceNameInput = document.getElementById("deviceName");
  const modelSelect = document.getElementById("deviceModel");
  const siteSelect = document.getElementById("siteSelect");
  const floorSelect = document.getElementById("floorSelect");
  const roomSelect = document.getElementById("roomSelect");
  
  // Get selected values
  const selectedModel = modelSelect.value;
  const selectedSite = siteSelect.value;
  const selectedFloor = floorSelect.value;
  const selectedRoom = roomSelect.value;
  
  console.log("updateDeviceName called:", {selectedModel, selectedSite, selectedFloor, selectedRoom});
  
  // Find the actual names (not IDs) - using cleanName for locations
  let deviceModelName = "";
  let siteName = "";
  let floorName = "";
  let roomName = "";
  
  if (selectedModel && selectedCategory) {
    const model = deviceModels[selectedCategory]?.find(m => m.id === selectedModel);
    deviceModelName = model ? model.name : "";
  }
  
  if (selectedSite) {
    const site = siteData.find(s => s.id === parseInt(selectedSite));
    siteName = site ? site.cleanName : "";
  }
  
  if (selectedFloor && selectedSite) {
    const site = siteData.find(s => s.id === parseInt(selectedSite));
    const floor = site?.floors.find(f => f.id === parseInt(selectedFloor));
    floorName = floor ? floor.cleanName : "";
  }
  
  if (selectedRoom && selectedFloor && selectedSite) {
    const site = siteData.find(s => s.id === parseInt(selectedSite));
    const floor = site?.floors.find(f => f.id === parseInt(selectedFloor));
    const room = floor?.rooms.find(r => r.id === parseInt(selectedRoom));
    roomName = room ? room.cleanName : "";
  }
  
  // Build the device name
  let autoName = "";
  if (deviceModelName) {
    autoName = deviceModelName;
    if (siteName && floorName && roomName) {
      autoName += ` | ${siteName} | ${floorName} | ${roomName}`;
    }
  }
  
  console.log("Generated name:", autoName);
  
  // Only update if the current value is empty or matches the previous auto-generated pattern
  const currentValue = deviceNameInput.value;
  if (!currentValue || currentValue.includes(" | ")) {
    deviceNameInput.value = autoName;
  }
}