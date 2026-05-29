# 🛒 MercaShop - Sistema de Tienda Online

MercaShop es una plataforma de comercio electrónico que permite la gestión completa de productos, usuarios, pedidos y pagos para una tienda online de tamaño medio.

## 📋 Descripción General

El sistema está compuesto por una **API REST** desarrollada en Python con FastAPI, conectada a una base de datos **PostgreSQL** y un cache **Redis** para sesiones. El frontend es una aplicación **React** que consume la API. Las pasarelas externas integradas son **Stripe** (procesamiento de pagos) y **SendGrid** (notificaciones por correo).

## 🎯 Funcionalidades Principales

### Para Usuarios
- Registro y autenticación con email + contraseña
- Catálogo de productos con filtros por categoría
- Carrito de compras
- Procesamiento de pagos seguro
- Historial de pedidos
- Notificaciones por email

### Para Administradores
- Gestión de productos (CRUD)
- Control de inventario y stock
- Visualización de pedidos y estados
- Procesamiento de reembolsos
- Reportes de ventas

## 🏗️ Arquitectura

El sistema sigue una arquitectura de **3 capas**:

1. **Capa de Presentación:** Frontend React
2. **Capa de Aplicación:** API FastAPI con routers especializados
3. **Capa de Datos:** PostgreSQL + Redis

Ver el diagrama completo en `diagramas/arquitectura_mercashop.drawio`.

## 📚 Módulos del Sistema

| Módulo | Responsabilidad |
|---|---|
| `productos` | Catálogo, inventario, categorías |
| `usuarios` | Registro, autenticación, perfiles |
| `pedidos` | Creación de pedidos, cálculo de totales, máquina de estados |
| `pagos` | Integración con Stripe, reembolsos |

## 💰 Reglas de Negocio Clave

- **IVA:** 12% aplicado a todos los pedidos (Guatemala)
- **Envío gratuito:** pedidos superiores a Q500.00
- **Costo de envío estándar:** Q35.00
- **Estados de pedido:** pendiente → pagado → enviado → entregado
- **Métodos de pago aceptados:** tarjeta, PayPal, transferencia bancaria

## 🚀 Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/empresa/mercashop-api.git
cd mercashop-api

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con las credenciales reales

# 5. Iniciar la base de datos con Docker
docker-compose up -d postgres redis

# 6. Ejecutar la API
uvicorn app.main:app --reload
```

La API estará disponible en `http://localhost:8000` y la documentación Swagger en `http://localhost:8000/docs`.

## 🧪 Pruebas

```bash
pytest tests/
```

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades, contactar al equipo de desarrollo.

## 📄 Licencia

Software propietario - MercaShop S.A. de C.V., 2026.
