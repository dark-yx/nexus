document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.querySelector('.input-container-chat'); // Selecciona el formulario por su clase
    const chatInput = chatForm.querySelector('#user-input'); // Selecciona el campo de entrada por su ID
    const chatMessagesContainer = document.getElementById('chat-messages-container');
    const sendBtn = chatForm.querySelector('.send-btn'); // Selecciona el botón de enviar

    // Limpiar el historial de mensajes al cargar la página
    chatMessagesContainer.innerHTML = '';

    // Agregar el mensaje predeterminado del asistente
    const defaultAssistantMessage = document.createElement('div');
    defaultAssistantMessage.classList.add('message', 'assistant-message');
    defaultAssistantMessage.textContent = "Hola, soy WLT 1.0 y estoy aquí para responder tus consultas sobre Marketing Digital. ¿En qué puedo ayudarte hoy?";
    chatMessagesContainer.appendChild(defaultAssistantMessage);

    sendBtn.addEventListener('click', function(event) {
        event.preventDefault(); // Detener el comportamiento predeterminado del formulario

        const userInput = chatInput.value.trim();

        if (userInput) {
            // Crear un nuevo elemento de mensaje de usuario
            const userMessage = document.createElement('div');
            userMessage.classList.add('message', 'user-message');
            userMessage.textContent = userInput;
            chatMessagesContainer.appendChild(userMessage);

            // Crear un nuevo elemento para la animación de puntos suspensivos
            const typingDotsElement = document.createElement('div');
            typingDotsElement.classList.add('typing-dots');
            typingDotsElement.textContent = '....';
            chatMessagesContainer.appendChild(typingDotsElement);

            // Enviar una solicitud AJAX al servidor
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `user_input=${encodeURIComponent(userInput)}`
            })
            .then(response => response.json()) // Parsear la respuesta como JSON
            .then(data => {
                // Eliminar el mensaje de puntos suspensivos
                typingDotsElement.remove();

                // Crear un nuevo elemento de mensaje del asistente
                const assistantMessage = document.createElement('div');
                assistantMessage.classList.add('message', 'assistant-message');

                // Verificar si el mensaje del asistente requiere formato Markdown
                if (data.markdownNeeded) {
                    // Si se necesita Markdown, utilizarlo
                    assistantMessage.innerHTML = `<pre><code>${data.response}</code></pre>`;
                } else {
                    // Si no se necesita Markdown, utilizar HTML
                    assistantMessage.innerHTML = data.response;
                }

                chatMessagesContainer.appendChild(assistantMessage);

                // Desplazarse al final del contenedor de mensajes para mantener la vista en la última interacción
                chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
            })
            .catch(error => {
                console.error('Error al obtener la respuesta del asistente:', error);
            });

            // Limpiar el campo de entrada
            chatInput.value = '';
        }
    });

    // Invertir el orden de los mensajes si es necesario al cargar la página
    if (chatMessagesContainer.children.length > 0) {
        const messages = Array.from(chatMessagesContainer.children);
        messages.reverse().forEach(message => chatMessagesContainer.appendChild(message));
    }
});
