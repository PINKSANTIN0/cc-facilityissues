# 🏗️ Laporan Kerusakan Fasilitas Kampus
### Facility Issue Reporting System

> **Telkom University — Cloud Computing UTS**  
> **Studi Kasus 8:** Laporan Kerusakan Fasilitas Kampus

---

## 👥 Anggota Kelompok

| No | Nama Lengkap | NIM |
|----|--------------|-----|
| 1  | Patar Idaon Situmorang | 101012300016 |
| 2  | Naufal Pratama | 101012300039 |
| 3  | Keyzard Nashbun Manangkali | 101012300367 |

---

## 📋 Deskripsi Proyek

Aplikasi web fullstack sederhana untuk **pelaporan kerusakan fasilitas kampus** (AC mati, proyektor rusak, meja/kursi rusak, dll). Mahasiswa dapat mengirimkan aduan kerusakan, melihat daftar aduan, dan menghapus aduan yang sudah selesai ditangani.

**Fitur API:**
- `GET /reports` — Menampilkan daftar seluruh aduan kerusakan
- `POST /reports` — Mengirim aduan kerusakan baru
- `DELETE /reports?index=X` — Menghapus aduan yang sudah selesai/terselesaikan

**Kategori Kerusakan:** AC Mati, Proyektor Rusak, Meja/Kursi Rusak, Listrik/Stop Kontak, Kebersihan, Lainnya.

---

## 🏛️ Diagram Arsitektur Docker

```
┌───────────────────────────────────────────────────────────────────┐
│                    HOST MACHINE (Docker Host)                     │
│                                                                   │
│  ┌─────────────────────── app-net (Custom Bridge Network) ──────┐ │
│  │                                                               │ │
│  │  ┌──────────────────────┐      ┌──────────────────────────┐  │ │
│  │  │   frontend (Nginx)   │      │   backend (Python API)   │  │ │
│  │  │   ─────────────────  │      │   ────────────────────   │  │ │
│  │  │   Container:         │ DNS  │   Container:             │  │ │
│  │  │   facility-frontend  │─────▶│   facility-backend       │  │ │
│  │  │                      │      │                          │  │ │
│  │  │   Port: 8080:80      │      │   Port: 5000:5000        │  │ │
│  │  │                      │      │                          │  │ │
│  │  │   📁 Bind Mount:     │      │   📦 Named Volume:       │  │ │
│  │  │   ./frontend ──▶     │      │   facility-data ──▶      │  │ │
│  │  │   /usr/share/nginx/  │      │   /var/lib/backend_data/ │  │ │
│  │  │   html (READ-ONLY)   │      │   facility_reports.json  │  │ │
│  │  └──────────────────────┘      └──────────────────────────┘  │ │
│  │                                                               │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Jenkins CI/CD (GitHub Webhook)                 │   │
│  │  ┌──────────┐ ┌──────────┐ ┌───────┐ ┌────────┐ ┌───────┐ │   │
│  │  │ Checkout │▶│ Syntax   │▶│ Build │▶│ Deploy │▶│Health │ │   │
│  │  │          │ │ Check    │ │ Image │ │        │ │ Check │ │   │
│  │  └──────────┘ └──────────┘ └───────┘ └────────┘ └───────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘

LEGEND:
  ──▶  Bind Mount (live file sync, no rebuild needed)
  ──▶  Named Volume (persistent data, survives container removal)
  DNS  Docker internal DNS resolution via service name
```

---

## 🗂️ Struktur File Proyek

```
facility-issue-reporting/
├── app.py                  # Backend Python REST API
├── Dockerfile              # Docker image untuk backend
├── docker-compose.yml      # Orchestration seluruh stack
├── nginx.conf              # Konfigurasi Nginx (reverse proxy)
├── Jenkinsfile             # Declarative CI/CD Pipeline
├── jenkins/
│   └── Dockerfile          # Image Jenkins + Docker CLI + Python 3
├── README.md               # Dokumentasi proyek (file ini)
└── frontend/
    └── index.html          # Frontend UI (HTML & Vanilla JS)
```

---

## 🚀 Langkah Instalasi & Menjalankan Lokal

### Prasyarat
- **Docker** & **Docker Compose** terinstal
- **Git** terinstal
- **Jenkins** terinstal (untuk CI/CD)

### 1. Clone Repository
```bash
git clone https://github.com/PINKSANTIN0/cc-facilityissues.git
cd cc-facilityissues
```

### 2. Jalankan dengan Docker Compose
```bash
# Build & jalankan seluruh stack
docker compose up -d --build

# Cek status kontainer
docker ps
```

### 3. Akses Aplikasi
| Service  | URL |
|----------|-----|
| Frontend (UI) | [http://localhost:8080](http://localhost:8080) |
| Backend (API) | [http://localhost:5000/reports](http://localhost:5000/reports) |
| Health Check  | [http://localhost:5000/health](http://localhost:5000/health) |

### 4. Testing API Manual (cURL)
```bash
# GET - Lihat semua aduan
curl http://localhost:5000/reports

# POST - Kirim aduan baru
curl -X POST http://localhost:5000/reports \
  -H "Content-Type: application/json" \
  -d '{"location":"GKU Lt.3 R.301","category":"AC Mati","description":"AC tidak dingin sejak pagi","reporter":"Budi Santoso"}'

# DELETE - Hapus aduan index ke-0
curl -X DELETE "http://localhost:5000/reports?index=0"
```

### 5. Simulasi Data Immunity (Named Volume)
```bash
# Tambah data terlebih dahulu via UI atau cURL POST

# Hapus paksa kontainer backend
docker rm -f facility-backend

# Jalankan ulang
docker compose up -d

# Verifikasi data masih ada
curl http://localhost:5000/reports
# ✅ Data tetap utuh karena disimpan di Named Volume 'facility-data'
```

### 6. Stop & Cleanup
```bash
# Stop semua kontainer
docker compose down

# Stop & hapus volume (HATI-HATI: data akan hilang!)
docker compose down -v
```

---

## 🔧 Konfigurasi Jenkins CI/CD

### 1. Jalankan Jenkins (di dalam kontainer Docker)

Jenkins berjalan sebagai kontainer dan mengendalikan Docker milik host lewat `docker.sock`.
Ada dua hal yang perlu disiapkan karena itu:

- **Image khusus** ([jenkins/Dockerfile](jenkins/Dockerfile)): image Jenkins resmi tidak punya `docker`, `docker compose`, dan `python3` yang dipakai pipeline. Image ini juga langsung memasang plugin Jenkins yang dibutuhkan.
- **Folder deploy di host**: bind mount selalu dibaca Docker dari sisi *host*, bukan dari workspace di dalam kontainer Jenkins. Pipeline menyalin `frontend/` dan `nginx.conf` ke folder ini, lalu Nginx melakukan bind mount ke folder tersebut.

```bash
# Build image Jenkins
docker build -t jenkins-facility:lts jenkins/
```

Jalankan Jenkins (contoh Windows / Docker Desktop, sesuaikan path folder deploy):

```bash
docker run -d --name jenkins --restart unless-stopped -p 9090:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock -v C:/Users/patar/facility-deploy:/deploy -e HOST_DEPLOY_DIR=C:/Users/patar/facility-deploy jenkins-facility:lts
```

| Opsi | Fungsi |
|------|--------|
| `-v jenkins_home:/var/jenkins_home` | Named Volume untuk data & konfigurasi Jenkins |
| `-v /var/run/docker.sock:...` | Jenkins memakai Docker daemon milik host |
| `-v <folder-host>:/deploy` | Folder deploy host, terlihat sebagai `/deploy` di dalam Jenkins |
| `-e HOST_DEPLOY_DIR=<folder-host>` | Path folder yang sama dilihat dari host, dipakai `docker-compose.yml` untuk bind mount |

Jenkins dapat diakses di [http://localhost:9090](http://localhost:9090). Password awal:

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Plugin yang dibutuhkan pipeline (**Pipeline**, **Git**, **GitHub**, **Pipeline Stage View**) sudah terpasang otomatis lewat image, jadi pada wizard awal cukup masukkan password di atas lalu buat user admin.

### 2. Buat Personal Access Token (PAT) GitHub
1. Login GitHub → **Settings** → **Developer settings**
2. **Personal access tokens** → **Tokens (classic)** → **Generate new token**
3. Note: `Jenkins CI/CD UTS Token`, Expiration: **90 days**
4. Centang: ☑️ `repo` dan ☑️ `admin:repo_hook`
5. **Generate token** → Salin token (`ghp_xxxx...`)

### 3. Tambah Credentials di Jenkins
1. **Manage Jenkins** → **Credentials** → **Global**
2. **Add Credentials** → Kind: **Username with password**
   - Username: `<GitHub username>`
   - Password: `<PAT token>`
   - ID: `github-credentials`

### 4. Buat Pipeline Job
1. **New Item** → nama: `facility-report-pipeline` → tipe: **Pipeline**
2. **Build Triggers**: ☑️ *GitHub hook trigger for GITScm polling*
3. **Pipeline** → Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/PINKSANTIN0/cc-facilityissues.git`
   - Credentials: pilih yang sudah ditambahkan
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`

### 5. Setup GitHub Webhook

GitHub harus bisa menjangkau Jenkins dari internet. Jika Jenkins berjalan di laptop, buka tunnel dengan [ngrok](https://ngrok.com/) terlebih dahulu:

```bash
ngrok http 9090
```

Salin URL `https://xxxx.ngrok-free.app` yang muncul, lalu:

1. Di repository GitHub → **Settings** → **Webhooks** → **Add webhook**
2. Payload URL: `https://xxxx.ngrok-free.app/github-webhook/` (garis miring di akhir wajib ada)
3. Content type: `application/json`
4. Events: **Just the push event**
5. ☑️ Active → **Add webhook** (pastikan muncul centang hijau pada *Recent Deliveries*)

> Jalankan **Build Now** satu kali secara manual setelah job dibuat, agar Jenkins mengenali repository dan trigger webhook aktif.

### 6. Testing CI/CD Pipeline
```bash
# Lakukan perubahan kode
echo "<!-- updated -->" >> frontend/index.html

# Push ke GitHub
git add .
git commit -m "trigger CI/CD pipeline"
git push origin main

# Jenkins akan otomatis ter-trigger via Webhook!
```

---

## 📐 Teknologi yang Digunakan

| Komponen | Teknologi |
|----------|-----------|
| Backend API | Python 3.11 (http.server, tanpa framework) |
| Frontend UI | HTML5, CSS3, Vanilla JavaScript (fetch API) |
| Web Server | Nginx Alpine |
| Containerization | Docker, Docker Compose |
| Data Storage | JSON file di Docker Named Volume |
| Networking | Docker Custom Bridge Network (`app-net`) |
| CI/CD | Jenkins (Declarative Pipeline) + GitHub Webhook |
| Version Control | Git & GitHub |

---

## 📌 Catatan Penting

- **Named Volume (`facility-data`)**: Menyimpan `facility_reports.json` — data tetap aman meskipun kontainer dihapus (`docker rm -f`).
- **Bind Mount (`./frontend`)**: Frontend HTML di-mount read-only ke Nginx, perubahan UI langsung terlihat tanpa rebuild image. Saat di-deploy oleh Jenkins, sumber bind mount adalah folder deploy di host (`HOST_DEPLOY_DIR`), yang diisi pipeline pada stage *Automated Deployment*.
- **Custom Bridge Network (`app-net`)**: Frontend dan Backend berkomunikasi via DNS Docker (service name `backend`), terisolasi dari jaringan luar.
- **Health Check pipeline**: Jenkins mengakses aplikasi lewat `host.docker.internal` (bukan `localhost`, karena Jenkins ada di dalam kontainer), menguji POST → GET → DELETE, dan hanya menghapus data uji miliknya sendiri.
- **Nginx Reverse Proxy**: Request ke `/api/reports` di-proxy ke `http://backend:5000/reports`, sehingga frontend dan backend berjalan di origin yang sama (menghindari CORS).

---

## 🎥 Video Demo

> Video demo berdurasi 5–8 menit yang mencakup:
> 1. Demo UI & API (tambah, lihat, hapus aduan)
> 2. Simulasi Data Immunity (hapus kontainer backend, data tetap ada)
> 3. Simulasi CI/CD (git push → Jenkins auto-trigger → auto-deploy)

📎 *Link video: (tempel link video demo di sini)*

---

*Dibuat untuk memenuhi Tugas UTS Mata Kuliah Cloud Computing — Telkom University © 2026*
