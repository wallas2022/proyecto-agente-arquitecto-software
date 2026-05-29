# 📘 Manual de API - MercaShop v1.0

## Autenticación

Todos los endpoints (excepto `/registro` y `/login`) requieren un token JWT en el header:

```
Authorization: Bearer <token>
```

---

## 🔐 Endpoints de Usuarios

### POST /api/usuarios/registro
Registra un nuevo usuario en el sistema.

**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "minimo8caracteres",
  "nombre": "Juan",
  "apellido": "Perez",
  "telefono": "+50212345678",
  "direccion": "Zona 10, Ciudad de Guatemala"
}
```

**Validaciones:**
- El email debe ser único en el sistema
- La contraseña debe tener al menos 8 caracteres
- El email debe contener '@'

**Respuesta 201:**
```json
{
  "id": 42,
  "email": "usuario@ejemplo.com",
  "mensaje": "Usuario registrado exitosamente"
}
```

### POST /api/usuarios/login
Autentica un usuario y devuelve un token.

**Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "minimo8caracteres"
}
```

**Respuesta 200:**
```json
{
  "token": "abc123...",
  "usuario_id": 42,
  "nombre": "Juan",
  "expira_en": "2026-05-30T10:00:00"
}
```

---

## 🛍️ Endpoints de Productos

### GET /api/productos/
Lista productos. Soporta filtros opcionales.

**Query Parameters:**
- `categoria` (string, opcional): Filtrar por categoría
- `activos` (bool, default true): Mostrar solo productos activos

### POST /api/productos/
Crea un nuevo producto (requiere rol admin).

**Validaciones:**
- El precio debe ser mayor a 0
- El stock no puede ser negativo
- El SKU debe ser único

### PUT /api/productos/{id}/stock
Actualiza el stock de un producto. La cantidad puede ser positiva (sumar) o negativa (restar).

---

## 📦 Endpoints de Pedidos

### POST /api/pedidos/
Crea un nuevo pedido completo.

**Body:**
```json
{
  "usuario_id": 42,
  "items": [
    {"producto_id": 1, "cantidad": 2},
    {"producto_id": 5, "cantidad": 1}
  ],
  "direccion_envio": "Zona 10, Ciudad de Guatemala"
}
```

**Flujo interno:**
1. Valida que el usuario exista
2. Valida que cada producto exista y tenga stock suficiente
3. Calcula subtotal, IVA (12%) y costo de envío
4. Descuenta stock de cada producto
5. Crea el pedido en estado 'pendiente'

**Respuesta 201:**
```json
{
  "pedido_id": 1001,
  "estado": "pendiente",
  "subtotal": 450.00,
  "impuestos": 54.00,
  "envio": 35.00,
  "total": 539.00
}
```

### PUT /api/pedidos/{id}/estado
Cambia el estado del pedido. Las transiciones permitidas son:

| Estado actual | Puede pasar a |
|---|---|
| pendiente | pagado, cancelado |
| pagado | enviado, cancelado |
| enviado | entregado |
| entregado | (final) |
| cancelado | (final) |

---

## 💳 Endpoints de Pagos

### POST /api/pagos/
Procesa el pago de un pedido pendiente.

**Body:**
```json
{
  "pedido_id": 1001,
  "metodo_pago": "tarjeta",
  "monto": 539.00
}
```

**Validaciones:**
- El pedido debe estar en estado 'pendiente'
- El monto debe coincidir exactamente con el total del pedido
- El método debe ser uno de: tarjeta, paypal, transferencia

### POST /api/pagos/{id}/reembolso
Solicita el reembolso de un pago completado.

**Restricciones:**
- Solo se pueden reembolsar pagos en estado 'completado'
- No se permiten reembolsos parciales
- El plazo máximo para solicitar reembolso es de 30 días

---

## 📊 Códigos de Estado HTTP

| Código | Significado |
|---|---|
| 200 | OK |
| 201 | Recurso creado |
| 400 | Datos inválidos |
| 401 | No autenticado |
| 403 | Sin permisos / usuario desactivado |
| 404 | Recurso no encontrado |
| 409 | Conflicto (ej. email duplicado) |
| 500 | Error interno del servidor |
