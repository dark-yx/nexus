$(document).ready(function() {
    console.log("Document is ready");

    // Función para enviar mensaje al chatbot
    async function sendMessage() {
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message) {
            // Agregar mensaje del usuario al chat
            addMessage(message, 'user');
            input.value = '';
            
            try {
                // Obtener la ruta actual
                const currentPath = window.location.pathname;
                
                // Enviar mensaje al servidor con la ruta actual
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        current_path: currentPath
                    })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage(data.error, 'assistant');
                } else {
                    addMessage(data.response, 'assistant');
                }
            } catch (error) {
                addMessage('Error al enviar el mensaje: ' + error, 'assistant');
            }
        }
    }

    // Función para agregar mensaje al chat
    function addMessage(message, sender) {
        const listGroup = document.getElementById('list-group');
        const messageDiv = document.createElement('div');
        messageDiv.className = `list-group-item ${sender}-message`;
        
        // Crear contenedor para el mensaje
        const messageContainer = document.createElement('div');
        messageContainer.className = 'message-container';
        
        // Agregar avatar según el remitente
        const avatar = document.createElement('img');
        avatar.className = 'message-avatar';
        if (sender === 'user') {
            avatar.src = '/static/img/user-avatar.png';
            avatar.alt = 'User';
        } else {
            avatar.src = '/static/img/chatbot.png';
            avatar.alt = 'DEREK';
        }
        
        // Crear contenedor para el texto del mensaje
        const textContainer = document.createElement('div');
        textContainer.className = 'message-text';
        
        // Convertir el mensaje a HTML usando marked
        textContainer.innerHTML = marked.parse(message);
        
        // Agregar elementos al contenedor del mensaje
        messageContainer.appendChild(avatar);
        messageContainer.appendChild(textContainer);
        messageDiv.appendChild(messageContainer);
        
        // Agregar el mensaje al chat
        listGroup.appendChild(messageDiv);
        
        // Scroll al final del chat
        listGroup.scrollTop = listGroup.scrollHeight;
    }

    // Event listeners
    document.addEventListener('DOMContentLoaded', function() {
        const chatButton = document.getElementById('chat-button');
        const chatPopup = document.getElementById('chat-popup');
        const closeButton = document.getElementById('close-chat');
        const sendButton = document.getElementById('gpt-button');
        const chatInput = document.getElementById('chat-input');
        
        // Mostrar/ocultar chat
        chatButton.addEventListener('click', function() {
            chatPopup.style.display = chatPopup.style.display === 'none' ? 'flex' : 'none';
        });
        
        // Cerrar chat
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                chatPopup.style.display = 'none';
            });
        }
        
        // Enviar mensaje con botón
        sendButton.addEventListener('click', sendMessage);
        
        // Enviar mensaje con Enter
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Mensaje inicial del chatbot
        const welcomeMessage = "¡Hola! Soy DEREK, tu asistente de marketing digital. ¿En qué puedo ayudarte hoy?";
        addMessage(welcomeMessage, 'assistant');
    });

    function scrollToBottom() {
        var chatList = $("#list-group");
        chatList.scrollTop(chatList.prop("scrollHeight"));
    }

    // Event listener for the chatbot button
    $("#chat-button").click(function() {
        $("#chat-popup").toggle();
        scrollToBottom();
    });

    // Event listener for the send button inside the popup
    $("#gpt-button").click(function() {
        sendMessage();
    });

    // Add event listener for Enter key press inside the popup
    $("#chat-input").keypress(function(event) {
        if (event.which === 13) { // Enter key pressed
            event.preventDefault(); // Prevent default form submission
            sendMessage();
        }
    });

    // Hide the chat popup initially
    $("#chat-popup").hide();
});
