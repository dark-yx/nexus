// Variable global para controlar si ya se está cargando contenido
let isLoading = false;

// ===================== Configuración para Desktop vs Móvil =====================

// Este bloque se ejecuta cuando el DOM se ha cargado y configura el comportamiento del menú
document.addEventListener("DOMContentLoaded", function () {
  var navbarNav = document.getElementById("navbarNav");
  var navbarToggle = document.querySelector(".navbar-toggler");
  var mainContent = document.querySelector("main");

  function configureMenu() {
    if (window.innerWidth >= 1025) {
      // En desktop: menú abierto por defecto y manejo manual del toggle
      navbarNav.classList.add("show");
      mainContent.classList.add("menu-open");
      navbarToggle.setAttribute("aria-expanded", "true");
      // Quitamos los atributos de Bootstrap para evitar el manejo automático
      navbarToggle.removeAttribute("data-bs-toggle");
      navbarToggle.removeAttribute("data-bs-target");
    } else {
      // En móvil/tablet: se restaura el comportamiento de Bootstrap
      navbarNav.classList.remove("show");
      mainContent.classList.remove("menu-open");
      navbarToggle.setAttribute("aria-expanded", "false");
      navbarToggle.setAttribute("data-bs-toggle", "collapse");
      navbarToggle.setAttribute("data-bs-target", "#navbarNav");
    }
  }

  // Configuración inicial y actualización al redimensionar la ventana
  configureMenu();
  window.addEventListener("resize", configureMenu);

  // Manejo del clic en el toggle en desktop (en móvil se deja que Bootstrap lo haga)
  navbarToggle.addEventListener("click", function (e) {
    if (window.innerWidth >= 1025) {
      e.preventDefault(); // Evita el comportamiento por defecto
      if (navbarNav.classList.contains("show")) {
        navbarNav.classList.remove("show");
        mainContent.classList.remove("menu-open");
        navbarToggle.setAttribute("aria-expanded", "false");
      } else {
        navbarNav.classList.add("show");
        mainContent.classList.add("menu-open");
        navbarToggle.setAttribute("aria-expanded", "true");
      }
    }
  });
});

// ===================== Eventos de Bootstrap para el Collapse =====================

// Estos eventos se disparan solo en móvil/tablet, pues en desktop ya se gestiona manualmente
$(document).on('shown.bs.collapse', '#navbarNav', function () {
  if (window.innerWidth >= 1025) {
    $('main').addClass('menu-open');
  } else {
    $('.menu-overlay').css('display', 'block');
  }
});

$(document).on('hidden.bs.collapse', '#navbarNav', function () {
  if (window.innerWidth >= 1025) {
    $('main').removeClass('menu-open');
  } else {
    $('.menu-overlay').css('display', 'none');
  }
});

// ===================== Resto de Funcionalidades y Eventos =====================

$(document).ready(function () {

  // Función para ejecutar scripts insertados en contenido AJAX
  function executeScripts(scripts) {
    scripts.each(function () {
      $.globalEval(this.text || this.textContent || this.innerHTML || "");
    });
  }

  // Función loadContent actualizada con control de isLoading
  function loadContent(url, addToHistory = true) {
    // Si ya se está cargando contenido, salimos de la función
    if (isLoading) return;
    isLoading = true;

    $.ajax({
      url: url,
      type: "GET",
      success: function (response) {
        // Extraemos y actualizamos solo el contenido de <main>
        var newContent = $(response).find("main").html();
        $("main").html(newContent);
        // Ejecutamos cualquier script incluido en la respuesta
        executeScripts($(response).filter("script"));
        // Actualizamos el historial solo si es necesario
        if (addToHistory && window.location.href !== url) {
          window.history.pushState({ path: url }, "", url);
        }
        // Reinicializamos los eventos y funcionalidades comunes
        initializeEvents();
        initCommonFunctionality();
        // Permitir nuevas solicitudes tras un breve retardo (por ejemplo, 50ms)
        setTimeout(() => {
          isLoading = false;
        }, 50);
      },
      error: function (xhr) {
        console.error(xhr.responseText);
        // En caso de error, se restablece el flag para permitir reintentos
        isLoading = false;
      }
    });
  }

  function initializeEvents() {
    // Reinicializa eventos para enlaces y formularios
    $(".nav-link").off("click").on("click", function (e) {
      e.preventDefault();
      var url = $(this).attr("href");
      if (!isLoading) {
        loadContent(url);
      }
    });

    $("#business-idea-form").on("submit", function (event) {
      event.preventDefault();
      const generateIdeasButton = document.getElementById("generate-ideas-button");
      generateIdeasButton.disabled = true;
      const formData = new FormData(this);
      fetch("/ideas-de-negocios", {
        method: "POST",
        body: formData,
      })
        .then(response => response.text())
        .then(data => {
          document.open();
          document.write(data);
          document.close();
        })
        .catch(error => console.error("Error:", error));
    });

    handleFormSubmission(
      "scrap1",
      "/analisis-web",
      "POST",
      function (response) {
        document.getElementById("analisis-result").innerHTML = response;
      },
      function (error) {
        console.error(error);
      }
    );

    handleFormSubmission(
      "funnel-form",
      "/funnel",
      "POST",
      function (response) {
        document.getElementById("embudo-container").innerHTML = response;
      },
      function (error) {
        console.error(error);
      }
    );

    handleFormSubmission(
      "calculadora-form",
      "/calculadora",
      "POST",
      function (response) {
        document.getElementById("resultado-calculadora").innerHTML = response;
      },
      function (error) {
        console.error(error);
      }
    );

    handleFormSubmission(
      "kwres1",
      "/keyword_research",
      "POST",
      function (response) {
        document.getElementById("keyword-research-result").innerHTML = response;
      },
      function (error) {
        console.error(error);
      }
    );

    // Llamadas a funciones para manejar el menú y el overlay
    // (Los eventos 'shown.bs.collapse' y 'hidden.bs.collapse' ya están registrados arriba)
    handleMobileMenuLinks();
    handleOutsideMenuClick();
    handleOverlayClick();
  }

  $(window).on("popstate", function (e) {
    if (e.originalEvent.state !== null) {
      var url = window.location.href;
      loadContent(url);
    }
  });

  initializeEvents();
  initCommonFunctionality();
});

function handleMobileMenuLinks() {
  var mobileMenuLinks = document.querySelectorAll(".navbar-nav a");
  var navbarToggle = document.querySelector(".navbar-toggler");
  var navbarNav = document.querySelector(".navbar-collapse");

  mobileMenuLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.innerWidth < 1025 && $(navbarNav).hasClass("show")) {
        $(navbarNav).collapse("hide");
        navbarToggle.setAttribute("aria-expanded", "false");
      }
    });
  });
}

function handleOutsideMenuClick() {
  document.addEventListener("click", function (event) {
    var navbarNav = document.querySelector(".navbar-collapse");
    var navbarToggle = document.querySelector(".navbar-toggler");

    // Solo cerrar en móvil si se hace clic fuera del menú y el botón toggle
    if (window.innerWidth < 1025 && $(navbarNav).hasClass("show") &&
        !event.target.closest(".navbar-collapse") &&
        !event.target.closest(".navbar-toggler")) {
      $(navbarNav).collapse("hide");
      navbarToggle.setAttribute("aria-expanded", "false");
    }
  });
}

function handleOverlayClick() {
  var overlay = document.querySelector(".menu-overlay");
  var navbarNav = document.querySelector(".navbar-collapse");
  var mainContent = document.querySelector("main");

  if (overlay) {
    overlay.addEventListener("click", function () {
      if (window.innerWidth < 1025) { // Solo en móvil
        $(navbarNav).collapse("hide");
        overlay.style.display = "none";
        if (mainContent.classList.contains("menu-open")) {
          mainContent.classList.remove("menu-open");
        }
        var navbarToggle = document.querySelector(".navbar-toggler");
        if (navbarToggle) {
          navbarToggle.setAttribute("aria-expanded", "false");
        }
      }
    });
  }
}

function handleFormSubmission(formId, url, method, successCallback, errorCallback) {
  var form = document.getElementById(formId);
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var formData = new FormData(form);
      var jsonData = {};
      formData.forEach(function (value, key) {
        jsonData[key] = value;
      });
      sendAjaxRequest(url, method, jsonData, function (error, response) {
        if (error) {
          errorCallback(error);
        } else {
          successCallback(response);
        }
      });
    });
  }
}

function initCommonFunctionality() {
  // Reinicia comportamientos comunes
  handleMobileMenuLinks();
  handleOutsideMenuClick();
  window.onscroll = function () {
    scrollFunction();
  };
  function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
      document.getElementById("scrollToTopBtn").style.display = "block";
    } else {
      document.getElementById("scrollToTopBtn").style.display = "none";
    }
  }
  document.getElementById("scrollToTopBtn").addEventListener("click", function () {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
  });
}

// ===================== Tema Dark/Light con Feather Icons =====================

function toggleTheme() {
  const body = document.body;
  const themeIcon = document.getElementById("theme-icon");
  body.classList.toggle("light-mode");
  if (body.classList.contains("light-mode")) {
    themeIcon.setAttribute("data-feather", "moon");
  } else {
    themeIcon.setAttribute("data-feather", "sun");
  }
  feather.replace();
  localStorage.setItem("theme", body.classList.contains("light-mode") ? "light" : "dark");
}

// Al cargar la página, restablece la preferencia del tema
document.addEventListener("DOMContentLoaded", function () {
  const themeIcon = document.getElementById("theme-icon");
  if (localStorage.getItem("theme") === "light") {
    document.body.classList.add("light-mode");
    themeIcon.setAttribute("data-feather", "moon");
  } else {
    themeIcon.setAttribute("data-feather", "sun");
  }
  feather.replace();
});


