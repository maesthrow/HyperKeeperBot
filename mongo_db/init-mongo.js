db.createUser({
  user: 'maesthrow',
  pwd: '9125x$89',
  roles: [
    { role: 'userAdminAnyDatabase', db: 'admin' },  // Добавляет возможность администрирования пользователей
    { role: 'dbAdminAnyDatabase', db: 'admin' },
    { role: 'readWriteAnyDatabase', db: 'admin' },
    { role: 'readAnyDatabase', db: 'admin' }         // Позволяет читать любые базы данных
  ],
});