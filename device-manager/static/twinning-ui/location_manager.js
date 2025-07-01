// Location data - this would be synchronized with your main siteData
let locationData = [
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

let editingItem = null;
let editingType = null;
let parentContext = null;

document.addEventListener("DOMContentLoaded", () => {
  renderLocationTree();
  setupEventListeners();
});

function setupEventListeners() {
  // Add Site button
  document.getElementById("addSiteBtn").addEventListener("click", () => {
    openModal("site", "add");
  });

  // Save buttons
  document.getElementById("saveSiteBtn").addEventListener("click", saveSite);
  document.getElementById("saveFloorBtn").addEventListener("click", saveFloor);
  document.getElementById("saveRoomBtn").addEventListener("click", saveRoom);
}

function renderLocationTree() {
  const treeContainer = document.getElementById("locationTree");
  treeContainer.innerHTML = "";

  locationData.forEach(site => {
    const siteElement = createLocationElement(site, "site");
    treeContainer.appendChild(siteElement);

    // Add floors
    site.floors.forEach(floor => {
      const floorElement = createLocationElement(floor, "floor", site);
      treeContainer.appendChild(floorElement);

      // Add rooms
      floor.rooms.forEach(room => {
        const roomElement = createLocationElement(room, "room", floor, site);
        treeContainer.appendChild(roomElement);
      });
    });
  });
}

function createLocationElement(item, type, parent = null, grandparent = null) {
  const div = document.createElement("div");
  const indentClass = type === "site" ? "" : type === "floor" ? "ms-4" : "ms-5";
  
  div.className = `d-flex justify-content-between align-items-center p-2 mb-2 bg-light rounded ${indentClass}`;
  div.innerHTML = `
    <div class="d-flex align-items-center">
      <i class="bi bi-${getTypeIcon(type)} text-${getTypeColor(type)} me-2"></i>
      <strong>${item.name}</strong>
      ${type !== "site" ? `<small class="text-muted ms-2">(${item.cleanName})</small>` : ""}
    </div>
    <div class="btn-group btn-group-sm">
      ${type !== "room" ? `<button class="btn btn-outline-success btn-sm" onclick="addChild('${type}', ${item.id})">
        <i class="bi bi-plus"></i> Add ${getChildType(type)}
      </button>` : ""}
      <button class="btn btn-outline-primary btn-sm" onclick="editItem('${type}', ${item.id})">
        <i class="bi bi-pencil"></i>
      </button>
      <button class="btn btn-outline-danger btn-sm" onclick="deleteItem('${type}', ${item.id})">
        <i class="bi bi-trash"></i>
      </button>
    </div>
  `;
  
  return div;
}

function getTypeIcon(type) {
  const icons = {
    site: "building",
    floor: "layers",
    room: "door-open"
  };
  return icons[type] || "circle";
}

function getTypeColor(type) {
  const colors = {
    site: "primary",
    floor: "info", 
    room: "success"
  };
  return colors[type] || "secondary";
}

function getChildType(type) {
  const childTypes = {
    site: "Floor",
    floor: "Room"
  };
  return childTypes[type] || "";
}

function openModal(type, action, item = null) {
  editingType = type;
  editingItem = item;
  
  const modalId = `${type}Modal`;
  const modal = new bootstrap.Modal(document.getElementById(modalId));
  
  // Update modal title
  const title = action === "add" ? `Add ${type.charAt(0).toUpperCase() + type.slice(1)}` : 
                                   `Edit ${type.charAt(0).toUpperCase() + type.slice(1)}`;
  document.querySelector(`#${modalId} .modal-title`).textContent = title;
  
  // Pre-populate form if editing
  if (action === "edit" && item) {
    document.getElementById(`${type}Name`).value = item.cleanName || item.name.replace(/^[^\s]+ /, "");
    // Set icon if available
    const iconSelect = document.getElementById(`${type}Icon`);
    const currentIcon = item.name.split(" ")[0];
    if (iconSelect) {
      iconSelect.value = currentIcon;
    }
  } else {
    document.getElementById(`${type}Form`).reset();
  }
  
  modal.show();
}

function addChild(parentType, parentId) {
  parentContext = { type: parentType, id: parentId };
  const childType = parentType === "site" ? "floor" : "room";
  openModal(childType, "add");
}

function editItem(type, id) {
  const item = findItemById(type, id);
  if (item) {
    openModal(type, "edit", item);
  }
}

function deleteItem(type, id) {
  if (confirm(`Are you sure you want to delete this ${type}? This will also delete all child items.`)) {
    removeItemById(type, id);
    renderLocationTree();
    showNotification(`${type.charAt(0).toUpperCase() + type.slice(1)} deleted successfully!`, "success");
  }
}

function saveSite() {
  const form = document.getElementById("siteForm");
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }
  
  const name = document.getElementById("siteName").value;
  const icon = document.getElementById("siteIcon").value;
  const fullName = `${icon} ${name}`;
  
  if (editingItem) {
    // Edit existing site
    editingItem.name = fullName;
    editingItem.cleanName = name;
  } else {
    // Add new site
    const newId = Math.max(...locationData.map(s => s.id)) + 1;
    locationData.push({
      id: newId,
      name: fullName,
      cleanName: name,
      floors: []
    });
  }
  
  renderLocationTree();
  bootstrap.Modal.getInstance(document.getElementById("siteModal")).hide();
  showNotification("Site saved successfully!", "success");
}

function saveFloor() {
  const form = document.getElementById("floorForm");
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }
  
  const name = document.getElementById("floorName").value;
  const icon = document.getElementById("floorIcon").value;
  const fullName = `${icon} ${name}`;
  
  if (editingItem) {
    // Edit existing floor
    editingItem.name = fullName;
    editingItem.cleanName = name;
  } else if (parentContext) {
    // Add new floor to site
    const site = locationData.find(s => s.id === parentContext.id);
    if (site) {
      const newId = Math.max(...locationData.flatMap(s => s.floors.map(f => f.id))) + 1;
      site.floors.push({
        id: newId,
        name: fullName,
        cleanName: name,
        rooms: []
      });
    }
  }
  
  renderLocationTree();
  bootstrap.Modal.getInstance(document.getElementById("floorModal")).hide();
  showNotification("Floor saved successfully!", "success");
  parentContext = null;
}

function saveRoom() {
  const form = document.getElementById("roomForm");
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }
  
  const name = document.getElementById("roomName").value;
  const icon = document.getElementById("roomIcon").value;
  const fullName = `${icon} ${name}`;
  
  if (editingItem) {
    // Edit existing room
    editingItem.name = fullName;
    editingItem.cleanName = name;
  } else if (parentContext) {
    // Add new room to floor
    const site = locationData.find(s => s.floors.some(f => f.id === parentContext.id));
    const floor = site?.floors.find(f => f.id === parentContext.id);
    if (floor) {
      const newId = Math.max(...locationData.flatMap(s => s.floors.flatMap(f => f.rooms.map(r => r.id)))) + 1;
      floor.rooms.push({
        id: newId,
        name: fullName,
        cleanName: name
      });
    }
  }
  
  renderLocationTree();
  bootstrap.Modal.getInstance(document.getElementById("roomModal")).hide();
  showNotification("Room saved successfully!", "success");
  parentContext = null;
}

function findItemById(type, id) {
  if (type === "site") {
    return locationData.find(s => s.id === id);
  } else if (type === "floor") {
    for (const site of locationData) {
      const floor = site.floors.find(f => f.id === id);
      if (floor) return floor;
    }
  } else if (type === "room") {
    for (const site of locationData) {
      for (const floor of site.floors) {
        const room = floor.rooms.find(r => r.id === id);
        if (room) return room;
      }
    }
  }
  return null;
}

function removeItemById(type, id) {
  if (type === "site") {
    const index = locationData.findIndex(s => s.id === id);
    if (index > -1) locationData.splice(index, 1);
  } else if (type === "floor") {
    for (const site of locationData) {
      const index = site.floors.findIndex(f => f.id === id);
      if (index > -1) {
        site.floors.splice(index, 1);
        break;
      }
    }
  } else if (type === "room") {
    for (const site of locationData) {
      for (const floor of site.floors) {
        const index = floor.rooms.findIndex(r => r.id === id);
        if (index > -1) {
          floor.rooms.splice(index, 1);
          return;
        }
      }
    }
  }
}

function showNotification(message, type = "info") {
  // Create a simple toast notification
  const toast = document.createElement("div");
  toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
  toast.style.cssText = "top: 20px; right: 20px; z-index: 9999; min-width: 300px;";
  toast.innerHTML = `
    ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
  `;
  
  document.body.appendChild(toast);
  
  // Auto-dismiss after 3 seconds
  setTimeout(() => {
    if (toast.parentNode) {
      toast.remove();
    }
  }, 3000);
}