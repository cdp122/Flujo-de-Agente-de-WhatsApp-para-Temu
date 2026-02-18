# Documentación Completa del Proyecto: Agente de IA WhatsApp para Temu

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Arquitectura General](#2-arquitectura-general)
3. [Componentes Principales](#3-componentes-principales)
4. [Evolución del Proyecto (V1, V2, V3)](#4-evolución-del-proyecto)
5. [Instalación y Configuración](#5-instalación-y-configuración)
6. [Base de Datos y Almacenamiento](#6-base-de-datos-y-almacenamiento)
7. [Flujo de Trabajo Detallado](#7-flujo-de-trabajo-detallado)
8. [Características Avanzadas](#8-características-avanzadas)
9. [Problemas Conocidos y Soluciones](#9-problemas-conocidos-y-soluciones)
10. [Mejores Prácticas](#10-mejores-prácticas)
11. [Guía de Uso](#11-guía-de-uso)
12. [Referencias y Recursos](#12-referencias-y-recursos)

---

## 1. Introducción

### 1.1 Propósito del Proyecto

Este proyecto implementa un **Agente de IA avanzado** para WhatsApp diseñado específicamente para facilitar el proceso de importación y venta de productos desde **Temu**. El asistente virtual, llamado **Estella**, automatiza:

- **Cotizaciones en tiempo real** de productos
- **Análisis de imágenes** para extraer precios y características
- **Gestión de carritos de compra** persistentes
- **Conversaciones contextuales** con memoria a largo plazo
- **Cálculo automático de impuestos** y costos de importación

### 1.2 Características Principales

- 🤖 **Inteligencia Artificial**: Integración con Ollama (modelos locales) para procesamiento de lenguaje natural e imágenes
- 💬 **Dual API Support**: Compatible con Evolution API (no oficial) y WhatsApp Business API (Meta oficial)
- 🧠 **Memoria Conversacional**: Redis para gestión de sesiones y contexto histórico
- 🛒 **Gestión de Carrito**: Sistema completo de seguimiento de productos y cálculos
- 📊 **Perfiles de Cliente**: Base de datos PostgreSQL para almacenar preferencias y comportamiento
- 🔐 **Sistema de Whitelist**: Control de acceso para testing y producción
- 📸 **Análisis de Imágenes**: OCR y visión por computadora para extraer precios de capturas

### 1.3 Stack Tecnológico

| Tecnología | Propósito | Versión |
|------------|-----------|---------|
| **n8n** | Orquestación de flujos de trabajo | Latest (Local) |
| **Evolution API** | Interfaz no oficial de WhatsApp | 2.3.7 |
| **WhatsApp Business API** | API oficial de Meta | Official |
| **PostgreSQL** | Base de datos principal | 15 |
| **Redis** | Cache y memoria conversacional | 7-alpine |
| **Ollama** | Motor de IA local | Latest |
| **Browserless** | Scraping y extracción de imágenes | Latest Chromium |
| **Docker** | Containerización de servicios | - |

---

## 2. Arquitectura General

### 2.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO WHATSAPP                          │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼──────┐
    │Evolution │          │  WhatsApp  │
    │   API    │          │Business API│
    │ (v2.3.7) │          │  (Oficial) │
    └────┬─────┘          └─────┬──────┘
         │                      │
         └───────────┬──────────┘
                     │
              ┌──────▼──────┐
              │   WEBHOOK   │
              │   n8n       │
              └──────┬──────┘
                     │
         ┌───────────┴────────────┐
         │                        │
    ┌────▼────────┐      ┌────────▼─────┐
    │ DataCleaning│      │  Whitelist   │
    │   & Routing │      │   Control    │
    └────┬────────┘      └──────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │         PROCESAMIENTO REDIS            │
    │  • Guardar mensajes temporales        │
    │  • Gestión de IDs de mensajes         │
    │  • Espera de mensajes agrupados       │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │      CONSULTA BASE DE DATOS            │
    │  • PostgreSQL: Perfil de cliente      │
    │  • Historial de compras               │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │     PROCESAMIENTO DE CONTENIDO         │
    │  ┌──────────┐      ┌───────────┐      │
    │  │  Texto   │      │  Imagen   │      │
    │  │ Normal   │      │   URL     │      │
    │  └────┬─────┘      └─────┬─────┘      │
    │       │                  │            │
    │       │      ┌───────────▼────────┐   │
    │       │      │   Browserless/     │   │
    │       │      │   HTTP Download    │   │
    │       │      └───────────┬────────┘   │
    │       │                  │            │
    │       │      ┌───────────▼────────┐   │
    │       │      │  Ollama Vision     │   │
    │       │      │  (llama3.2-vision) │   │
    │       │      └───────────┬────────┘   │
    │       │                  │            │
    └───────┴──────────────────┴────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │      GESTIÓN DE CARRITO (REDIS)        │
    │  • Cálculo de subtotales              │
    │  • Impuestos (15%)                    │
    │  • Total acumulado                    │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │     SELECTOR DE PROMPT DINÁMICO        │
    │  • Cotización exitosa                 │
    │  • Checkout (finalizar compra)        │
    │  • Solicitud de captura               │
    │  • Conversación general               │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │      IA CONTESTADORA (OLLAMA)          │
    │  • Modelo: llama3.1 (8b)              │
    │  • Memoria conversacional (Redis)     │
    │  • Prompt system: "Estella"           │
    └────┬──────────────────────────────────┘
         │
    ┌────▼──────────────────────────────────┐
    │       REDIRECCIÓN DE RESPUESTA         │
    │  ┌──────────┐  ┌──────────┐           │
    │  │Evolution │  │  Oficial │           │
    │  └────┬─────┘  └────┬─────┘           │
    └───────┼─────────────┼─────────────────┘
            │             │
            └──────┬──────┘
                   │
    ┌──────────────▼──────────────────────┐
    │    ENVÍO DE MENSAJE FINAL           │
    │  • Estado "disponible"              │
    │  • Marcar como leído                │
    │  • Estado "escribiendo" (delay)     │
    │  • Enviar texto                     │
    │  • Estado "no disponible"           │
    └──────────────┬──────────────────────┘
                   │
    ┌──────────────▼──────────────────────┐
    │  ESPERA Y FINALIZACIÓN              │
    │  • Wait 60s (producción)            │
    │  • Verificar nuevos mensajes        │
    │  • Si no hay → Resumir conversación│
    │  • Guardar perfil en PostgreSQL    │
    └─────────────────────────────────────┘
```

### 2.2 Flujo de Datos

1. **Recepción**: Webhook recibe mensaje desde Evolution API o Meta API
2. **Limpieza**: `DataCleaning` extrae y normaliza datos
3. **Control**: Verifica whitelist y tipo de mensaje
4. **Buffer**: Redis acumula mensajes (60s wait para agrupar)
5. **Contexto**: Consulta perfil del cliente en PostgreSQL
6. **Análisis**: Procesa texto/imagen según tipo de contenido
7. **Carrito**: Actualiza carrito en Redis con cálculos
8. **Respuesta**: IA genera respuesta contextual
9. **Envío**: Entrega respuesta por API correspondiente
10. **Resumen**: Al finalizar conversación, guarda perfil actualizado

---

## 3. Componentes Principales

### 3.1 n8n (Orquestador)

**n8n** es el cerebro del sistema, un motor de automatización de código abierto que permite crear flujos de trabajo visuales sin necesidad de programar extensivamente.

#### Nodos Principales Utilizados:

| Nodo | Función | Configuración Clave |
|------|---------|---------------------|
| **Webhook** | Recibir mensajes de WhatsApp | Path: `/prueba` POST |
| **Chat Trigger** | Interfaz de testing en consola | Permite subir imágenes |
| **Code (JavaScript)** | Procesamiento personalizado | DataCleaning, Selector de Prompt |
| **HTTP Request** | Llamadas a Evolution API | Auth: Header API Key |
| **Redis** | Gestión de cache y memoria | Operaciones: push, get, delete |
| **PostgreSQL** | Persistencia de datos | UPSERT de perfiles |
| **Ollama** | IA local | Modelos: llama3.1, llama3.2-vision |
| **Wait** | Agrupación de mensajes | 60s en producción, 0s en testing |
| **Switch** | Enrutamiento condicional | Por tipo de trigger/API |
| **If** | Lógica condicional | Validaciones de datos |

#### Credenciales Configuradas:

- **EvolutionApi ApiKey**: Header Auth para autenticación con Evolution API
- **WP API Sender**: Credenciales para WhatsApp Business API oficial
- **Redis account**: Conexión a instancia Redis
- **Postgres account**: Conexión a base de datos PostgreSQL
- **Ollama account**: URL local del servidor Ollama

### 3.2 Evolution API (v2.3.7)

Evolution API es una **interfaz no oficial** para WhatsApp que permite mayor flexibilidad que la API oficial, aunque con riesgos de suspensión de cuenta.

#### Características Utilizadas:

- **Webhook de Mensajes**: Recepción en tiempo real de mensajes entrantes
- **Gestión de Presencia**: Cambiar estado (disponible, escribiendo, no disponible)
- **Marcar como Leído**: Confirmación de lectura de mensajes
- **Envío de Mensajes**: Texto, imágenes, documentos
- **Extracción de Media**: Obtener base64 de imágenes recibidas
- **Delay Dinámico**: Simular escritura humana con delays variables

#### Endpoints Utilizados:

```javascript
// Base URL
const dominio_evolution = "http://localhost:8080";

// Marcar como leído
POST /chat/markMessageAsRead/{instancia}
Body: { readMessages: [{ id: "mensaje_id", fromMe: false, remoteJid: "numero@s.whatsapp.net" }] }

// Cambiar presencia
POST /chat/sendPresence/{instancia}
Body: { number: "593xxx", presence: "composing", delay: 1200 }

// Cambiar estado general
POST /instance/setPresence/{instancia}
Body: { presence: "available" | "unavailable" }

// Enviar texto
POST /message/sendText/{instancia}
Body: { number: "593xxx", text: "mensaje", delay: 5000 }

// Obtener media en base64
POST /chat/getBase64FromMediaMessage/{instancia}
Body: { message: { key: { id: "mensaje_id" } }, convertToMp4: false }
```

#### Estructura de Webhook Recibido:

```json
{
  "instance": "nombre_instancia",
  "body": {
    "event": "messages.upsert",
    "data": {
      "key": {
        "remoteJid": "593xxxxxxxxx@s.whatsapp.net",
        "fromMe": false,
        "id": "3EB0XXXXX"
      },
      "messageType": "conversation" | "imageMessage",
      "pushName": "Nombre Usuario",
      "message": {
        "conversation": "Hola",
        "imageMessage": {
          "mimetype": "image/jpeg",
          "caption": "Texto con imagen"
        }
      }
    }
  }
}
```

### 3.3 WhatsApp Business API (Meta/Facebook)

La **API oficial** de Meta proporciona un canal empresarial confiable pero más limitado en funcionalidades.

#### Diferencias con Evolution API:

| Característica | Evolution API | WhatsApp Business API |
|----------------|---------------|----------------------|
| **Legalidad** | No oficial (riesgo) | Oficial (seguro) |
| **Presencia** | Sí (disponible/escribiendo) | No |
| **Delays** | Personalizables | No |
| **Costo** | Gratis | Conversaciones gratuitas limitadas |
| **Webhook** | Directo | Requiere verificación |
| **Media** | Base64 directo | URL con token temporal |

#### Configuración en n8n:

```javascript
// Nodo: WhatsApp Trigger
updates: ["messages"]
webhookId: "3a9967b8-955e-47d4-abf4-2d05af6cceed"

// Nodo: WhatsApp (Send)
operation: "send"
phoneNumberId: "925355883990190"
recipientPhoneNumber: "={{ $('WP API Oficial').item.json.contacts[0].wa_id }}"
textBody: "={{ $json.output }}"
```

### 3.4 PostgreSQL (Base de Datos)

#### Tabla: `perfil_cliente`

La base de datos almacena perfiles de usuarios para personalización y análisis.

**Estructura:**

```sql
CREATE TABLE public.perfil_cliente (
    numero_wp VARCHAR(15) PRIMARY KEY,
    perfil_usuario TEXT NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE perfil_cliente OWNER TO docker;
```

**Campos:**

- `numero_wp` (PK): Número de WhatsApp sin formato internacional (ej: `593988207600`)
- `perfil_usuario`: JSON o texto libre con resumen del cliente generado por IA
- `fecha_actualizacion`: Timestamp de última actualización automática

**Ejemplo de Perfil Usuario:**

```json
{
  "nombre": "Cliente",
  "intereses": ["electrónica", "ropa deportiva"],
  "historial_productos": [
    {"nombre": "Audífonos Bluetooth", "precio": 25.00, "fecha": "2024-02-15"},
    {"nombre": "Zapatillas Running", "precio": 45.00, "fecha": "2024-02-18"}
  ],
  "preferencias": {
    "metodo_pago": "transferencia",
    "urgencia": "normal"
  },
  "notas": "Cliente recurrente, prefiere productos de calidad media-alta"
}
```

### 3.5 Redis (Cache y Memoria)

Redis actúa como almacenamiento temporal y memoria conversacional con múltiples propósitos:

#### Estructuras de Datos Utilizadas:

**1. Cola de Mensajes Temporales** (LIST)
```
Key: {numero_cuenta}
Values: ["Mensaje 1", "Mensaje 2", "Mensaje 3"]
TTL: Hasta procesamiento
```

**2. IDs de Mensajes para Marcar como Leído** (LIST)
```
Key: {numero_cuenta}_idmsj
Values: ["3EB0XXX", "3EB0YYY", "3EB0ZZZ"]
TTL: Hasta marcado
```

**3. Carrito de Compras** (STRING - JSON serializado)
```
Key: carrito:{numero_cuenta}
Value: JSON {
  "productos": [...],
  "subtotal": 100.00,
  "impuesto": 15.00,
  "total": 115.00
}
TTL: 3600s (1 hora)
```

**4. Memoria Conversacional** (Gestionado por n8n Langchain)
```
Key: {numero_cuenta}_ia_V3
Value: Buffer de mensajes con ventana de 20 mensajes
TTL: 300s (testing) / 3600s (producción)
```

#### Operaciones Implementadas:

```javascript
// Guardar mensaje
operation: "push"
list: "={{ $json.numero_cuenta }}"
messageData: "={{ $json.mensaje_texto || '[Imagen/Archivo recibido]' }}"

// Obtener mensajes
operation: "get"
propertyName: "mensajes"
key: "={{ $('DataCleaning 1').item.json.numero_cuenta }}"
keyType: "list"

// Borrar mensajes
operation: "delete"
key: "={{ $('DataCleaning 1').item.json.numero_cuenta }}"

// Guardar carrito
operation: "set"
key: "=carrito:{{ $('DataCleaning 1').first().json.numero_cuenta }}"
value: "={{ $json.carrito_json_string }}"
expire: true
ttl: 3600
```

### 3.6 Ollama (Motor de IA)

Ollama proporciona modelos de lenguaje e imágenes ejecutados localmente sin dependencia de APIs externas.

#### Modelos Utilizados:

**1. llama3.1 (8b)**
- **Uso**: IA Contestadora y Resumidor
- **Contexto**: 8192 tokens
- **Temperatura**: 0.7 (balance creatividad/precisión)
- **Propósito**: Generar respuestas conversacionales naturales

**2. llama3.2-vision**
- **Uso**: Análisis de imágenes
- **Capacidad**: Extracción de texto y reconocimiento visual
- **Propósito**: Leer precios de capturas de pantalla de Temu

#### Configuración en n8n:

```javascript
// Nodo: Ollama Chat Model (IA Contestadora)
{
  type: "@n8n/n8n-nodes-langchain.lmChatOllama",
  model: "llama3.1:8b",
  baseURL: "http://localhost:11434",
  temperature: 0.7,
  maxTokens: 500
}

// Nodo: Ollama (Visión)
{
  type: "@n8n/n8n-nodes-langchain.ollama",
  model: "llama3.2-vision",
  maxTokens: 1000
}

// System Prompt IA Contestadora
systemMessage: `
Eres Estella, una asistente virtual experta en importaciones de Temu.
Tu ÚNICO objetivo es responder al usuario utilizando exactamente el texto 
que se te entrega en las instrucciones.
PROHIBIDO usar formato JSON. PROHIBIDO agregar etiquetas como "analisis" o "datos". 
Habla siempre como una humana normal.
`
```

### 3.7 Browserless (Scraping de Imágenes)

Browserless es una instancia de Chromium headless en Docker que permite extraer imágenes de URLs sin ser detectado como bot.

#### Configuración Docker:

```yaml
browserless:
  image: ghcr.io/browserless/chromium:latest
  container_name: browserless_chrome
  restart: always
  ports:
    - "3000:3000"
  environment:
    - MAX_CONCURRENT_SESSIONS=10
    - DEBUG=browserless*
    - STEALTH_EVASIONS=1         # Ocultar que es un bot
    - HEADLESS=false             # Simular navegador real
    - ENABLE_CORS=true
    - KEEP_ALIVE=true
    - CONNECTION_TIMEOUT=300000  # 5 min timeout
  shm_size: '2gb'
```

#### Uso en el Flujo:

Cuando un usuario envía un **enlace de Temu** (desde Evolution API), el sistema:

1. Detecta que es URL de Temu
2. Invoca Browserless para tomar captura de pantalla
3. Extrae la imagen del producto
4. Pasa imagen a Ollama Vision para OCR
5. Obtiene precio y características

---

## 4. Evolución del Proyecto

### 4.1 Flujo V1 - Prueba con LM Studio

**Fecha**: Primera versión  
**Estado**: Archivado (no en producción)

#### Características:

- ✅ Integración con **LM Studio** (servidor local de LLM)
- ✅ Soporte básico para Evolution API
- ✅ Whitelist de números para testing
- ✅ Procesamiento de texto simple
- ✅ Sistema de "presencia" para simular humano
- ❌ Sin API oficial de Meta
- ❌ Sin gestión de carrito
- ❌ Sin análisis de imágenes
- ❌ Sin memoria persistente en PostgreSQL

#### Lecciones Aprendidas:

- LM Studio funcionó bien para pruebas locales
- Necesidad de agrupar mensajes (usuarios que escriben en ráfagas)
- Importancia de delays dinámicos para parecer humano
- Detección de mensajes propios del bot (`fromMe: true`)

### 4.2 Flujo V2 - Flujo con API Oficial

**Fecha**: Evolución intermedia  
**Estado**: Archivado

#### Características:

- ✅ **Dual API**: Evolution + WhatsApp Business API oficial
- ✅ Manejo de imágenes desde API oficial (descarga desde URL con token)
- ✅ Mejora en limpieza de datos (`DataCleaning` más robusto)
- ✅ Procesamiento de imágenes con Ollama Vision
- ✅ Memoria conversacional con Redis (sin PostgreSQL aún)
- ❌ Sin gestión de carrito completa
- ❌ Sin selector dinámico de prompts
- ❌ Sin perfiles de cliente persistentes

#### Cambios Clave:

**Diferencias en Manejo de Imágenes:**

| Aspecto | Evolution API | Meta API |
|---------|---------------|-----------|
| **Formato recibido** | No incluye imagen directamente | URL con token temporal |
| **Extracción** | POST a `/getBase64FromMediaMessage` | HTTP Request a URL provista |
| **Conversión** | Base64 → Binary en Code Node | Directo desde HTTP |

**Código DataCleaning V2:**

```javascript
// TRIGGER: WHATSAPP API OFICIAL (META)
else if ($input.first().json.messaging_product) {
  datos.tipo_trigger = "oficial"
  
  const msg = $input.first().json.messages?.[0]
  const contact = $input.first().json.contacts?.[0]
  
  datos.numero_cuenta = contact.wa_id
  datos.id_mensaje = msg.id
  datos.nombre_contacto = contact.profile?.name || ""
  
  // Imagen desde API oficial
  if (msg.type === "image") {
    datos.tipo_mensaje = "imagen"
    datos.imagen = {
      id: msg.image.id,
      mime: msg.image.mime_type,
      caption: msg.image.caption || null
    }
    datos.mensaje_texto = msg.image.caption || "[IMAGEN SIN TEXTO]"
  }
}
```

### 4.3 Flujo V3 - Proyecto Estella (PRODUCCIÓN)

**Fecha**: Versión actual  
**Estado**: 🟢 **ACTIVO**

#### Características Completas:

✅ **Dual API con Switch inteligente**  
✅ **Gestión completa de carrito con Redis**  
✅ **Perfiles de cliente en PostgreSQL**  
✅ **Selector dinámico de prompts según contexto**  
✅ **Análisis de imágenes con Ollama Vision**  
✅ **Extracción de URLs con Browserless**  
✅ **Cálculo automático de impuestos (15%)**  
✅ **Memoria conversacional con ventana de 20 mensajes**  
✅ **Resumen automático al finalizar conversación**  
✅ **Detección de intención de pago (checkout)**  
✅ **Soporte multi-producto en carrito**  
✅ **Delays adaptativos según longitud de respuesta**  

#### Novedades Principales:

**1. Sistema de Carrito Inteligente**

```javascript
// Estructura del carrito en Redis
{
  "productos": [
    {
      "nombre": "Producto A",
      "precio_web": 25.00,
      "impuesto": 3.75,
      "total": 28.75
    },
    {
      "nombre": "Producto B",
      "precio_web": 40.00,
      "impuesto": 6.00,
      "total": 46.00
    }
  ],
  "cantidad_productos": 2,
  "gran_total": 74.75
}
```

**2. Selector de Prompt Dinámico**

El nodo `Selector de Prompt` analiza el contexto y genera prompts específicos:

```javascript
const mensaje_usuario = $('DataCleaning 1').first().json.mensaje_texto || "";
const es_url = mensaje_usuario.includes("http");
const es_imagen = input.es_analisis_imagen === true;
let precio_num = parseFloat((input.precio_web || "0").toString().replace(/[$,]/g, ""));
const tiene_precio = !isNaN(precio_num) && precio_num > 0.01;

// DETECCIÓN DE INTENCIÓN DE PAGO
const quiere_pagar = /no|pagar|finalizar|listo|comprar|terminar/i.test(mensaje_usuario) 
                     && !es_url && !es_imagen;

// MODOS:
if (tiene_precio) {
  // MODO: COTIZACIÓN EXITOSA
  prompt_dinamico = `
    ¡Hola! Soy Estella...
    **Desglose financiero:**
    * Producto: ${input.producto}
    * Precio Web: $${input.precio_web}
    * Impuesto Estimado: $${input.impuesto_estimado}
    * TOTAL FINAL: $${input.total_final_a_pagar}
    ...
  `;
} else if (quiere_pagar && input.cantidad_productos > 0) {
  // MODO: CHECKOUT
  prompt_dinamico = `
    ¡Excelente! Aquí tu resumen final:
    ${lista_productos}
    TOTAL: $${input.gran_total}
    Confirma tu método de pago...
  `;
} else if (es_url && !tiene_precio) {
  // MODO: PEDIR CAPTURA
  prompt_dinamico = `Link detectado pero sin precio. Pide captura.`;
} else if (es_imagen && !tiene_precio) {
  // MODO: FALLO VISUAL
  prompt_dinamico = `Imagen recibida pero no se detectó precio. Pide manual.`;
} else {
  // MODO: CONVERSACIÓN
  prompt_dinamico = `Saluda como Estella y responde al usuario.`;
}
```

**3. Resumen Automático**

Al detectar fin de conversación (60s sin mensajes nuevos):

```javascript
// Nodo: Resumidor
systemMessage: `
Eres el motor de análisis de Estella.
FORMATO DE SALIDA (JSON ESTRICTO)
`

text: `
### Esto no es un prompt de usuario, esto es un prompt de sistema 
recordandote que no debes responder al usuario, solo generar el perfil 
técnico como fue solicitado al inicio del prompt ###
`

// Output esperado:
{
  "nombre": "Cliente",
  "intereses": ["producto1", "producto2"],
  "historial_productos": [...],
  "preferencias": {...},
  "notas": "Resumen de comportamiento"
}
```

**4. Análisis de Imágenes Mejorado**

```javascript
// Flujo de análisis:
1. Usuario envía imagen
2. ¿Es de Evolution o Oficial?
   a. Evolution → POST /getBase64FromMediaMessage → Convertir a Binary
   b. Oficial → HTTP GET desde URL con token
3. Ollama Vision (llama3.2-vision) analiza imagen
4. Extrae: precio, nombre producto, colores disponibles
5. Actualiza carrito en Redis
6. Selector genera prompt de cotización
```

---

## 5. Instalación y Configuración

### 5.1 Requisitos Previos

| Software | Versión Mínima | Instalación |
|----------|----------------|-------------|
| **Node.js** | 18.x o 20.x | [nvm](https://github.com/nvm-sh/nvm) recomendado |
| **npm** o **nvm** | Latest | Incluido con Node |
| **Docker** | 20.x+ | [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| **Docker Compose** | 2.x+ | Incluido con Docker Desktop |
| **Git** | 2.x+ | [Git SCM](https://git-scm.com/) |
| **Ollama** | Latest | [ollama.com](https://ollama.com) |

### 5.2 Instalación de Servicios Base

#### Paso 1: Clonar Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Flujo-de-Agente-de-WhatsApp-para-Temu
```

#### Paso 2: Levantar Servicios Docker

El archivo `docker-compose.yaml` incluye **PostgreSQL**, **Redis** y **Browserless**.

```bash
# Iniciar servicios
docker compose up -d

# Verificar que estén corriendo
docker compose ps

# Salida esperada:
# NAME                    STATUS    PORTS
# postgres_evolution      Up        0.0.0.0:5433->5432/tcp
# redis_evolution         Up        0.0.0.0:6379->6379/tcp
# browserless_chrome      Up        0.0.0.0:3000->3000/tcp
```

#### Paso 3: Configurar Base de Datos PostgreSQL

```bash
# Conectarse al contenedor
docker exec -it postgres_evolution psql -U docker -d evolution_db

# Ejecutar script de creación
\i /path/to/perfil_cliente.sql

# O manualmente:
CREATE TABLE public.perfil_cliente (
    numero_wp VARCHAR(15) PRIMARY KEY,
    perfil_usuario TEXT NOT NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE perfil_cliente OWNER TO docker;

# Verificar
\dt
\d perfil_cliente

# Salir
\q
```

#### Paso 4: Instalar Ollama

**Windows:**
```powershell
# Descargar desde https://ollama.com/download
# Ejecutar instalador
# Verificar instalación
ollama --version
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Descargar Modelos:**
```bash
# Modelo de chat (8GB)
ollama pull llama3.1:8b

# Modelo de visión (5GB)
ollama pull llama3.2-vision

# Verificar
ollama list

# Salida esperada:
# NAME                     ID              SIZE
# llama3.1:8b             xxx             8.0GB
# llama3.2-vision         yyy             5.2GB
```

**Iniciar servidor:**
```bash
# Por defecto corre en http://localhost:11434
ollama serve
```

### 5.3 Instalación de Evolution API

⚠️ **IMPORTANTE**: No usar Docker para Evolution API v2.3.7 (solo soporta 2.2.3 desactualizada).

#### Instalación con NVM:

```bash
# 1. Instalar NVM (si no está instalado)
# Linux/Mac:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Windows: Descargar nvm-windows desde GitHub

# 2. Instalar Node.js 20
nvm install 20
nvm use 20

# 3. Clonar Evolution API
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# 4. Checkout versión 2.3.7
git checkout v2.3.7

# 5. Instalar dependencias
npm install

# 6. Crear archivo .env
cp .env.example .env
```

#### Configuración `.env` de Evolution API:

```env
# SERVER
SERVER_URL=http://localhost:8080
PORT=8080

# DATABASE (PostgreSQL del docker-compose)
DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://docker:password@localhost:5433/evolution_db

# REDIS (del docker-compose)
REDIS_ENABLED=true
REDIS_URI=redis://localhost:6379

# AUTHENTICATION
AUTHENTICATION_TYPE=apikey
AUTHENTICATION_API_KEY=your_super_secret_api_key_here

# QRCODE
QRCODE_TIMEOUT=60000

# WEBHOOK
WEBHOOK_GLOBAL_ENABLED=true
WEBHOOK_GLOBAL_URL=http://localhost:5678/webhook/prueba
WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS=true

# RABBITMQ (opcional, desactivar si no se usa)
RABBITMQ_ENABLED=false

# CHATWOOT (opcional)
CHATWOOT_ENABLED=false

# TYPEBOT (opcional)
TYPEBOT_ENABLED=false

# LOG
LOG_LEVEL=INFO
LOG_COLOR=true
```

#### Iniciar Evolution API:

```bash
npm run start:prod

# Salida esperada:
# [Evolution API] Server started on port 8080
# [Database] Connected to PostgreSQL
# [Redis] Connected to Redis
```

**Verificar funcionamiento:**
```bash
curl http://localhost:8080/
# Debería devolver información de la API
```

### 5.4 Instalación de n8n

#### Opción 1: Instalación Local (Recomendada)

```bash
# Instalar n8n globalmente
npm install -g n8n

# Iniciar n8n
n8n start

# Salida esperada:
# n8n ready on http://localhost:5678
```

**Configuración inicial:**
1. Abrir navegador en `http://localhost:5678`
2. Crear cuenta de usuario (primera vez)
3. Importar flujo desde archivo JSON

#### Opción 2: Docker (Alternativa)

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

⚠️ **Limitaciones de Docker**: Versiones desactualizadas de nodos, difícil conexión con servicios locales.

### 5.5 Configuración de n8n

#### Importar Flujo V3:

1. En n8n, ir a **Workflows** → **Add workflow**
2. Click en `...` (menú) → **Import from File**
3. Seleccionar `Flujo V3 - Proyecto Estella.json`
4. Click **Import**

#### Configurar Credenciales:

**1. EvolutionApi ApiKey**
- Tipo: `HTTP Header Auth`
- Name: `apikey`
- Value: `your_super_secret_api_key_here` (mismo que en `.env` de Evolution)

**2. Redis account**
- Host: `localhost`
- Port: `6379`
- Database: `0`

**3. Postgres account**
- Host: `localhost`
- Port: `5433`
- Database: `evolution_db`
- User: `docker`
- Password: `password`
- SSL: `Disable`

**4. Ollama account**
- Base URL: `http://localhost:11434`

**5. WP API Sender** (solo si usas API oficial)
- Access Token: (obtener desde [Meta Developer Console](https://developers.facebook.com/))
- Phone Number ID: Tu ID de número de teléfono de WhatsApp Business

#### Configurar Webhook:

**Evolution API:**
- Asegurar que `WEBHOOK_GLOBAL_URL` en `.env` apunte a: `http://localhost:5678/webhook/prueba`

**API Oficial (opcional):**
- Configurar webhook verification en Meta Developer Console
- URL: `http://tu-dominio-publico/webhook-test/xxx` (requiere HTTPS y dominio público)

### 5.6 Crear Instancia de WhatsApp en Evolution API

#### Usando Postman/cURL:

```bash
# POST http://localhost:8080/instance/create
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: your_super_secret_api_key_here" \
  -d '{
    "instanceName": "prueba_temu",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'

# Respuesta esperada:
{
  "instance": {
    "instanceName": "prueba_temu",
    "status": "created"
  },
  "qrcode": {
    "code": "2@xxx...",  // Código QR en formato texto
    "base64": "data:image/png;base64,xxx..."  // QR en imagen
  }
}
```

#### Escanear QR Code:

1. Abrir WhatsApp en tu teléfono
2. Ir a **Configuración** → **Dispositivos vinculados**
3. **Vincular un dispositivo**
4. Escanear el código QR de la respuesta anterior

> 📱 Si usas los números de prueba, asegúrate de que estén en la whitelist del código.

### 5.7 Configuración de Whitelist

Editar nodo `DataCleaning 1` en n8n:

```javascript
/*******************************
 * WHITELIST DE NÚMEROS
 *******************************/
const numeros_admitidos = [
  "593997350897",  // Prueba 1
  "593980062977",  // Prueba 2
  "593978640544",  // Tu número principal
  "593997129254",  // Cliente de confianza
  "593995817315",  // Equipo
  "593988207600"   // Soporte
];
```

**¿Cómo funciona?**

- Si `is_testing = true` → Sin delays, respuestas instantáneas
- Si `is_testing = false` → Modo producción con delays y esperas
- Si mensaje viene de número no admitido **y no estamos en producción** → Se descarta

Para **habilitar modo producción completo**, comentar la lógica de whitelist o devolver siempre `false`.

---

## 6. Base de Datos y Almacenamiento

### 6.1 Modelo de Datos PostgreSQL

#### Tabla: `perfil_cliente`

**Propósito**: Almacenar perfiles de clientes para personalización y análisis de comportamiento.

**Relaciones**: Ninguna (tabla única por ahora)

**Índices**:
- PRIMARY KEY en `numero_wp` (automático)

**Queries Frecuentes**:

```sql
-- Insertar o actualizar perfil
INSERT INTO perfil_cliente (numero_wp, perfil_usuario, fecha_actualizacion)
VALUES ('593988207600', '{"nombre": "Juan", "intereses": ["electrónica"]}', NOW())
ON CONFLICT (numero_wp)
DO UPDATE SET 
  perfil_usuario = EXCLUDED.perfil_usuario,
  fecha_actualizacion = NOW();

-- Buscar perfil
SELECT * FROM perfil_cliente WHERE numero_wp = '593988207600';

-- Listar todos los perfiles
SELECT numero_wp, fecha_actualizacion FROM perfil_cliente ORDER BY fecha_actualizacion DESC;

-- Eliminar perfiles antiguos (más de 6 meses)
DELETE FROM perfil_cliente WHERE fecha_actualizacion < NOW() - INTERVAL '6 months';
```

**Consideraciones**:

- **JSON vs TEXT**: Actualmente `perfil_usuario` es `TEXT`, permitiendo almacenar JSON o texto libre. Para queries complejas, considerar cambiar a tipo `JSONB`.
- **Backup**: Configurar backups automáticos del contenedor de PostgreSQL.
- **Migración futura**: Posible normalización en tablas separadas (clientes, productos, conversaciones).

### 6.2 Almacenamiento en Redis

#### Patrones de Keys:

| Key Pattern | Tipo | TTL | Propósito |
|-------------|------|-----|-----------|
| `{numero}` | LIST | Manual | Cola de mensajes temporales |
| `{numero}_idmsj` | LIST | Manual | IDs de mensajes para marcar leídos |
| `carrito:{numero}` | STRING | 3600s | Carrito de compras serializado |
| `{numero}_ia_V3` | STRING | 3600s | Memoria conversacional (Langchain) |

#### Operaciones Comunes:

```javascript
// === Cola de Mensajes ===
// Agregar mensaje
RPUSH 593988207600 "Hola, quiero cotizar esto"

// Obtener todos los mensajes
LRANGE 593988207600 0 -1

// Borrar cola
DEL 593988207600

// === IDs de Mensajes ===
// Agregar ID
RPUSH 593988207600_idmsj "3EB0ABC123"

// Obtener IDs
LRANGE 593988207600_idmsj 0 -1

// Borrar IDs
DEL 593988207600_idmsj

// === Carrito ===
// Guardar carrito
SET "carrito:593988207600" '{"productos":[...],"total":100.00}' EX 3600

// Obtener carrito
GET "carrito:593988207600"

// Borrar carrito
DEL "carrito:593988207600"

// === Memoria Conversacional ===
// (Gestionado automáticamente por n8n Langchain)
// Estructura interna:
// {numero}_ia_V3 → Buffer de últimos 20 mensajes con formato:
// [
//   {"role": "user", "content": "Hola"},
//   {"role": "assistant", "content": "¡Hola! Soy Estella..."},
//   ...
// ]
```

#### Limpieza y Mantenimiento:

```bash
# Conectarse a Redis
docker exec -it redis_evolution redis-cli

# Ver todas las keys
KEYS *

# Limpiar keys expiradas manualmente (Redis lo hace automáticamente)
# Borrar carrito de un usuario específico
DEL carrito:593988207600

# Borrar todas las memorias conversacionales (PELIGRO)
KEYS *_ia_V3
# (listar primero, luego borrar individualmente)

# Ver estadísticas
INFO memory
INFO keyspace
```

### 6.3 Estrategia de Persistencia

```
┌─────────────────────────────────────────────────────────┐
│                   DATOS TEMPORALES                      │
│                      (Redis)                            │
│  • Mensajes en buffer (< 60s)                           │
│  • Carrito actual (1h)                                  │
│  • Memoria conversacional (1h)                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Al finalizar conversación
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 DATOS PERSISTENTES                      │
│                   (PostgreSQL)                          │
│  • Perfil completo del cliente                          │
│  • Historial de productos                               │
│  • Preferencias de pago                                 │
└─────────────────────────────────────────────────────────┘
```

**Ventajas**:
- ⚡ **Performance**: Redis para operaciones rápidas y temporales
- 💾 **Persistencia**: PostgreSQL para datos a largo plazo
- 🔄 **Sincronización**: Resumen generado por IA al finalizar conversación
- 🧹 **Auto-limpieza**: TTLs en Redis evitan saturación

---

## 7. Flujo de Trabajo Detallado

### 7.1 Diagrama de Secuencia Completa

```
USUARIO              WHATSAPP API         N8N WEBHOOK          DATACLEANING         REDIS                POSTGRESQL           IA (OLLAMA)          RESPUESTA
  │                       │                    │                     │                    │                      │                      │                  │
  │─────Enviar msg───────>│                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │─────POST /webhook──>│                     │                    │                      │                      │                  │
  │                       │                    │────Extrae datos─────>│                    │                      │                      │                  │
  │                       │                    │                     │─Validar whitelist─>│                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │─────PUSH msg──────>│                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │<────Wait 60s────────│                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │─────LRANGE msgs───>│                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │────SELECT perfil────────────────────────>│                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │<────Perfil existente│                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │────Concatenar msgs + perfil───────────────────────────────────────────────────────>│
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │<──Procesar con IA│
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │────Generar resp──>│
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │<────────────────────────────────────────────────────────────────Respuesta generada│
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │────Enviar estado disponible────────────>│                      │                      │                  │
  │<─────"disponible"─────│                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │────Marcar leído──────────────────────────>│                      │                      │                  │
  │<───✓✓ leído───────────│                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │────Enviar "escribiendo" + delay──────────────────────────────────────────────────────────────────────────>│
  │<─────escribiendo...───│                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │────Enviar texto final────────────────────>│                      │                      │                  │
  │<─────MENSAJE──────────│                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │────Estado "no disponible"────────────────>│                      │                      │                  │
  │<─────"ausente"────────│                    │                     │                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │<─────Wait 60s───────│                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │─────¿Nuevos msgs?──────────────────────>│                      │                      │                  │
  │                       │                    │                     │<────Empty list─────│                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │────Resumir conversación─────────────────────────────────────────────────────────────────────────────────>│
  │                       │                    │                     │                    │                      │                      │<────Resumen JSON│
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │─────UPSERT perfil──────────────────────────────────────────────>│                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
  │                       │                    │<────FIN FLUJO───────│                    │                      │                      │                  │
  │                       │                    │                     │                    │                      │                      │                  │
```

### 7.2 Desglose por Fase

#### FASE 1: Recepción y Limpieza

**Nodos involucrados**: 
- `Evolution API` (Webhook)
- `WP API Oficial` (WhatsApp Trigger)
- `Mensaje Consola` (Chat Trigger)
- `DataCleaning 1` (Code Node)

**Lógica del DataCleaning:**

```javascript
// 1. DETECTAR ORIGEN
if ($input.first().json.action) {
  // Trigger desde consola de n8n
  datos.tipo_trigger = "consola";
  datos.numero_cuenta = "Consola";
  datos.mensaje_texto = $input.first().json.chatInput;
}
else if ($input.first().json.body?.data?.messageType) {
  // Trigger desde Evolution API
  datos.tipo_trigger = "evolution";
  datos.instancia = $input.first().json.body.instance;
  datos.numero_cuenta = $input.first().json.body.data.key.remoteJid;
  
  // Verificar whitelist
  const permitido = comprobar_whitelist(datos.numero_cuenta, true);
  if (permitido === null) return []; // Mensaje propio del bot
  datos.is_testing = permitido;
  
  // Extraer nombre (fix para nombres nulos o numéricos)
  const pushName = $input.first().json.body.data.pushName;
  datos.nombre_contacto = pushName && isNaN(pushName) ? pushName : "Cliente";
  
  datos.id_mensaje = $input.first().json.body.data.key.id;
  datos.mensaje_texto = $input.first().json.body.data.message.conversation || 
                        $input.first().json.body.data.message.imageMessage?.caption || "";
}
else if ($input.first().json.messaging_product) {
  // Trigger desde API oficial de Meta
  datos.tipo_trigger = "oficial";
  const contact = $input.first().json.contacts[0];
  datos.numero_cuenta = contact.wa_id;
  datos.nombre_contacto = contact.profile.name;
  // ... (similar)
}

// 2. VALIDAR Y RETORNAR
return datos;
```

**Output del DataCleaning:**

```json
{
  "tipo_trigger": "evolution",
  "dominio_evolution": "http://localhost:8080",
  "is_testing": true,
  "instancia": "prueba_temu",
  "numero_cuenta": "593988207600@s.whatsapp.net",
  "nombre_contacto": "Adrián",
  "id_mensaje": "3EB0ABC123DEF",
  "tipo_mensaje": "conversation",
  "mensaje_texto": "Hola, quiero cotizar este producto: https://temu.com/..."
}
```

#### FASE 2: Decisión de Ruta

**Nodo**: `¿Mensaje tipo consola?` (If Node)

```javascript
// Condición:
$json.tipo_trigger === "consola"

// Salida TRUE → Directo a IA Contestadora (sin Redis)
// Salida FALSE → Procesar con Redis
```

**Si FALSE (mensajes de WhatsApp)**:

**Nodo**: `¿Guardar ID Mensajes?` (If Node)

```javascript
// Condición:
$json.tipo_trigger === "evolution"

// TRUE → Guardar IDs de mensajes (para marcar como leído después)
// FALSE → Solo guardar texto del mensaje
```

#### FASE 3: Buffer de Mensajes (Redis)

**Nodos**:
- `Guardar IDs Mensajes` (Redis PUSH)
- `Guardar Mensajes` (Redis PUSH)
- `Esperar a mas mensajes` (Wait Node - 60s)

**¿Por qué esperar 60 segundos?**

Muchos usuarios escriben en "ráfagas":
```
[10:00:00] Hola
[10:00:02] Quiero cotizar
[10:00:05] Este producto
[10:00:08] https://temu.com/...
```

Sin espera, el bot respondería 4 veces. Con el wait de 60s:
```
[10:00:00] Mensaje 1 → PUSH a Redis → Wait 60s
[10:00:02] Mensaje 2 → PUSH a Redis → Renicia Wait
[10:00:05] Mensaje 3 → PUSH a Redis → Renicia Wait
[10:00:08] Mensaje 4 → PUSH a Redis → Renicia Wait
[10:01:08] (60s sin mensajes) → Procesar todos juntos
```

**Código de Espera:**

```javascript
// Nodo: Esperar a mas mensajes
amount: "={{ $('DataCleaning 1').item.json.is_testing ? 0 : 60 }}"
```

- **Testing**: 0 segundos (respuesta inmediata)
- **Producción**: 60 segundos (agrupación)

#### FASE 4: Obtención de Contexto

**Nodos**:
- `Conseguir Mensajes` (Redis LRANGE)
- `Buscar Perfil de Cliente` (PostgreSQL SELECT)
- `Concatenar Mensajes` (Code Node)

**Código de Concatenación:**

```javascript
// Unir todos los mensajes de Redis
const mensajes_array = $('Conseguir Mensajes').first().json.mensajes || [];
const mensajes_texto = mensajes_array.join("\n");

// Obtener perfil de PostgreSQL
const perfil = $('Buscar Perfil de Cliente').first().json.perfil_usuario || null;

// Formato final para la IA
let contexto_completo = "";

if (perfil) {
  contexto_completo = `
    PERFIL DEL CLIENTE:
    ${perfil}
    
    ---
    
    MENSAJES RECIENTES:
    ${mensajes_texto}
  `;
} else {
  contexto_completo = mensajes_texto;
}

return {
  contexto_completo,
  mensajes_texto,
  tiene_perfil: !!perfil
};
```

#### FASE 5: Procesamiento de Contenido

**Bifurcación**: `¿Es imagen?` (If Node)

**RUTA A: Procesamiento de Texto**
```
¿Es imagen? → FALSE
  └─> Es un enlace? → ¿Contiene "http"?
        │
        ├─> TRUE (URL de Temu)
        │     └─> Origen de la Imagen → ¿Es Evolution o Oficial?
        │           │
        │           ├─> Evolution → Browser Docker (Browserless)
        │           │     └─> Extraer Precio (Ollama Vision)
        │           │
        │           └─> Oficial → Obtener URL (HTTP Request)
        │                 └─> Descargar Imagen
        │                       └─> Analizar Texto (Llama3)
        │
        └─> FALSE (Texto simple)
              └─> Selector de Prompt → IA Contestadora
```

**RUTA B: Procesamiento de Imagen**
```
¿Es imagen? → TRUE
  └─> Origen de la Imagen
        │
        ├─> Evolution → Extraer Imagen (POST /getBase64FromMediaMessage)
        │     └─> Convertir a imagen (Code Node - Base64 a Binary)
        │           └─> Analyze image (Ollama Vision)
        │
        └─> Oficial → Obtener URL → Descargar Imagen
              └─> Analyze image (Ollama Vision)
```

**Código de Browser Docker (Browserless):**

```javascript
// Nodo: Browser Docker (HTTP Request)
method: "POST"
url: "http://localhost:3000/screenshot"
body: {
  "url": "{{ $('DataCleaning 1').first().json.mensaje_texto }}",
  "type": "jpeg",
  "fullPage": false,
  "selector": ".product-image", // Selector específico de Temu
  "options": {
    "waitUntil": "networkidle2"
  }
}

// Respuesta: Imagen en formato binary
```

**Código de Ollama Vision:**

```javascript
// Nodo: Analyze image
model: "llama3.2-vision"
prompt: `
Analiza esta imagen de un producto de Temu.

EXTRAE:
1. **Precio**: Valor numérico exacto (ej: 25.99)
2. **Nombre del producto**: Título completo
3. **Colores disponibles**: Lista de opciones (si aparecen)

FORMATO DE SALIDA (JSON):
{
  "precio": 25.99,
  "nombre": "Audífonos Bluetooth Inalámbricos",
  "colores": ["Negro", "Blanco", "Rojo"]
}
`

// Binary input: Imagen adjunta
```

#### FASE 6: Gestión de Carrito

**Nodos**:
- `Conseguir Carrito` (Redis GET)
- `Matematicas` (Code Node)
- `Guardar en Carrito` (Redis SET)

**Código de Matemáticas:**

```javascript
// Input desde nodos anteriores
const precio_web = parseFloat($json.precio) || 0;
const nombre_producto = $json.nombre || "Producto sin nombre";

// Calcular impuesto (15%)
const impuesto_estimado = precio_web * 0.15;
const total_producto = precio_web + impuesto_estimado;

// Obtener carrito existente
let carrito = {};
try {
  carrito = JSON.parse($('Conseguir Carrito').first().json.carrito_json || "{}");
} catch (e) {
  carrito = { productos: [], cantidad_productos: 0, gran_total: 0 };
}

// Agregar producto al carrito
carrito.productos = carrito.productos || [];
carrito.productos.push({
  nombre: nombre_producto,
  precio_web: precio_web.toFixed(2),
  impuesto: impuesto_estimado.toFixed(2),
  total: total_producto.toFixed(2)
});

// Recalcular totales
carrito.cantidad_productos = carrito.productos.length;
carrito.gran_total = carrito.productos.reduce((sum, p) => sum + parseFloat(p.total), 0).toFixed(2);

return {
  carrito: carrito,
  carrito_json_string: JSON.stringify(carrito),
  producto: nombre_producto,
  precio_web: precio_web.toFixed(2),
  impuesto_estimado: impuesto_estimado.toFixed(2),
  total_final_a_pagar: total_producto.toFixed(2),
  cantidad_productos: carrito.cantidad_productos,
  gran_total: carrito.gran_total,
  es_analisis_imagen: true,
  colores: $json.colores || []
};
```

#### FASE 7: Selector de Prompt Dinámico

**Nodo**: `Selector de Prompt` (Code Node)

Ver código completo en sección 4.3. Resumen de modos:

| Modo | Condición | Prompt Generado |
|------|-----------|-----------------|
| **COTIZACIÓN EXITOSA** | `tiene_precio === true` | Plantilla con desglose financiero completo |
| **CHECKOUT** | `quiere_pagar && cantidad_productos > 0` | Lista final del carrito + solicitud de pago |
| **PEDIR CAPTURA** | `es_url && !tiene_precio` | Solicitud de screenshot del producto |
| **FALLO VISUAL** | `es_imagen && !tiene_precio` | Pedir precio manualmente |
| **CONVERSACIÓN** | Ninguna de las anteriores | Saludo general de Estella |

#### FASE 8: Generación de Respuesta

**Nodo**: `IA Contestadora` (Langchain Agent + Ollama)

**Configuración:**

```javascript
// Agent
promptType: "define"
text: "={{ $('Selector de Prompt').first().json.prompt_dinamico }}"
systemMessage: `
Eres Estella, una asistente virtual experta en importaciones de Temu.
Tu ÚNICO objetivo es responder al usuario utilizando exactamente el texto 
que se te entrega en las instrucciones.
PROHIBIDO usar formato JSON. PROHIBIDO agregar etiquetas como "analisis" o "datos". 
Habla siempre como una humana normal.
`

// Langchain Memory (Redis Chat Memory)
sessionKey: "={{ $('DataCleaning 1').item.json.numero_cuenta + '_ia_V3' }}"
sessionTTL: "={{ $('DataCleaning 1').item.json.is_testing ? 300 : 3600 }}"
contextWindowLength: 20  // Últimos 20 mensajes

// Model (Ollama Chat Model)
model: "llama3.1:8b"
temperature: 0.7
maxTokens: 500
```

**Output:**

```json
{
  "output": "¡Hola! Soy Estella, tu asistente de importaciones en Temu.\n\n**Desglose financiero:**\n\n* **Producto:** Audífonos Bluetooth Inalámbricos\n* **Precio Web:** $25.99\n\n-------------------------------------------\n* **Subtotal Acumulado:** $25.99\n* **Impuesto Estimado:** $3.90\n* **TOTAL FINAL A PAGAR:** $29.89\n\n¿Desea agregar algún otro producto al carrito o prefiere finalizar la orden?"
}
```

#### FASE 9: Redirección y Envío

**Nodo**: `Redirección Respuesta` (Switch Node)

```javascript
// Condiciones:
CASO 1: tipo_trigger === "evolution" → Enviar por Evolution API
CASO 2: tipo_trigger === "oficial" → Enviar por API Oficial
CASO 3: tipo_trigger === "consola" → Finalizar (respuesta ya en consola)
```

**CASO 1: Evolution API**

**Secuencia de nodos**:

1. **Enviar Estado Disponible** (HTTP Request)
```javascript
POST /instance/setPresence/{instancia}
Body: { "presence": "available" }
```

2. **Conseguir ID Mensaje** (Redis LRANGE)
```javascript
// Obtener IDs guardados en FASE 3
key: "={{ $('DataCleaning 1').item.json.numero_cuenta + '_idmsj' }}"
```

3. **Estructurar Body Request** (Code Node)
```javascript
// Crear array de mensajes para marcar como leídos
const ids = $('Conseguir ID Mensaje').first().json.mensajes || [];
const numero = $('DataCleaning 1').item.json.numero_cuenta;

return {
  readMessages: ids.map(id => ({
    id: id,
    fromMe: false,
    remoteJid: numero
  }))
};
```

4. **Marcar como leído** (HTTP Request)
```javascript
POST /chat/markMessageAsRead/{instancia}
Body: {{ $json }} // Output del nodo anterior
```

5. **Borrar IDs Mensajes** (Redis DELETE)
```javascript
key: "={{ $('DataCleaning 1').item.json.numero_cuenta + '_idmsj' }}"
```

6. **Enviar estado "escribiendo"** (HTTP Request)
```javascript
POST /chat/sendPresence/{instancia}
Body: {
  "number": "{{ numero_cuenta }}",
  "presence": "composing",
  "delay": {{ delay_dinamico }} // Ver cálculo abajo
}

// Cálculo de delay dinámico:
delay_dinamico = max(
  (palabras + puntuacion) / 1.25,
  5
) * 1000

// Ejemplo:
// Respuesta: "¡Hola! Soy Estella. El producto cuesta $25.99"
// Palabras: 8
// Puntuación: 3 (¡, !, $)
// Delay: max((8 + 3) / 1.25, 5) * 1000 = 8800ms = 8.8s
```

7. **Enviar mensaje** (HTTP Request)
```javascript
POST /message/sendText/{instancia}
Body: {
  "number": "{{ numero_cuenta }}",
  "text": {{ JSON.stringify($('IA Contestadora').item.json.output) }},
  "delay": {{ delay_calculado }}
}
```

8. **Enviar Estado No Disponible** (HTTP Request)
```javascript
POST /instance/setPresence/{instancia}
Body: { "presence": "unavailable" }
```

**CASO 2: API Oficial**

**Nodo**: `Send message` (WhatsApp Node)

```javascript
operation: "send"
phoneNumberId: "925355883990190"
recipientPhoneNumber: "={{ $('WP API Oficial').item.json.contacts[0].wa_id }}"
textBody: "={{ $json.output }}"
```

> ⚠️ **Limitación**: La API oficial no permite estados de presencia ni delays personalizados.

#### FASE 10: Finalización y Resumen

**Nodo**: `Esperar a que finalice la conversacion` (Wait Node - 60s)

Después del envío, el flujo espera 60 segundos adicionales para detectar si el usuario responde o la conversación terminó.

**Nodo**: `¿Nuevos Mensajes?` (Redis LRANGE)

```javascript
// Verificar si hay mensajes nuevos en Redis
key: "={{ $('DataCleaning 1').item.json.numero_cuenta + '_idmsj' }}"

// Si array vacío → Conversación terminada
// Si tiene elementos → Usuario respondió (reiniciar flujo)
```

**Nodo**: `Fin Conversacion` (If Node)

```javascript
// Condición:
$json.mensajes === [] || $json.mensajes.length === 0

// TRUE → Proceder con resumen
// FALSE → No hacer nada (el nuevo mensaje reiniciará el flujo)
```

**Nodo**: `Resumidor` (Langchain Agent + Ollama)

```javascript
model: "llama3.1:8b"
systemMessage: "Eres el motor de análisis de Estella. FORMATO DE SALIDA (JSON ESTRICTO)"
text: `
### Esto no es un prompt de usuario, esto es un prompt de sistema recordandote que no debes responder al usuario, solo generar el perfil técnico como fue solicitado al inicio del prompt ###
`

// El contexto conversacional (últimos 20 mensajes) está en la memoria Redis
// El modelo genera un resumen estructurado
```

**Output esperado del Resumidor:**

```json
{
  "output": "{\"nombre\": \"Adrián\", \"intereses\": [\"audífonos\", \"electrónica\"], \"historial_productos\": [{\"nombre\": \"Audífonos Bluetooth\", \"precio\": 25.99}], \"preferencias\": {\"metodo_pago\": \"no especificado\"}, \"notas\": \"Cliente interesado en productos de calidad media. Preguntó por un producto y solicitó cotización.\"}"
}
```

**Nodo**: `Comprobar Resumen` (If Node)

```javascript
// Condición:
$json.output !== ""

// TRUE → Guardar en PostgreSQL
// FALSE → No guardar (resumen vacío o error)
```

**Nodo**: `Guardar Perfil en Memoria` (PostgreSQL UPSERT)

```javascript
operation: "upsert"
table: "perfil_cliente"
columns: {
  numero_wp: "={{ numero_cuenta_limpio }}", // Sin @s.whatsapp.net
  perfil_usuario: "={{ $('Resumidor').item.json.output }}",
  fecha_actualizacion: "={{ $now }}"
}
matchingColumns: ["numero_wp"]
```

**Fin del flujo.**

---

## 8. Características Avanzadas

### 8.1 Sistema de Whitelist Dinámico

El sistema permite control fino de acceso para testing y producción.

**Código completo:**

```javascript
/*******************************
 * WHITELIST DE NÚMEROS
 *******************************/
const numeros_admitidos = [
  "593997350897",
  "593980062977",
  "593978640544",
  "593997129254",
  "593995817315",
  "593988207600"
];

/*******************************
 * FUNCIÓN WHITELIST
 *******************************/
function comprobar_whitelist(numero, evolutional) {
  if (!numero) return false;

  // Limpiar número si viene de evolution
  const numero_limpio =
    evolutional && typeof numero === "string"
      ? numero.split("@")[0]
      : numero;

  // Si el mensaje es enviado por el bot, cortamos flujo
  if (evolutional && $input.first().json.body?.data?.key?.fromMe) {
    return null; // señal explícita de corte
  }

  return numeros_admitidos.includes(numero_limpio);
}
```

**Casos de uso:**

| Retorno | Significado | Acción |
|---------|-------------|--------|
| `true` | Testing permitido | `is_testing = true` (sin delays) |
| `false` | Producción permitida | `is_testing = false` (con delays) |
| `null` | Mensaje propio del bot | Cortar flujo (return []) |

**Activar modo producción total:**

```javascript
// Opción 1: Comentar verificación
// const permitido = comprobar_whitelist(...);
const permitido = false; // Forzar modo producción

// Opción 2: Devolver siempre false
function comprobar_whitelist(numero, evolutional) {
  if (evolutional && $input.first().json.body?.data?.key?.fromMe) {
    return null;
  }
  return false; // Todos en modo producción
}
```

### 8.2 Delays Adaptativos

Los delays simulan escritura humana y previenen detección de bots.

**Fórmula:**

```javascript
delay_ms = max(
  (cantidad_palabras + cantidad_puntuacion) / velocidad_escritura,
  minimo_segundos
) * 1000

// Valores:
// velocidad_escritura = 1.25 palabras por segundo
// minimo_segundos = 5 segundos
```

**Implementación en n8n:**

```javascript
// Nodo: Enviar estado "escribiendo"
jsonBody: `
{
  "number": "{{ $('DataCleaning 1').item.json.numero_cuenta }}",
  "presence": "composing",
  "delay": {{ max(
    ($('IA Contestadora').item.json.output.split(' ').length + 
     ($('IA Contestadora').item.json.output.match(/[¿?¡!,]/g) || []).length
    ) / 1.25, 
    5
  ) * 1000 }}
}
`

// Nodo: Enviar mensaje
jsonBody: `
{
  "number": "{{ $('DataCleaning 1').item.json.numero_cuenta }}",
  "text": {{ JSON.stringify($('IA Contestadora').item.json.output) }},
  "delay": {{ max(...) * 1000 }} // Mismo cálculo
}
`
```

**Ejemplos de delays:**

| Respuesta | Palabras | Puntos | Delay |
|-----------|----------|--------|-------|
| "Hola" | 1 | 0 | 5s (mínimo) |
| "¡Hola! Soy Estella." | 3 | 2 | 5s (mínimo) |
| "El producto cuesta $25.99. ¿Deseas comprarlo?" | 6 | 3 | 7.2s |
| Cotización completa (~100 palabras) | 100 | 15 | 92s |

### 8.3 Agrupación de Mensajes

Ya explicado en FASE 3. Recordatorio de lógica:

```
Wait Node renicia timer cada vez que llega un mensaje nuevo.
Solo cuando pasan 60s sin actividad se procesa el grupo completo.
```

**Ventajas:**
- ✅ Menos llamadas a la IA (economía)
- ✅ Contexto completo en una respuesta
- ✅ Experiencia de usuario más fluida

**Desventajas:**
- ❌ Latencia de 60s en primer mensaje
- ❌ Usuario puede pensar que no funciona

**Mitigación**: Enviar ACK inmediato (futuro):

```javascript
// Al recibir primer mensaje, enviar:
"Recibido, analizando tu consulta..."
// Luego procesar con wait normal
```

### 8.4 Análisis de Imágenes Multi-Fuente

El sistema puede extraer imágenes de 3 fuentes:

**1. Archivo adjunto directo (Consola n8n)**
```
Usuario → Arrastra imagen a chat de n8n
       → $input.first().json.files[0]
       → Binary data directo a Ollama Vision
```

**2. Mensaje de imagen (Evolution API)**
```
Usuario → Envía imagen por WhatsApp
       → Evolution webhook incluye messageType: "imageMessage"
       → POST /chat/getBase64FromMediaMessage
       → Code Node convierte base64 → binary
       → Ollama Vision
```

**3. URL de imagen (Ambas APIs)**
```
Usuario → Envía link de producto Temu
       → Detectar "http" en mensaje
       → Browserless screenshot (Evolution) 
          O HTTP Request a URL (Oficial)
       → Ollama Vision
```

**Código de Detección:**

```javascript
// Nodo: ¿Es imagen?
const tipo_mensaje = $('DataCleaning 1').first().json.tipo_mensaje;
const mensaje_texto = $('DataCleaning 1').first().json.mensaje_texto;

// Verificar si es imagen directa
const es_imagen_directa = tipo_mensaje === "imageMessage" || 
                         tipo_mensaje === "imagen";

// O si el mensaje anterior generó análisis de imagen
const es_analisis_previo = $('Selector de Prompt').first().json.es_analisis_imagen === true;

if (es_imagen_directa || es_analisis_previo) {
  return true; // Ruta de imagen
}

// Sino, verificar si es URL
const es_url = mensaje_texto && mensaje_texto.includes("http");
return !es_url; // Si no es URL, procesar como texto normal
```

### 8.5 Cálculo Automático de Impuestos

Ecuador (país de origen del proyecto) cobra **15% de impuesto** sobre importaciones.

**Fórmula:**

```javascript
// Entrada: Precio en página web de Temu
precio_web = 25.99

// Cálculo:
impuesto = precio_web * 0.15  // 3.90
total = precio_web + impuesto   // 29.89

// Para múltiples productos:
productos.forEach(p => {
  p.impuesto = p.precio_web * 0.15;
  p.total = p.precio_web + p.impuesto;
});

gran_total = productos.reduce((sum, p) => sum + p.total, 0);
```

**Personalización para otros países:**

```javascript
// Crear variable de configuración
const TASA_IMPUESTO = 0.15; // 15% para Ecuador

// Ajustar según país:
// USA: 0.0625 (California) - 0.00 (Oregon)
// México: 0.16 (IVA)
// Colombia: 0.19 (IVA)
// España: 0.21 (IVA)

// Uso:
impuesto = precio_web * TASA_IMPUESTO;
```

### 8.6 Memoria Conversacional con Ventana Deslizante

Redis Chat Memory de Langchain implementa ventana deslizante automática.

**Configuración:**

```javascript
// Nodo: Redis Chat Memory
sessionKey: "={{ numero_cuenta + '_ia_V3' }}"
sessionTTL: 3600  // 1 hora
contextWindowLength: 20  // Últimos 20 mensajes
```

**Comportamiento:**

```
Mensaje 1  ──┐
Mensaje 2  ──┤
...          ├─> Ventana de 20
Mensaje 19 ──┤
Mensaje 20 ──┘
Mensaje 21 ──┐ (Mensaje 1 se elimina)
Mensaje 22 ──┤
...          ├─> Ventana desliza
Mensaje 39 ──┤
Mensaje 40 ──┘
```

**Ventajas:**
- ✅ Memoria limitada (no crece indefinidamente)
- ✅ Contexto reciente preservado
- ✅ TTL previene datos huérfanos

**Alternativa sin ventana (memoria completa):**

```javascript
// Cambiar a:
contextWindowLength: -1  // Sin límite

// ⚠️ Cuidado: Puede llenar Redis y exceder tokens de IA
```

---

## 9. Problemas Conocidos y Soluciones

*(Basado en el archivo `problemas conocidos en evolutional api.md`)*

### 9.1 Imágenes No Procesadas

**Descripción**: Evolution API recibe imágenes pero el flujo actual no las procesa completamente en todos los casos.

**Efecto**: Imágenes ignoradas o errores en nodos de procesamiento.

**Soluciones Implementadas**:
✅ Nodo `¿Es imagen?` detecta `imageMessage`  
✅ Endpoint `/getBase64FromMediaMessage` extrae imagen  
✅ Code Node convierte base64 → binary  
✅ Ollama Vision analiza imagen  

**Pendiente**:
- ⚠️ Agregar filtros para imágenes corruptas
- ⚠️ Soporte para múltiples imágenes en un mensaje

### 9.2 Crashs con Stickers y Reacciones

**Descripción**: Mensajes de tipo `stickerMessage` o `reactionMessage` causan errores en el flujo.

**Efecto**: n8n crashea o el flujo falla, perdiendo contexto.

**Solución Recomendada**:

```javascript
// Al inicio de DataCleaning 1, después de detectar Evolution:
if ($input.first().json.body?.data?.messageType) {
  const tipo_mensaje = $input.first().json.body.data.messageType;
  
  // Lista de tipos no soportados
  const tipos_ignorados = [
    "stickerMessage",
    "reactionMessage",
    "audioMessage",  // Opcional: si no quieres procesar audios
    "videoMessage"   // Opcional
  ];
  
  if (tipos_ignorados.includes(tipo_mensaje)) {
    console.log(`[INFO] Mensaje tipo ${tipo_mensaje} ignorado`);
    return []; // Cortar flujo sin procesar
  }
  
  // ... continuar con lógica normal
}
```

**Estado**: ❌ **NO IMPLEMENTADO** (requiere agregar al código)

### 9.3 Respuestas Fuera de Orden (Race Condition)

**Descripción**: Si el bot está generando respuesta A y llega mensaje B, puede responder B antes que A.

**Efecto**: Conversaciones mezcladas y confusión del usuario.

**Causa**: Múltiples ejecuciones del flujo en paralelo para el mismo usuario.

**Solución Implementada**:
✅ Redis con colas por `numero_cuenta` serializa mensajes  
✅ Wait de 60s agrupa mensajes (reduce concurrencia)  

**Solución Adicional Recomendada (Lock Distribuido)**:

```javascript
// Al inicio del flujo, después de DataCleaning:
const lock_key = `lock:${numero_cuenta}`;

// Intentar obtener lock
const lock_acquired = await redis.set(lock_key, "1", "EX", 120, "NX");

if (!lock_acquired) {
  console.log(`[INFO] Conversación ${numero_cuenta} ya en proceso. Esperando...`);
  // Esperar y reintentar, o descartar mensaje
  return [];
}

// Procesar flujo...

// Al finalizar, liberar lock
await redis.del(lock_key);
```

**Estado**: ⚠️ **PARCIALMENTE MITIGADO** (pendiente lock explícito)

### 9.4 Falta Referencia al Mensaje Original

**Descripción**: Las respuestas no citan/responden explícitamente al mensaje que las provocó.

**Efecto**: Dificulta seguimiento cuando hay mensajes rápidos.

**Solución con Evolution API**:

```javascript
// Nodo: Enviar mensaje
jsonBody: `
{
  "number": "{{ numero_cuenta }}",
  "text": {{ JSON.stringify(output) }},
  "delay": {{ delay }},
  "quoted": {
    "key": {
      "remoteJid": "{{ numero_cuenta }}",
      "fromMe": false,
      "id": "{{ id_mensaje_original }}"
    }
  }
}
`
```

**Documentación**: [Evolution API Postman](https://www.postman.com/agenciadgcode/evolution-api/collection/nm0wqgt/evolution-api-v2-3)

**Estado**: ❌ **NO IMPLEMENTADO** (futuro)

### 9.5 Detección de Fin de Conversación Imprecisa

**Descripción**: Esperar 60s no garantiza que la conversación terminó; puede haber ventanas de latencia o usuarios que responden tarde.

**Efecto**: Resúmenes generados prematuramente o recursos retenidos.

**Solución Actual**:
✅ Wait 60s + verificación de nuevos mensajes en Redis  

**Mejoras Recomendadas**:

```javascript
// 1. Aumentar tiempo de espera en producción
amount: "={{ $('DataCleaning 1').item.json.is_testing ? 0 : 180 }}" // 3 minutos

// 2. Palabras clave de cierre
const palabras_cierre = ["gracias", "adiós", "adios", "bye", "chao", "listo"];
const mensaje_lower = mensaje_texto.toLowerCase();
const indica_cierre = palabras_cierre.some(p => mensaje_lower.includes(p));

if (indica_cierre) {
  // Espera reducida (30s en lugar de 60s)
  wait_time = 30;
}

// 3. Confirmación explícita
// Si usuario dice "listo", bot pregunta:
// "¿Deseas finalizar o hay algo más en lo que pueda ayudarte?"
```

**Estado**: ⚠️ **FUNCIONAL PERO MEJORABLE**

### 9.6 Tamaño de Payload de Media

**Descripción**: Imágenes grandes en base64 pueden causar timeouts o alto consumo de memoria.

**Recomendación GPT**: Usar URLs temporales en S3/Minio en lugar de base64 directo.

**Recomendación Humana (del documento)**: 
> "No lo veo recomendable, no he visto videos implementando esto y seguramente resulte difícil."

**Solución Actual**: 
✅ Evolution API ya maneja base64 internamente  
✅ Browserless descarga imágenes directamente (no base64)  

**Estado**: ✅ **NO ES PROBLEMA EN LA PRÁCTICA**

### 9.7 Gestión de IDs de Mensaje y Duplicados

**Descripción**: Webhooks pueden llegar duplicados, causando procesamiento múltiple.

**Recomendación GPT**: Guardar `messageId` en Redis para deduplicación.

**Recomendación Humana**:
> "Verificar por timestamp en lugar de remoteJID. Redis ya organiza por numero_cuenta. **No recomendable**, feature mínima."

**Análisis**: En la práctica, Evolution API v2.3.7 no envía webhooks duplicados. Si fuera necesario:

```javascript
// Al recibir mensaje en DataCleaning:
const msg_id = $input.first().json.body.data.key.id;
const dedup_key = `processed:${msg_id}`;

// Verificar si ya fue procesado
const ya_procesado = await redis.get(dedup_key);
if (ya_procesado) {
  console.log(`[INFO] Mensaje ${msg_id} ya procesado. Ignorando.`);
  return [];
}

// Marcar como procesado (TTL 5 minutos)
await redis.set(dedup_key, "1", "EX", 300);

// Continuar con flujo...
```

**Estado**: ⚠️ **NO IMPLEMENTADO** (riesgo bajo)

---

## 10. Mejores Prácticas

### 10.1 Manejo de Errores

**Implementar try-catch en Code Nodes:**

```javascript
try {
  // Lógica principal
  const resultado = procesarDatos($input.first().json);
  return resultado;
} catch (error) {
  console.error(`[ERROR] ${error.message}`);
  // Retornar datos mínimos para evitar crash
  return {
    error: true,
    mensaje: "Error en procesamiento",
    detalle: error.message
  };
}
```

**Validar datos antes de usar:**

```javascript
// ❌ Mal:
const precio = $json.precio * 0.15;

// ✅ Bien:
const precio = parseFloat($json.precio) || 0;
const impuesto = precio > 0 ? precio * 0.15 : 0;
```

### 10.2 Logging y Monitoreo

**Console.log estratégico:**

```javascript
// Inicio de DataCleaning
console.log(`[DataCleaning] Mensaje recibido de ${numero_cuenta}`);

// Antes de llamada a IA
console.log(`[IA] Prompt: ${prompt_dinamico.substring(0, 100)}...`);

// Después de respuesta
console.log(`[IA] Respuesta generada: ${output.length} caracteres`);

// Errores
console.error(`[ERROR] Fallo en análisis de imagen: ${error}`);
```

**Revisar logs de n8n:**

```bash
# Si n8n está local:
cd ~/.n8n/logs
tail -f n8n.log

# Si está en Docker:
docker logs n8n -f
```

### 10.3 Testing

**Usar modo consola antes de producción:**

1. Activar flujo en n8n
2. Abrir **Chat** (botón inferior derecho)
3. Probar escenarios:
   - Texto simple
   - URL de Temu
   - Imágenes (arrastar archivo)
   - Múltiples mensajes seguidos
   - Palabras clave de pago

**Números de prueba en whitelist:**

```javascript
const numeros_admitidos = [
  "593978640544",  // Tu número principal
  "593000000001",  // Número de prueba ficticio
];
```

**Verificar salidas intermedias:**

- Activar "Always Output Data" en nodos clave
- Inspeccionar JSON de cada paso
- Validar transformaciones

### 10.4 Seguridad

**Proteger credenciales:**

```javascript
// ❌ Nunca:
const apikey = "your_super_secret_api_key_here";

// ✅ Siempre usar credenciales de n8n
// Configurar en Credentials → HTTP Header Auth
```

**No commitear archivos sensibles:**

```bash
# Agregar a .gitignore:
.env
*.log
credentials.json
```

**Validar entrada de usuarios:**

```javascript
// Sanitizar URLs
const url_segura = mensaje_texto.replace(/[^\w\s:/.?=&-]/g, "");

// Limitar longitud
const texto_limitado = mensaje_texto.substring(0, 500);
```

### 10.5 Optimización

**Redis TTL adecuados:**

```javascript
// Mensajes temporales: Sin TTL (se borran manualmente)
// Carrito: 1 hora (usuario puede tardar en decidir)
// Memoria conversacional: 1 hora (balancear contexto vs memoria)
```

**Limpiar datos al finalizar:**

```javascript
// Al final del flujo, borrar colas temporales:
await redis.del(numero_cuenta);
await redis.del(`${numero_cuenta}_idmsj`);
// Carrito se auto-elimina por TTL
```

**Limitar contexto de IA:**

```javascript
// No enviar historia completa si no es necesaria
contextWindowLength: 20  // Suficiente para conversaciones típicas

// Para conversaciones técnicas largas:
contextWindowLength: 50  // Aumentar si es necesario
```

---

## 11. Guía de Uso

### 11.1 Para Usuarios Finales (Clientes)

**Cómo cotizar un producto:**

1. **Opción A: Enviar enlace**
   ```
   Usuario: https://temu.com/producto-ejemplo
   Bot: ¡Hola! Soy Estella... [Cotización con precio]
   ```

2. **Opción B: Enviar captura de pantalla**
   ```
   Usuario: [Envía imagen del producto]
   Bot: He analizado tu imagen... [Cotización]
   ```

3. **Opción C: Describir producto**
   ```
   Usuario: Quiero cotizar audífonos bluetooth
   Bot: Con gusto. ¿Podrías enviarme el enlace o una captura?
   ```

**Agregar más productos:**

```
Usuario: Y también quiero estos
Usuario: https://temu.com/otro-producto
Bot: Perfecto. Tu carrito ahora tiene:
     * Audífonos - $29.89
     * Producto 2 - $45.00
     TOTAL: $74.89
```

**Finalizar compra:**

```
Usuario: Listo, quiero comprar
Bot: Excelente. Resumen final:
     * Audífonos - $29.89
     * Producto 2 - $45.00
     TOTAL: $74.89
     
     ¿Cuál es tu método de pago preferido?
```

### 11.2 Para Administradores

**Monitorear conversaciones activas:**

```bash
# Conectarse a Redis
docker exec -it redis_evolution redis-cli

# Ver usuarios en conversación
KEYS *_ia_V3

# Salida ejemplo:
# 1) "593988207600_ia_V3"
# 2) "593997350897_ia_V3"

# Ver carrito de un usuario
GET "carrito:593988207600"
```

**Revisar perfiles en PostgreSQL:**

```bash
# Conectarse a PostgreSQL
docker exec -it postgres_evolution psql -U docker -d evolution_db

# Ver últimos 10 perfiles actualizados
SELECT numero_wp, fecha_actualizacion 
FROM perfil_cliente 
ORDER BY fecha_actualizacion DESC 
LIMIT 10;

# Ver perfil específico
SELECT * FROM perfil_cliente WHERE numero_wp = '593988207600';
```

**Reiniciar servicios:**

```bash
# Reiniciar Evolution API
cd evolution-api
npm run start:prod

# Reiniciar n8n
n8n start

# Reiniciar servicios Docker
docker compose restart postgres_evolution redis_evolution browserless_chrome
```

**Backup de datos:**

```bash
# Backup de PostgreSQL
docker exec postgres_evolution pg_dump -U docker evolution_db > backup_$(date +%Y%m%d).sql

# Backup de Redis (opcional, datos temporales)
docker exec redis_evolution redis-cli SAVE
docker cp redis_evolution:/data/dump.rdb backup_redis_$(date +%Y%m%d).rdb
```

### 11.3 Para Desarrolladores

**Modificar prompts:**

1. Abrir flujo V3 en n8n
2. Localizar nodo `Selector de Prompt`
3. Editar secciones de plantilla:

```javascript
// Plantilla de cotización
prompt_dinamico = `
    ¡Hola! Soy Estella...
    
    **Desglose financiero:**
    * Producto: ${input.producto}
    * Precio Web: $${input.precio_web}
    ...
`;

// Guardar y probar en consola
```

**Agregar nuevo tipo de mensaje:**

```javascript
// En DataCleaning 1, después de detección de Evolution:
else if (tipo_mensaje === "audioMessage") {
  datos.tipo_mensaje = "audio";
  datos.audio_url = $input.first().json.body.data.message.audioMessage.url;
  // Procesar audio con Whisper u otro servicio
}
```

**Integrar con otro servicio:**

```javascript
// Ejemplo: Enviar notificación a Slack cuando hay cotización
// Crear nodo HTTP Request después de "IA Contestadora"
method: "POST"
url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
body: {
  "text": `Nueva cotización de ${nombre_contacto}: $${total_final}`
}
```

---

## 12. Referencias y Recursos

### 12.1 Documentación Oficial

**Evolution API**
- [Documentación v2.3.7](https://doc.evolution-api.com/v1/en/install/nvm)
- [Postman Collection](https://www.postman.com/agenciadgcode/evolution-api/collection/nm0wqgt/evolution-api-v2-3)
- [GitHub Repository](https://github.com/EvolutionAPI/evolution-api)

**WhatsApp Business API**
- [Meta Developer Docs](https://developers.facebook.com/docs/whatsapp)
- [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)

**n8n**
- [Documentación Principal](https://docs.n8n.io/)
- [Langchain Integration](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain/)

**Ollama**
- [Sitio Oficial](https://ollama.com)
- [Documentación de Modelos](https://ollama.com/library)
- [GitHub](https://github.com/ollama/ollama)

**Redis**
- [Comandos Redis](https://redis.io/commands)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)

**PostgreSQL**
- [Documentación Oficial](https://www.postgresql.org/docs/)

**Browserless**
- [Documentación](https://www.browserless.io/docs/)
- [GitHub](https://github.com/browserless/chrome)

### 12.2 Archivos del Proyecto

| Archivo | Descripción |
|---------|-------------|
| `Flujo V3 - Proyecto Estella.json` | Flujo de trabajo principal (producción) |
| `Flujo V2 - Flujo con API Oficial.json` | Versión intermedia (archivado) |
| `Flujo V1 - Prueba con LM Studio.json` | Primera versión (archivado) |
| `docker-compose.yaml` | Configuración de PostgreSQL, Redis, Browserless |
| `perfil_cliente.sql` | Script de creación de tabla |
| `problemas conocidos en evolutional api.md` | Documentación de problemas y soluciones |

### 12.3 Comandos Útiles

**Docker:**
```bash
# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f [servicio]

# Reiniciar servicio
docker compose restart [servicio]

# Detener todo
docker compose down
```

**Redis:**
```bash
# Conectarse
docker exec -it redis_evolution redis-cli

# Ver todas las keys
KEYS *

# Ver contenido de key
GET "clave"   # Para STRING
LRANGE "clave" 0 -1  # Para LIST

# Borrar key
DEL "clave"

# Estadísticas
INFO memory
INFO keyspace
```

**PostgreSQL:**
```bash
# Conectarse
docker exec -it postgres_evolution psql -U docker -d evolution_db

# Listar tablas
\dt

# Describir tabla
\d perfil_cliente

# Query
SELECT * FROM perfil_cliente;

# Salir
\q
```

**Ollama:**
```bash
# Ver modelos instalados
ollama list

# Descargar modelo
ollama pull llama3.1:8b

# Probar modelo
ollama run llama3.1:8b "Hola, ¿cómo funcionas?"

# Eliminar modelo
ollama rm llama3.1:8b
```

**n8n:**
```bash
# Iniciar n8n
n8n start

# Ver versión
n8n --version

# Exportar workflow
n8n export:workflow --id=<ID> --output=backup.json

# Importar workflow
n8n import:workflow --input=backup.json
```

### 12.4 Solución de Problemas Comunes

**Problema: Evolution API no responde**
```bash
# Verificar que esté corriendo
ps aux | grep node

# Ver logs
cd evolution-api
npm run start:prod

# Verificar puerto
curl http://localhost:8080/
```

**Problema: n8n no conecta con Redis**
```bash
# Verificar que Redis esté corriendo
docker ps | grep redis

# Probar conexión
docker exec -it redis_evolution redis-cli PING
# Debe responder: PONG

# Revisar configuración en n8n
# Host: localhost (si n8n local) o redis_evolution (si n8n en Docker)
# Port: 6379
```

**Problema: PostgreSQL rechaza conexiones**
```bash
# Verificar estado
docker exec postgres_evolution pg_isready

# Verificar usuario y contraseña
docker exec -it postgres_evolution psql -U docker -d evolution_db

# Si falla, revisar docker-compose.yaml:
# POSTGRES_USER=docker
# POSTGRES_PASSWORD=password
```

**Problema: Ollama no encuentra modelos**
```bash
# Verificar modelos instalados
ollama list

# Si no aparecen, descargar:
ollama pull llama3.1:8b
ollama pull llama3.2-vision

# Verificar servidor
curl http://localhost:11434/api/tags
```

**Problema: Delays muy largos**
```javascript
// Ajustar fórmula en nodos de "escribiendo" y "enviar mensaje"
// Cambiar divisor de 1.25 a 2.0 para delays más cortos:
delay: {{ max(
  (palabras + puntuacion) / 2.0,  // Era 1.25
  3  // Mínimo 3s en lugar de 5s
) * 1000 }}
```

---

## Apéndices

### Apéndice A: Ejemplo de Conversación Completa

```
[Usuario]: Hola
[Bot]: ¡Hola! Soy Estella, tu asistente de importaciones en Temu. 
       ¿En qué puedo ayudarte hoy?

[Usuario]: Quiero cotizar audífonos
[Bot]: Con gusto. ¿Podrías enviarme el enlace del producto de Temu 
       o una captura de pantalla?

[Usuario]: https://temu.com/audfionos-bluetooth-12345
[Bot]: ¡Perfecto! Estoy analizando el producto...

[Bot]: ¡Hola! Soy Estella, tu asistente de importaciones en Temu.

       **Desglose financiero:**
       
       * **Producto:** Audífonos Bluetooth Inalámbricos Sport
       * **Precio Web:** $25.99
       
       -------------------------------------------
       * **Subtotal Acumulado:** $25.99
       * **Impuesto Estimado:** $3.90
       * **TOTAL FINAL A PAGAR:** $29.89
       
       ¿Desea agregar algún otro producto al carrito o prefiere finalizar la orden?

[Usuario]: Quiero agregar también esto
[Usuario]: [Envía imagen de zapatillas]

[Bot]: He analizado la imagen. Veo que son Zapatillas Running Pro.
       
       **Desglose financiero:**
       
       * **Producto:** Zapatillas Running Pro
       * **Precio Web:** $45.00
       
       -------------------------------------------
       * **Subtotal Acumulado:** $45.00
       * **Impuesto Estimado:** $6.75
       * **TOTAL FINAL A PAGAR:** $51.75
       
       -------------------------------------------
       (SECCIÓN DEL CARRITO)
       * **Productos en carrito:**
           * Audífonos Bluetooth Inalámbricos... - $29.89
           * Zapatillas Running Pro... - $51.75
       * **TOTAL DE LOS PRODUCTOS A PAGAR:** $81.64
       -------------------------------------------
       
       ¿Desea agregar algún otro producto o prefiere finalizar?

[Usuario]: Listo, quiero pagar
[Bot]: ¡Excelente! Aquí tienes el resumen final de tu carrito de compras:
       
           * Audífonos Bluetooth Inalámbricos... - $29.89
           * Zapatillas Running Pro... - $51.75
       
       -------------------------------------------
       * **TOTAL DE LOS PRODUCTOS A PAGAR:** $81.64
       -------------------------------------------
       
       Para proceder con el pago y la importación, por favor confírmame 
       tu método de pago preferido.

[Usuario]: Transferencia bancaria
[Bot]: Perfecto. Te enviaré los datos bancarios por privado para que 
       realices la transferencia. Una vez confirmado el pago, procederemos 
       con la importación. ¿Hay algo más en lo que pueda ayudarte?

[Usuario]: No, gracias
[Bot]: ¡Excelente! Fue un placer ayudarte. Cualquier duda, estoy aquí. 
       ¡Que tengas un excelente día! 👋

[Sistema]: Conversación finalizada. Guardando perfil...
[Sistema]: Perfil actualizado en PostgreSQL.
```

### Apéndice B: Estructura JSON del Carrito

```json
{
  "productos": [
    {
      "nombre": "Audífonos Bluetooth Inalámbricos Sport",
      "precio_web": "25.99",
      "impuesto": "3.90",
      "total": "29.89"
    },
    {
      "nombre": "Zapatillas Running Pro",
      "precio_web": "45.00",
      "impuesto": "6.75",
      "total": "51.75"
    }
  ],
  "cantidad_productos": 2,
  "gran_total": "81.64"
}
```

### Apéndice C: Formato de Perfil en PostgreSQL

```json
{
  "nombre": "Adrián",
  "intereses": ["audífonos", "zapatillas", "deportes", "tecnología"],
  "historial_productos": [
    {
      "nombre": "Audífonos Bluetooth Inalámbricos Sport",
      "precio": 25.99,
      "fecha": "2024-02-18T10:30:00Z"
    },
    {
      "nombre": "Zapatillas Running Pro",
      "precio": 45.00,
      "fecha": "2024-02-18T10:35:00Z"
    }
  ],
  "preferencias": {
    "metodo_pago": "transferencia bancaria",
    "urgencia": "normal",
    "comunicacion": "formal"
  },
  "estadisticas": {
    "total_conversaciones": 3,
    "total_gastado": 150.00,
    "producto_favorito": "tecnología"
  },
  "notas": "Cliente recurrente. Prefiere productos de calidad media-alta. Siempre confirma antes de comprar. Responsive y educado."
}
```

---

## Licencia y Créditos

**Desarrollador Principal**: Adrián  
**Colaboradores**: M. Recalde, M. Rocha, Carlos  
**Proyecto**: Estella - Agente de IA para Importaciones Temu  
**Fecha**: 2024  

**Tecnologías de Código Abierto Utilizadas**:
- n8n (Fair Code License)
- Ollama (MIT License)
- PostgreSQL (PostgreSQL License)
- Redis (BSD License)
- Evolution API (GNU AGPL v3)

---

## Notas Finales

### Advertencia Importante

⚠️ **Evolution API es NO OFICIAL**. WhatsApp puede banear cuentas que la usen. Recomendaciones:

1. **No usar números principales de negocio**
2. **Simular comportamiento humano** (delays, presencia)
3. **Limitar mensajes por día** (< 100 mensajes/día por número)
4. **Tener respaldo con API oficial** (para migración si es necesario)
5. **Monitorear cuenta constantemente**

### Contacto de Soporte

Para dudas sobre este proyecto:
- Revisar documentación completa
- Consultar archivo `problemas conocidos en evolutional api.md`
- Contactar al desarrollador (según lo mencionado en el documento original)

---

**Fin de la Documentación Completa**

*Última actualización: Febrero 18, 2026*
*Versión del flujo: V3 (Proyecto Estella)*  
*Generado con asistencia de GitHub Copilot*
