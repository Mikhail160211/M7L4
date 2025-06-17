import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()


def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

# Возможные варианты тестов:
def test_add_existing_user(setup_database, connection):
    """Тест добавления пользователя с уже существующим логином."""
    add_user('existinguser','none@example.com', 'password123')
    response = add_user('existinguser', 'none2@example.com', 'password456')
    assert not response,  "Пользователь с таким логином уже существует."

def test_authotnification_success(setup_database, connection):
    """Тест успешной аутентификации пользователя."""
    add_user('existinguser', 'none@example.com', 'password123')
    assert authenticate_user('existinguser', 'password123') == True

def test_authentication_nonexistent_user(setup_database, connection):
    """Тест аутентификации несуществующего пользователя."""
    assert authenticate_user('nonexistentuser', 'password123') == False

def test_authentication_wrong_password(setup_database, connection):
    """Тест аутентификации пользователя с неправильным паролем."""
    add_user('wronguser', 'none@example.com', 'password123')
    assert authenticate_user('wronguser', 'wrongpassword') == False

def test_display_users(setup_database, connection, capsys):
    """Тест отображения списка пользователей."""
    add_user('user1', 'none@example.com', 'password123')
    display_users()
    captured = capsys.readouterr() 
    assert 'user1' in captured.out, "Список пользователей должен содержать добавленного пользователя 'user1'."
    assert 'password123' not in captured.out, '.Пароль не должен отображаться в списке пользователей.'
