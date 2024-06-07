// Обработчик сброса формы
document.getElementById('reset-btn').addEventListener('click', function() {
    // Получаем форму
    const form = document.getElementById('search-form');
    
    // Сбрасываем значения всех полей формы
    form.reset();
    
    // Запускаем поиск с пустыми параметрами
    searchMovies(new FormData(form));
});

// Функция для поиска фильмов
function searchMovies(formData) {
    const searchParams = new URLSearchParams(formData).toString();

    fetch(`/api/movies?${searchParams}`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('movies-container');
            container.innerHTML = '';
            data.forEach(movie => {
                const movieCard = `
                    <div class="col">
                        <div class="card h-100">
                            <img src="${movie.poster}" class="card-img-top" alt="${movie.title}">
                            <div class="card-body">
                                <h5 class="card-title">${movie.title}</h5>
                                <p class="card-text">${movie.description}</p>
                            </div>
                            <div class="card-footer">
                                <a href="/movies/${movie.id}" class="btn btn-primary">Подробнее</a>
                            </div>
                        </div>
                    </div>
                `;
                container.innerHTML += movieCard;
            });
        })
        .catch(error => console.error('Error:', error));
}

// Обработчик отправки формы
document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault();
    searchMovies(new FormData(event.target));
});

