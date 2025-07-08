export function setupCreateEventModal(buttonSelector = '.btn-create-event') {
  // Create modal HTML if it doesn't exist
  if (!document.getElementById('createEventModal')) {
    const modalHtml = `
      <div class="modal fade" id="createEventModal" tabindex="-1" aria-labelledby="createEventModalLabel" aria-hidden="true">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="createEventModalLabel">Create Event</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <!-- Event form fields go here -->
              <form>
                <div class="mb-3">
                  <label for="eventName" class="form-label">Event Name</label>
                  <input type="text" class="form-control" id="eventName" placeholder="Enter event name">
                </div>
                <div class="mb-3">
                  <label for="eventDate" class="form-label">Date</label>
                  <input type="date" class="form-control" id="eventDate">
                </div>
                <div class="mb-3">
                  <label for="eventDescription" class="form-label">Description</label>
                  <textarea class="form-control" id="eventDescription" rows="3"></textarea>
                </div>
              </form>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
              <button type="button" class="btn btn-primary">Save Event</button>
            </div>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
  }

  // Attach click event to trigger button(s)
  document.querySelectorAll(buttonSelector).forEach(btn => {
    btn.addEventListener('click', () => {
      const modal = new bootstrap.Modal(document.getElementById('createEventModal'));
      modal.show();
    });
  });
} 