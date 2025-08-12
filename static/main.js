document.addEventListener('DOMContentLoaded', function() {
    // Sidebar navigation
    const sections = {
        'new-order-link': 'new-order-section',
        'orders-list-link': 'orders-list-section',
        'financial-link': 'financial-section'
    };
    
    Object.keys(sections).forEach(linkId => {
        document.getElementById(linkId).addEventListener('click', function(e) {
            e.preventDefault();
            
            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {
                section.style.display = 'none';
            });
            
            // Remove active class from all sidebar links
            document.querySelectorAll('.sidebar .list-group-item').forEach(link => {
                link.classList.remove('active');
            });
            
            // Show the selected section and mark link as active
            document.getElementById(sections[linkId]).style.display = 'block';
            this.classList.add('active');
            
            // Load data for specific sections
            if (linkId === 'orders-list-link') {
                loadOrders();
            } else if (linkId === 'financial-link') {
                loadCompletedOrders();
                initChart();
            }
        });
    });
    
    // Phone number management for new order form
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-phone')) {
            const phoneContainer = document.getElementById('phones-container');
            const newPhoneGroup = document.createElement('div');
            newPhoneGroup.className = 'input-group mb-2';
            newPhoneGroup.innerHTML = `
                <input type="text" class="form-control phone-input" required>
                <button class="btn btn-danger remove-phone" type="button">-</button>
            `;
            phoneContainer.appendChild(newPhoneGroup);
        } else if (e.target.classList.contains('remove-phone')) {
            e.target.parentElement.remove();
        }
    });
    
    // Add new order
    document.getElementById('new-order-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const phones = [];
        document.querySelectorAll('.phone-input').forEach(input => {
            if (input.value.trim()) {
                phones.push(input.value.trim());
            }
        });
        
        const orderData = {
            client_name: document.getElementById('client-name').value,
            device_model: document.getElementById('device-model').value,
            serial_number: document.getElementById('serial-number').value,
            device_condition: document.getElementById('device-condition').value,
            issue_description: document.getElementById('issue-description').value,
            repair_price: document.getElementById('repair-price').value,
            phones: phones
        };
        
        fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData),
        })
        .then(response => response.json())
        .then(data => {
            alert('Замовлення успішно створено!');
            this.reset();
            
            // Reset phone inputs
            const phoneContainer = document.getElementById('phones-container');
            phoneContainer.innerHTML = `
                <div class="input-group mb-2">
                    <input type="text" class="form-control phone-input" required>
                    <button class="btn btn-success add-phone" type="button">+</button>
                </div>
            `;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Помилка при створенні замовлення');
        });
    });
    
    // Load orders
    function loadOrders(filter = 'all') {
        fetch('/api/orders')
        .then(response => response.json())
        .then(orders => {
            const tableBody = document.getElementById('orders-table-body');
            tableBody.innerHTML = '';
            
            orders.forEach(order => {
                if (filter === 'active' && order.status) return;
                if (filter === 'completed' && !order.status) return;
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${order.id}</td>
                    <td>${order.client_name}</td>
                    <td>${order.device_model}</td>
                    <td>${order.received_date}</td>
                    <td>${order.final_price || order.repair_price} грн</td>
                    <td>${order.status ? 
                        '<span class="badge bg-success">Виконано</span>' : 
                        '<span class="badge bg-warning">В роботі</span>'}
                    </td>
                    <td>
                        <button class="btn btn-sm btn-info view-order" data-id="${order.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
            
            // Add event listeners to view buttons
            document.querySelectorAll('.view-order').forEach(button => {
                button.addEventListener('click', function() {
                    const orderId = this.getAttribute('data-id');
                    openOrderDetails(orderId, orders);
                });
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Помилка при завантаженні замовлень');
        });
    }
    
    // Apply filter for orders
    document.getElementById('apply-filter').addEventListener('click', function() {
        const filter = document.getElementById('status-filter').value;
        loadOrders(filter);
    });
    
    // Open order details modal
    function openOrderDetails(orderId, ordersData) {
        const order = ordersData.find(o => o.id === parseInt(orderId));
        
        document.getElementById('edit-order-id').value = order.id;
        document.getElementById('edit-client-name').value = order.client_name;
        document.getElementById('edit-device-model').value = order.device_model;
        document.getElementById('edit-serial-number').value = order.serial_number;
        document.getElementById('edit-device-condition').value = order.device_condition;
        document.getElementById('edit-issue-description').value = order.issue_description;
        document.getElementById('edit-repair-price').value = order.repair_price;
        document.getElementById('edit-final-price').value = order.final_price || '';
        document.getElementById('edit-received-date').value = order.received_date;
        document.getElementById('edit-completion-date').value = order.completion_date ? 
            order.completion_date.replace(' ', 'T') : '';
        document.getElementById('edit-status').checked = order.status;
        
        // Set phone numbers
        const phonesContainer = document.getElementById('edit-phones-container');
        phonesContainer.innerHTML = '';
        
        order.phones.forEach(phone => {
            const phoneGroup = document.createElement('div');
            phoneGroup.className = 'input-group mb-2';
            phoneGroup.innerHTML = `
                <input type="text" class="form-control edit-phone-input" value="${phone}" required>
                <button class="btn btn-danger remove-edit-phone" type="button">-</button>
            `;
            phonesContainer.appendChild(phoneGroup);
        });
        
        // If no phones, add an empty input
        if (order.phones.length === 0) {
            const phoneGroup = document.createElement('div');
            phoneGroup.className = 'input-group mb-2';
            phoneGroup.innerHTML = `
                <input type="text" class="form-control edit-phone-input" required>
                <button class="btn btn-danger remove-edit-phone" type="button">-</button>
            `;
            phonesContainer.appendChild(phoneGroup);
        }
        
        // Show the modal
        new bootstrap.Modal(document.getElementById('orderDetailsModal')).show();
    }
    
    // Add phone in edit form
    document.getElementById('add-edit-phone').addEventListener('click', function() {
        const phonesContainer = document.getElementById('edit-phones-container');
        const phoneGroup = document.createElement('div');
        phoneGroup.className = 'input-group mb-2';
        phoneGroup.innerHTML = `
            <input type="text" class="form-control edit-phone-input" required>
            <button class="btn btn-danger remove-edit-phone" type="button">-</button>
        `;
        phonesContainer.appendChild(phoneGroup);
    });
    
    // Remove phone in edit form
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('remove-edit-phone')) {
            e.target.parentElement.remove();
        }
    });
    
    // Save order changes
    document.getElementById('save-order-btn').addEventListener('click', function() {
        const orderId = document.getElementById('edit-order-id').value;
        
        const phones = [];
        document.querySelectorAll('.edit-phone-input').forEach(input => {
            if (input.value.trim()) {
                phones.push(input.value.trim());
            }
        });
        
        const completionDate = document.getElementById('edit-completion-date').value;
        
        const orderData = {
            client_name: document.getElementById('edit-client-name').value,
            device_model: document.getElementById('edit-device-model').value,
            serial_number: document.getElementById('edit-serial-number').value,
            device_condition: document.getElementById('edit-device-condition').value,
            issue_description: document.getElementById('edit-issue-description').value,
            repair_price: parseFloat(document.getElementById('edit-repair-price').value),
            final_price: document.getElementById('edit-final-price').value ? 
                parseFloat(document.getElementById('edit-final-price').value) : null,
            completion_date: completionDate ? 
                completionDate.replace('T', ' ') : null,
            status: document.getElementById('edit-status').checked,
            phones: phones
        };
        
        fetch(`/api/orders/${orderId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData),
        })
        .then(response => {
            if (response.ok) {
                bootstrap.Modal.getInstance(document.getElementById('orderDetailsModal')).hide();
                loadOrders(document.getElementById('status-filter').value);
                alert('Замовлення успішно оновлено!');
            } else {
                throw new Error('Failed to update order');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Помилка при оновленні замовлення');
        });
    });
    
    // Delete order button
    document.getElementById('delete-order-btn').addEventListener('click', function() {
        // Hide the details modal and show delete confirmation
        bootstrap.Modal.getInstance(document.getElementById('orderDetailsModal')).hide();
        new bootstrap.Modal(document.getElementById('deleteOrderModal')).show();
    });
    
    // Confirm delete order
    document.getElementById('confirm-delete-order').addEventListener('click', function() {
        const orderId = document.getElementById('edit-order-id').value;
        
        fetch(`/api/orders/${orderId}`, {
            method: 'DELETE',
        })
        .then(response => {
            if (response.ok) {
                bootstrap.Modal.getInstance(document.getElementById('deleteOrderModal')).hide();
                loadOrders(document.getElementById('status-filter').value);
                alert('Замовлення успішно видалено!');
            } else {
                throw new Error('Failed to delete order');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Помилка при видаленні замовлення');
        });
    });
    
    // Financial section - Calculate revenue
    document.getElementById('calculate-revenue').addEventListener('click', function() {
        initChart();
    });
    
    // Load completed orders for financial section
    function loadCompletedOrders() {
        fetch('/api/orders')
        .then(response => response.json())
        .then(orders => {
            const completedOrders = orders.filter(order => order.status && order.final_price);
            const tableBody = document.getElementById('completed-orders-body');
            tableBody.innerHTML = '';
            
            // Sort by completion date, most recent first
            completedOrders.sort((a, b) => {
                return new Date(b.completion_date) - new Date(a.completion_date);
            });
            
            // Take only the last 10 orders
            const recentOrders = completedOrders.slice(0, 10);
            
            recentOrders.forEach(order => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${order.id}</td>
                    <td>${order.client_name}</td>
                    <td>${order.device_model}</td>
                    <td>${order.received_date}</td>
                    <td>${order.completion_date || '-'}</td>
                    <td>${order.final_price || order.repair_price} грн</td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    // Initialize chart for financial section
    function initChart() {
        const ctx = document.getElementById('stats-chart').getContext('2d');
        const period = document.getElementById('revenue-period').value;
        
        // Очищаємо попередній графік, якщо він існує
        if (window.revenueChart) {
            window.revenueChart.destroy();
        }
        
        // Завантаження даних з сервера
        fetch(`/api/financial/?period=${period}`)
        .then(response => response.json())
        .then(data => {
            // Відображення загального доходу
            document.getElementById('revenue-amount').textContent = `${data.total_revenue} грн`;
            
            // Створення графіка
            window.revenueChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: data.datasets
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Помилка при завантаженні фінансових даних');
        });
    }
    
    // Додати виклик при зміні періоду
    document.getElementById('revenue-period').addEventListener('change', function() {
        initChart();
    });
    
    // Initialize the page with the first section
    document.getElementById('new-order-link').click();

    // Додавання обробника пошуку
    const searchButton = document.getElementById('search-btn');
    searchButton.addEventListener('click', function() {
        console.log('Натиснуто кнопку пошуку');
        searchOrders();
    });

    const searchInput = document.getElementById('search-orders');
    searchInput.addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            console.log('Натиснуто Enter у полі пошуку');
            searchOrders();
        }
    });

    // Функція пошуку
    function searchOrders() {
        const searchText = document.getElementById('search-orders').value.toLowerCase().trim();
        console.log('Пошук за текстом:', searchText);
        
        const rows = document.querySelectorAll('#orders-table-body tr');
        console.log('Знайдено рядків:', rows.length);
        
        rows.forEach(row => {
            let found = false;
            // Перевіряємо всі клітинки в рядку, крім останньої (кнопки)
            const cells = row.querySelectorAll('td:not(:last-child)');
            
            cells.forEach(cell => {
                if (cell.textContent.toLowerCase().includes(searchText)) {
                    found = true;
                }
            });
            
            if (found || searchText === '') {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    }
}); 