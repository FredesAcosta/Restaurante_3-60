import bcrypt
print(bcrypt.hashpw('Admin123*'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
print(bcrypt.hashpw('Empleado123*'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))
