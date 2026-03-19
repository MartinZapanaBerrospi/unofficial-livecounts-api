# 🎶 Unofficial Livecounts.io API - Alto Rendimiento

**Una librería de alto rendimiento para extraer estadísticas en tiempo real de Livecounts.io. Soporta TikTok, YouTube, Twitter y Twitch de forma síncrona y asíncrona.**

Esta versión ha sido optimizada para ofrecer la máxima velocidad posible mediante el uso de `httpx` (networking moderno) y `msgspec` (serialización de datos ultra-rápida).

## ✨ Características Principales

- **Velocidad Extrema**: Hasta 3.3x más rápido gracias a la concurrencia asíncrona y parsing eficiente.
- **Soporte Todo-en-Uno**: TikTok, YouTube, Twitter y Twitch en una sola librería.
- **Multimodo**: Soporte nativo para programación síncrona (`api.tiktok.find_user`) y asíncrona (`api.tiktok.find_user_async`).
- **Minimalista**: Todo el núcleo funcional se encuentra en un solo archivo profesional (`unofficial_livecounts_api.py`).
- **Manejo de Sesiones**: Reutilización de clientes HTTP para minimizar la latencia de conexión.

---

## 🚀 Instalación y Preparación

### 1. Requisitos
- Python 3.10 o superior.
- Dependencias indicadas en `requirements.txt`.

### 2. Configuración del Entorno
Se recomienda usar un entorno virtual:
```bash
python -m venv venv
.\venv\Scripts\activate  # En Windows
pip install -r requirements.txt
```

---

## 🕵️ Guía de Uso

### Importación
```python
from unofficial_livecounts_api import api
```

### 1. TikTok API
Ofrece búsqueda de usuarios, métricas detalladas y próximamente videos.

```python
# Síncrono
usuarios = api.tiktok.find_user("best")
metricas = api.tiktok.fetch_user_metrics("userId_ejemplo")

# Asíncrono (Recomendado para rendimiento)
usuarios = await api.tiktok.find_user_async("best")
metricas = await api.tiktok.fetch_user_metrics_async("userId_ejemplo")
```

### 2. YouTube API
Permite buscar canales y obtener sus suscriptores y métricas en vivo.

```python
# Buscar canales
canales = await api.youtube.find_channel_async("mrbeast")

# Obtener métricas
stats = await api.youtube.fetch_channel_metrics_async("channelId")
print(f"Subscriptores: {stats['subscribers']}")
```

### 3. Twitter y Twitch
Funcionamiento similar para seguidores en tiempo real.

```python
# Twitter
twitter_user = await api.twitter.find_user_async("jack")
t_metrics = await api.twitter.fetch_user_metrics_async("jack")

# Twitch
twitch_users = await api.twitch.find_user_async("jack")
tw_metrics = await api.twitch.fetch_user_metrics_async("jack")
```

---

## ⚡ Rendimiento y Concurrencia
Para realizar múltiples consultas a la vez, utiliza el modo asíncrono. Esto permite que las peticiones se realicen en paralelo en lugar de secuencialmente.

```python
import asyncio
from unofficial_livecounts_api import api

async def main():
    canales = ["mrbeast", "pewdiepie", "tseries"]
    tareas = [api.youtube.find_channel_async(c) for c in canales]
    resultados = await asyncio.gather(*tareas)
    # ... procesar resultados ...

asyncio.run(main())
```

---

## 📛 Aviso Legal
Este proyecto tiene fines educacionales y de investigación de seguridad. El uso indebido para fines maliciosos no está permitido y los desarrolladores no se hacen responsables de actividades ilegales realizadas con esta herramienta.
