
const canvas = document.getElementById('canvas');

function renderComponent(component) {
    const element = document.createElement(component.type);
    element.innerHTML = component.content;
    canvas.appendChild(element);
}

// Example of how to receive UI updates from the orchestrator
// This should be replaced with a WebSocket connection
function getUiUpdates() {
    fetch('/derek', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: 'ui_update' })
    })
    .then(response => response.json())
    .then(data => {
        canvas.innerHTML = '';
        data.forEach(component => {
            renderComponent(component);
        });
    });
}

// Initial UI render
getUiUpdates();
