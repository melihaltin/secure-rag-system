# Docker Deployment Guide - HR Guard

Bu dokümantasyon, HR Guard uygulamasını Docker ile Azure'a (veya başka bir ortama) dağıtmak için adım adım rehber sunar.

## 📋 İçindekiler

- [Gereklilikler](#gereklilikler)
- [Yerel Geliştirme (Docker Compose)](#yerel-geliştirme-docker-compose)
- [Azure Container Registry'ye Upload](#azure-container-registrye-upload)
- [Azure Container Instances'ta Çalıştırma](#azure-container-instancesta-çalıştırma)
- [Azure App Service'te Çalıştırma](#azure-app-servicete-çalıştırma)
- [Ortam Değişkenleri](#ortam-değişkenleri)

## ✅ Gereklilikler

- Docker Desktop kurulu
- Docker Hub veya Azure Container Registry (ACR) hesabı
- Azure CLI kurulu (Azure'a dağıtım için)
- `.env` dosyası oluşturulmuş

## 🚀 Yerel Geliştirme (Docker Compose)

### 1. Environment dosyası oluştur

```bash
cat > .env << EOF
GOOGLE_API_KEY=your-google-api-key-here
LLM_MODEL=gemini-2.5-flash-lite-preview-09-2025
TEMPERATURE=0.3
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

### 2. Docker Compose ile başlat

```bash
docker-compose up --build
```

Uygulama şu adreslerde erişilebilir olacaktır:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

### 3. Durdurmak için

```bash
docker-compose down
```

### 4. Logları görmek için

```bash
# Tüm hizmetlerin logları
docker-compose logs -f

# Sadece backend
docker-compose logs -f backend

# Sadece frontend
docker-compose logs -f frontend
```

## 🔧 Azure Container Registry'ye Upload

### 1. Azure'a giriş yap

```bash
az login
```

### 2. Container Registry oluştur (eğer yoksa)

```bash
az acr create --resource-group myResourceGroup --name hrguardregistry --sku Basic
```

### 3. Login credentials'ı al

```bash
az acr login --name hrguardregistry
```

### 4. Backend image oluştur ve push et

```bash
docker build -f Dockerfile.backend -t hrguardregistry.azurecr.io/hr-guard-backend:latest .

docker push hrguardregistry.azurecr.io/hr-guard-backend:latest
```

### 5. Frontend image oluştur ve push et

```bash
docker build -f Dockerfile.frontend -t hrguardregistry.azurecr.io/hr-guard-frontend:latest .

docker push hrguardregistry.azurecr.io/hr-guard-frontend:latest
```

## 🌐 Azure Container Instances'ta Çalıştırma

### 1. Container Group oluştur

```bash
az container create \
  --resource-group myResourceGroup \
  --name hr-guard \
  --image hrguardregistry.azurecr.io/hr-guard-backend:latest \
  --registry-login-server hrguardregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --port 8000 \
  --environment-variables \
    GOOGLE_API_KEY='your-api-key' \
    LLM_MODEL='gemini-2.5-flash-lite-preview-09-2025' \
    TEMPERATURE='0.3' \
  --cpu 2 \
  --memory 4
```

## 🌐 Azure App Service'te Çalıştırma (Önerilen)

### 1. App Service Plan oluştur

```bash
az appservice plan create \
  --name hr-guard-plan \
  --resource-group myResourceGroup \
  --sku B2 \
  --is-linux
```

### 2. Web App oluştur (Backend)

```bash
az webapp create \
  --resource-group myResourceGroup \
  --plan hr-guard-plan \
  --name hr-guard-api \
  --deployment-container-image-name hrguardregistry.azurecr.io/hr-guard-backend:latest
```

### 3. Container Registry credentials yapılandır

```bash
az webapp config container set \
  --name hr-guard-api \
  --resource-group myResourceGroup \
  --docker-custom-image-name hrguardregistry.azurecr.io/hr-guard-backend:latest \
  --docker-registry-server-url https://hrguardregistry.azurecr.io \
  --docker-registry-server-user <username> \
  --docker-registry-server-password <password>
```

### 4. Ortam değişkenlerini ayarla

```bash
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name hr-guard-api \
  --settings \
    GOOGLE_API_KEY='your-api-key' \
    LLM_MODEL='gemini-2.5-flash-lite-preview-09-2025' \
    TEMPERATURE='0.3' \
    WEBSITES_PORT=8000
```

### 5. Frontend için aynı işlemleri tekrarla

```bash
az webapp create \
  --resource-group myResourceGroup \
  --plan hr-guard-plan \
  --name hr-guard-web \
  --deployment-container-image-name hrguardregistry.azurecr.io/hr-guard-frontend:latest

az webapp config container set \
  --name hr-guard-web \
  --resource-group myResourceGroup \
  --docker-custom-image-name hrguardregistry.azurecr.io/hr-guard-frontend:latest \
  --docker-registry-server-url https://hrguardregistry.azurecr.io \
  --docker-registry-server-user <username> \
  --docker-registry-server-password <password>

az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name hr-guard-web \
  --settings NEXT_PUBLIC_API_URL='https://hr-guard-api.azurewebsites.net'
```

## 🔐 Ortam Değişkenleri

### Gerekli Değişkenler

| Değişken | Açıklama | Örnek |
|----------|----------|-------|
| `GOOGLE_API_KEY` | Google Gemini API Key | `AIzaSy...` |
| `LLM_MODEL` | Kullanılacak LLM modeli | `gemini-2.5-flash-lite-preview-09-2025` |
| `TEMPERATURE` | LLM sıcaklığı (0-1) | `0.3` |
| `NEXT_PUBLIC_API_URL` | Backend API URL'si | `https://hr-guard-api.azurewebsites.net` |

### Azure App Service için

```bash
# Environment variables ayarla
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name hr-guard-api \
  --settings \
    GOOGLE_API_KEY='your-key' \
    LLM_MODEL='gemini-2.5-flash-lite-preview-09-2025' \
    TEMPERATURE='0.3' \
    WEBSITES_PORT=8000
```

## 📊 Monitoring ve Debugging

### Logs görüntüle

```bash
# Azure App Service logs
az webapp log tail --name hr-guard-api --resource-group myResourceGroup

# Container Instances logs
az container logs --name hr-guard --resource-group myResourceGroup
```

### Container durumunu kontrol et

```bash
az container show \
  --name hr-guard \
  --resource-group myResourceGroup \
  --query "containers[].instanceView.currentState"
```

## 🔄 Güncelleme Süreci

### Yeni image push et

```bash
# Backend
docker build -f Dockerfile.backend -t hrguardregistry.azurecr.io/hr-guard-backend:latest .
docker push hrguardregistry.azurecr.io/hr-guard-backend:latest

# App Service'i yeniden başlat
az webapp restart --name hr-guard-api --resource-group myResourceGroup
```

## ⚠️ Üretim Ortamı İçin İpuçları

1. **Secrets Management**: Hassas veriler (API keys) için Azure Key Vault kullanın
2. **Scaling**: Traffic yoğunluğu için App Service Plan'ı upgrade edin
3. **Database**: Persistent data için Azure Database kullanın
4. **CDN**: Frontend için Azure CDN kullanın
5. **Monitoring**: Application Insights ile monitoring yapın
6. **Backup**: Chroma DB ve session verileri için düzenli backup alın

## 🚨 Sorun Giderme

### Container başlamıyor
```bash
# Logs kontrol et
docker logs container-name

# Container içine gir
docker exec -it container-name /bin/bash
```

### Network bağlantısı sorunu
```bash
# Docker network kontrol et
docker network ls
docker network inspect hr-guard-network
```

### Port konflikti
```bash
# Kullanılan portları kontrol et
docker ps

# Farklı port kullan
docker run -p 9000:8000 image-name
```

## 📚 Yararlı Komutlar

```bash
# Docker images listele
docker images

# Container'ları listele
docker ps -a

# Image sil
docker rmi image-name

# Container sil
docker rm container-id

# Docker disk kullanımını kontrol et
docker system df

# Unused resources temizle
docker system prune -a
```

---

**İletişim & Destek**: Sorularınız için Azure belgelerine veya proje dokumentasyonuna başvurun.
