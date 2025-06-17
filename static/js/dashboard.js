document.addEventListener('DOMContentLoaded', function() {
  // Navigation
  const navItems = document.querySelectorAll('.sidebar-nav li');
  const sections = document.querySelectorAll('.dashboard-section');
  const sectionTitle = document.getElementById('section-title');
  
  navItems.forEach(item => {
      item.addEventListener('click', () => {
          const target = item.getAttribute('data-target');
          
          // Update active class on nav items
          navItems.forEach(navItem => navItem.classList.remove('active'));
          item.classList.add('active');
          
          // Update visible section
          sections.forEach(section => {
              section.classList.remove('active');
              if (section.id === target) {
                  section.classList.add('active');
                  sectionTitle.textContent = section.querySelector('h2').textContent;
              }
          });
      });
  });
  
  // Load requests on page load
  loadAllRequests();
  
  // Refresh buttons
  document.getElementById('refresh-pending').addEventListener('click', () => {
      loadRequests('pending');
  });
  
  document.getElementById('refresh-authorized').addEventListener('click', () => {
      loadRequests('authorized');
  });
  
  document.getElementById('refresh-banned').addEventListener('click', () => {
      loadRequests('banned');
  });
  
  // Modal close button
  const modal = document.getElementById('notification-modal');
  const modalClose = document.querySelector('.modal-close');
  
  modalClose.addEventListener('click', () => {
      modal.style.display = 'none';
  });
  
  // Close modal when clicking outside
  window.addEventListener('click', (e) => {
      if (e.target === modal) {
          modal.style.display = 'none';
      }
  });
  
  // Set up polling for new requests (every 30 seconds)
  setInterval(() => {
      checkForNewRequests();
  }, 30000);
});

// Global variables to track requests
let allRequests = [];
let lastRequestTime = new Date().toISOString();

// Function to load all types of requests
function loadAllRequests() {
  loadRequests('pending');
  loadRequests('authorized');
  loadRequests('banned');
}

// Function to load requests by type
function loadRequests(type) {
  const url = '/api/requests';
  
  fetch(url)
      .then(response => response.json())
      .then(data => {
          allRequests = data;
          
          // Update counters
          document.getElementById('pending-count').textContent = 
              data.filter(request => request.status === 'Pending').length;
          document.getElementById('authorized-count').textContent = 
              data.filter(request => request.status === 'Authorized').length;
          document.getElementById('banned-count').textContent = 
              data.filter(request => request.status === 'Banned').length;
          
          // Filter requests based on type
          let filteredRequests;
          let containerId;
          
          switch(type) {
              case 'pending':
                  filteredRequests = data.filter(request => request.status === 'Pending');
                  containerId = 'pending-container';
                  break;
              case 'authorized':
                  filteredRequests = data.filter(request => request.status === 'Authorized');
                  containerId = 'authorized-container';
                  break;
              case 'banned':
                  filteredRequests = data.filter(request => request.status === 'Banned');
                  containerId = 'banned-container';
                  break;
              default:
                  return;
          }
          
          renderRequests(filteredRequests, containerId, type);
      })
      .catch(error => {
          console.error('Error loading requests:', error);
          document.getElementById(`${type}-container`).innerHTML = 
              `<div class="error-message">Error loading data. Please try again.</div>`;
      });
}

// Function to render requests into container
function renderRequests(requests, containerId, type) {
  const container = document.getElementById(containerId);
  
  if (requests.length === 0) {
      container.innerHTML = `<div class="no-data">No ${type} requests found.</div>`;
      return;
  }
  
  let html = '';
  
  requests.forEach(request => {
      const isPending = request.status === 'Pending';
      
      html += `
          <div class="card" data-id="${request.face_id}">
              <div class="card-header">
                  <div class="card-title">Face ID: ${request.face_id.substring(0, 8)}...</div>
                  <span class="status status-${request.status.toLowerCase()}">${request.status}</span>
              </div>
              <div class="card-body">
                  <img src="${request.image}" alt="Face" class="face-image">
                  <div class="face-details">
                      <p>
                          <span class="label">Detection Time:</span>
                          <span>${formatDate(request.timestamp)}</span>
                      </p>
                  </div>
                  ${isPending ? `
                  <div class="card-actions">
                      <button class="btn-success" onclick="approveUser('${request.face_id}')">Approve</button>
                      <button class="btn-danger" onclick="banUser('${request.face_id}')">Ban</button>
                  </div>
                  ` : ''}
              </div>
          </div>
      `;
  });
  
  container.innerHTML = html;
}

// Function to check for new requests
function checkForNewRequests() {
  fetch('/api/requests')
      .then(response => response.json())
      .then(data => {
          // Check if there are any new pending requests
          const newPendingRequests = data.filter(request => 
              request.status === 'Pending' && 
              new Date(request.timestamp) > new Date(lastRequestTime)
          );
          
          if (newPendingRequests.length > 0) {
              // Update last request time
              lastRequestTime = new Date().toISOString();
              
              // Update counters and containers
              document.getElementById('pending-count').textContent = 
                  data.filter(request => request.status === 'Pending').length;
              
              // Show notification for the newest request
              const latestRequest = newPendingRequests[0];
              showNotification(latestRequest);
              
              // Refresh the pending container if it's active
              if (document.getElementById('pending-section').classList.contains('active')) {
                  renderRequests(
                      data.filter(request => request.status === 'Pending'),
                      'pending-container',
                      'pending'
                  );
              }
          }
      })
      .catch(error => {
          console.error('Error checking for new requests:', error);
      });
}

// Function to show notification modal
function showNotification(request) {
  const modal = document.getElementById('notification-modal');
  const faceId = document.getElementById('modal-face-id');
  const timestamp = document.getElementById('modal-timestamp');
  const image = document.getElementById('modal-face-image');
  const approveBtn = document.getElementById('modal-approve');
  const banBtn = document.getElementById('modal-ban');
  
  // Set notification data
  faceId.textContent = request.face_id;
  timestamp.textContent = formatDate(request.timestamp);
  image.src = request.image;
  
  // Set button actions
  approveBtn.onclick = function() {
      approveUser(request.face_id);
      modal.style.display = 'none';
  };
  
  banBtn.onclick = function() {
      banUser(request.face_id);
      modal.style.display = 'none';
  };
  
  // Show modal
  modal.style.display = 'block';
  
  // Play notification sound
  const audio = new Audio('/static/audio/notification.mp3');
  audio.play().catch(() => {
      console.log('Auto-play was prevented. User interaction is required for audio.');
  });
}

// Function to approve a user
function approveUser(faceId) {
  fetch(`/api/approve/${faceId}`)
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              // Show success message
              alert(`User ${faceId} has been approved.`);
              
              // Refresh all request lists
              loadAllRequests();
          }
      })
      .catch(error => {
          console.error('Error approving user:', error);
          alert('Failed to approve user. Please try again.');
      });
}

// Function to ban a user
function banUser(faceId) {
  fetch(`/api/ban/${faceId}`)
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              // Show success message
              alert(`User ${faceId} has been banned.`);
              
              // Refresh all request lists
              loadAllRequests();
          }
      })
      .catch(error => {
          console.error('Error banning user:', error);
          alert('Failed to ban user. Please try again.');
      });
}

// Helper function to format date
function formatDate(dateString) {
  const options = { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
  };
  return new Date(dateString).toLocaleDateString(undefined, options);
}
