$(document).ready(function () {
    // Función para la navegación AJAX en los enlaces de la barra de navegación y barra lateral
    $('.nav-link').on('click', function (e) {
        e.preventDefault();
        var url = $(this).attr('href');
        $.ajax({
            url: url,
            type: 'GET',
            success: function (response) {
                var newContent = $(response).find('main').html();
                $('main').html(newContent);
                // Ejecutar scripts después de cargar el nuevo contenido
                executeScripts($(response).filter('script'));
                window.history.pushState({ path: url }, '', url);
            },
            error: function (xhr) {
                console.log(xhr.responseText);
            }
        });
    });

    // Manejar los eventos de navegación del historial
    $(window).on('popstate', function (e) {
        if (e.originalEvent.state !== null) {
            var url = window.location.href;
            $.ajax({
                url: url,
                type: 'GET',
                success: function (response) {
                    var newContent = $(response).find('main').html();
                    $('main').html(newContent);
                    // Ejecutar scripts después de cargar el nuevo contenido
                    executeScripts($(response).filter('script'));
                },
                error: function (xhr) {
                    console.log(xhr.responseText);
                }
            });
        }
    });

    // Función para ejecutar scripts después de cargar el contenido
    function executeScripts(scripts) {
        scripts.each(function () {
            $.globalEval(this.text || this.textContent || this.innerHTML || '');
        });
    }

    // Combina el script anterior con el siguiente

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

            inputSteps[currentStep - 1].style.display = 'none';
            loadingMessage.style.display = 'block';

            const formData = new FormData(form);
            fetch('/ideas-de-negocios', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.text())
            .then(data => {
                document.open();
                document.write(data);
                document.close();
            })
            .catch(error => console.error('Error:', error));
        });

        function validateStep(step) {
            let isValid = true;

            switch(step) {
                case 1:
                    const skillsInput = document.getElementById('skills');
                    const skillsError = document.getElementById('skills-error');
                    if (skillsInput.value.trim() === '') {
                        skillsError.style.display = 'block';
                        isValid = false;
                    } else {
                        skillsError.style.display = 'none';
                    }
                    break;
                case 2:
                    const interestsInput = document.getElementById('interests');
                    const interestsError = document.getElementById('interests-error');
                    if (interestsInput.value.trim() === '') {
                        interestsError.style.display = 'block';
                        isValid = false;
                    } else {
                        interestsError.style.display = 'none';
                    }
                    break;
                case 3:
                    const capitalInput = document.getElementById('capital');
                    const capitalError = document.getElementById('capital-error');
                    const capitalValue = capitalInput.value;
                    const capitalPattern = /^[0-9]+(\.[0-9]{1,2})?$/;
                    
                    if (!capitalPattern.test(capitalValue) || capitalValue.trim() === '') {
                        capitalError.style.display = 'block';
                        isValid = false;
                    } else {
                        capitalError.style.display = 'none';
                    }
                    break;
                case 4:
                    const economicScenarioInput = document.getElementById('economic_scenario');
                    const economicScenarioError = document.getElementById('economic_scenario-error');
                    if (economicScenarioInput.value.trim() === '') {
                        economicScenarioError.style.display = 'block';
                        isValid = false;
                    } else {
                        economicScenarioError.style.display = 'none';
                    }
                    break;
                case 5:
                    const dedicationInput = document.getElementById('dedication');
                    const dedicationError = document.getElementById('dedication-error');
                    if (dedicationInput.value.trim() === '') {
                        dedicationError.style.display = 'block';
                        isValid = false;
                    } else {
                        dedicationError.style.display = 'none';
                    }
                    break;
            }

            return isValid;
        }

        var summaryContent = document.getElementById('summary-content');
        if (summaryContent) {
            summaryContent.innerHTML = marked.parse(summaryContent.textContent);
        }
    });
});