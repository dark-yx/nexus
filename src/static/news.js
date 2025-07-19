document.getElementById('load-news').addEventListener('click', function () {
    // Hacer una solicitud AJAX a la misma ruta /news
    fetch('/news', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest' // Identificar como solicitud AJAX
        }
    })
    .then(response => response.json())
    .then(data => {
        // Mostrar el resumen
        document.getElementById('summary').textContent = data.summary;

        // Mostrar los artículos
        const articlesList = document.getElementById('articles');
        articlesList.innerHTML = ''; // Limpiar contenido previo
        data.articles.forEach(article => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = article.url;
            link.textContent = article.title;
            link.target = '_blank'; // Abrir en nueva pestaña
            listItem.appendChild(link);
            articlesList.appendChild(listItem);
        });

        // Mostrar la sección de noticias
        document.getElementById('news-container').style.display = 'block';
    })
    .catch(error => {
        console.error('Error al cargar las noticias:', error);
    });
});
