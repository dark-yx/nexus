document.addEventListener('DOMContentLoaded', function() {
    const nextButtons = document.querySelectorAll('.next-button');
    const form = document.getElementById('business-idea-form');
    const inputSteps = document.querySelectorAll('.input-step');
    const loadingMessage = document.getElementById('loading-message');
    let currentStep = 1;

    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (currentStep < inputSteps.length) {
                if (validateStep(currentStep)) {
                    inputSteps[currentStep - 1].style.display = 'none';
                    inputSteps[currentStep].style.display = 'block';
                    currentStep++;
                }
            }
        });
    });

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const generateIdeasButton = document.getElementById('generate-ideas-button');
        generateIdeasButton.disabled = true;
        form.style.display = 'none';
        loadingMessage.style.display = 'block'; // Mostrar mensaje de carga al enviar el formulario
        form.submit(); // Enviar el formulario
    });

    function validateStep(step) {
        let isValid = true;
        const stepInputs = inputSteps[step - 1].querySelectorAll('input');
        stepInputs.forEach(input => {
            if (!input.checkValidity()) {
                const errorMessage = input.parentElement.querySelector('.error-message');
                if (errorMessage) {
                    errorMessage.style.display = 'block';
                }
                isValid = false;
            } else {
                const errorMessage = input.parentElement.querySelector('.error-message');
                if (errorMessage) {
                    errorMessage.style.display = 'none';
                }
            }
        });
        return isValid;
    }
});
