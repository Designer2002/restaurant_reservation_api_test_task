// ========== Управление модальными окнами ==========
function setupModal(modalId, openButtonClass, closeButtonClass) {
    const modal = document.getElementById(modalId);
    const openBtn = document.querySelector(openButtonClass);
    const closeBtn = document.querySelector(".close");

    openBtn?.addEventListener('click', () => {
        modal.style.display = 'block';
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
    }

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Инициализация модальных окон
setupModal('addTableModal', '.create-table', '.close');
setupModal('deleteTableModal', '.delete-table', '.close');
setupModal('addReservationModal', '.create-reservation', '.close');
setupModal('deleteReservationModal', '.delete-reservation', '.close');

function showTables() {
    document.getElementById('tablesContainer').style.display = 'block';
    document.getElementById('reservationsContainer').style.display = 'none';
    //updateTablesTable(); // Загружаем данные при первом показе
}

function showReservations() {
    document.getElementById('reservationsContainer').style.display = 'block';
    document.getElementById('tablesContainer').style.display = 'none';
    //updateReservationsTable(); // Загружаем данные при первом показе
}

async function updateTablesTable() {
    const tables = await fetchTables();
    const tbody = document.querySelector('table.container tbody');
    tbody.innerHTML = tables.map(table => `
        <tr>
            <td>${table.id}</td>
            <td>${table.name}</td>
            <td>${table.capacity}</td>
            <td>${table.location}</td>
        </tr>
    `).join('');
}

// Функция для обновления таблицы бронирований
async function updateReservationsTable() {
    try {
        // Получаем данные бронирований с сервера
        const reservations = await fetchReservations();
        const tbody = document.querySelector('table.reservations tbody');
        
        if (!tbody) {
            console.error('Не найдена таблица бронирований в DOM');
            return;
        }

        // Форматируем данные для отображения
        tbody.innerHTML = reservations.map(reservation => {
            // Форматируем дату для красивого отображения
            const resDate = new Date(reservation.reservation_time);
            const formattedDate = resDate.toLocaleString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            return `
                <tr>
                    <td>${reservation.id}</td>
                    <td>${reservation.table_id}</td>
                    <td>${reservation.customer_name}</td>
                    <td>${formattedDate}</td>
                    <td>${reservation.guests_count}</td>
                    <td>
                        <button class="cancel-btn" data-id="${reservation.id}">Отменить</button>
                    </td>
                </tr>
            `;
        }).join('');

        // Добавляем обработчики для кнопок отмены
        document.querySelectorAll('.cancel-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const reservationId = e.target.getAttribute('data-id');
                if (confirm('Вы уверены, что хотите отменить эту бронь?')) {
                    await deleteReservation(reservationId);
                    await updateReservationsTable();
                    await updateTablesTable(); // Обновляем таблицу столиков на случай изменения статуса
                }
            });
        });

    } catch (error) {
        console.error('Ошибка при обновлении таблицы бронирований:', error);
        alert('Не удалось загрузить данные бронирований');
    }
}


// Получение всех столиков
async function fetchTables() {
    showTables()
    try {
        const response = await fetch(`${API_URL}/tables`);
        if (!response.ok) throw new Error('Ошибка сети');
        return await response.json();
    } catch (error) {
        console.error('Ошибка:', error);
        return [];
    }
}

// Получение всех броней
async function fetchReservations() {
    showReservations()
    try {
        const response = await fetch(`${API_URL}/reservations`);
        if (!response.ok) throw new Error('Ошибка сети');
        return await response.json();
    } catch (error) {
        console.error('Ошибка:', error);
        return [];
    }
}

// ========== Обновленные функции для работы с API ==========
async function populateTablesDropdown() {
    const tables = await fetchTables();
    const dropdown = document.getElementById('tableToDelete');
    const reservationDropdown = document.getElementById('reservationTable');
    
    dropdown.innerHTML = '<option value="">-- Выберите столик --</option>';
    reservationDropdown.innerHTML = '<option value="">-- Выберите столик --</option>';
    
    tables.forEach(table => {
        const option = document.createElement('option');
        option.value = table.id;
        option.textContent = `${table.name} (${table.location}, ${table.capacity} мест)`;
        dropdown.appendChild(option.cloneNode(true));
        reservationDropdown.appendChild(option);
    });
}

async function populateReservationsDropdown() {
    const reservations = await fetchReservations();
    const dropdown = document.getElementById('reservationToDelete');
    
    dropdown.innerHTML = '<option value="">-- Выберите бронь --</option>';
    
    reservations.forEach(res => {
        const option = document.createElement('option');
        option.value = res.id;
        
        // Форматируем дату для удобства чтения
        const resDate = new Date(res.reservation_time);
        const formattedDate = resDate.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        option.textContent = `Бронь #${res.id} - ${res.customer_name} (${formattedDate})`;
        dropdown.appendChild(option);
    });
}

// Обработчики форм
document.getElementById('addTableForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const modal = document.getElementById('addTableModal');
    
    const tableData = {
        name: document.getElementById('tableName').value,
        capacity: parseInt(document.getElementById('tableCapacity').value),
        location: document.getElementById('tableLocation').value
    };
    
    try {
        await createTable(tableData);
        modal.style.display = 'none';
        updateTablesTable();
        populateTablesDropdown();
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
    // После успешного создания брони:
    document.getElementById('addTableForm').reset();
});

// Создание столика
async function createTable(tableData) {
    const response = await fetch(`${API_URL}/tables`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(tableData)
    });
    return await response.json();
}

// Удаление столика
async function deleteTable(id) {
    const response = await fetch(`${API_URL}/tables/${id}`, {
        method: 'DELETE'
    });
    return await response.json();
}
async function createReservation() {
    const tableId = prompt('Введите ID столика:');
    if (!tableId) return;
    
    const customerName = prompt('Введите имя клиента:');
    const reservationTime = prompt('Введите время брони (ГГГГ-ММ-ДД ЧЧ:ММ):');
    const guestsCount = prompt('Введите количество гостей:');
    
    try {
        const response = await fetch(`${API_URL}/reservations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                table_id: parseInt(tableId),
                customer_name: customerName,
                reservation_time: reservationTime,
                guests_count: parseInt(guestsCount)
            })
        });
        
        if (!response.ok) throw new Error('Ошибка при создании брони');
        updateReservationsTable();
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
}

async function deleteReservation() {
    const reservationId = prompt('Введите ID брони для удаления:');
    if (!reservationId) return;
    
    try {
        const response = await fetch(`${API_URL}/reservations/${reservationId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Ошибка при удалении');
        updateReservationsTable();
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
}

document.getElementById('deleteTableForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const modal = document.getElementById('deleteTableModal');
    const tableId = document.getElementById('tableToDelete').value;
    
    try {
        await deleteTable(tableId);
        modal.style.display = 'none';
        updateTablesTable();
        populateTablesDropdown();
        updateReservationsTable();
        populateReservationsDropdown();
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
});

// Обработчик формы добавления брони
document.getElementById('addReservationForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const modal = document.getElementById('addReservationModal');
    
    const reservationData = {
        table_id: parseInt(document.getElementById('reservationTable').value),
        customer_name: document.getElementById('customerName').value,
        reservation_time: document.getElementById('reservationTime').value,
        guests_count: parseInt(document.getElementById('guestsCount').value)
    };
    
    // Валидация
    if (!reservationData.table_id || !reservationData.customer_name || 
        !reservationData.reservation_time || !reservationData.guests_count) {
        alert('Пожалуйста, заполните все поля');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/reservations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(reservationData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при создании брони');
        }
        
        modal.style.display = 'none';
        document.getElementById('addReservationForm').reset();
        updateReservationsTable();
        populateReservationsDropdown();
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
    // После успешного создания брони:
    document.getElementById('addReservationForm').reset();
});

// Обработчик формы удаления брони
document.getElementById('deleteReservationForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const modal = document.getElementById('deleteReservationModal');
    const reservationId = document.getElementById('reservationToDelete').value;
    
    if (!reservationId) {
        alert('Пожалуйста, выберите бронь для удаления');
        return;
    }
    
    if (!confirm('Вы уверены, что хотите отменить эту бронь?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/reservations/${reservationId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка при удалении брони');
        }
        
        modal.style.display = 'none';
        updateReservationsTable();
        populateReservationsDropdown();
        
        // Обновим список столиков на случай, если статус столика изменился
        updateTablesTable();
        populateTablesDropdown();
    } catch (error) {
        alert(`Ошибка: ${error.message}`);
    }
});


// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    updateTablesTable();
    updateReservationsTable();
    populateTablesDropdown();
    populateReservationsDropdown();
    
    // Обработчики для кнопок
    document.querySelector('.fetch-tables')?.addEventListener('click', updateTablesTable);
    document.querySelector('.fetch-reservations')?.addEventListener('click', updateReservationsTable);
});

const API_URL="127.0.0.1:8000"
document.getElementById('reservationsContainer').style.display = 'none';
document.getElementById('tablesContainer').style.display = 'none';
console.log("SCRIPT LOADED")