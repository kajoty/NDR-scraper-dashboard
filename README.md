# 📻 NDR Scraper Dashboard

Ein interaktives Dashboard zur Visualisierung von Radiosender-Playlists (z. B. NDR 2, NDR 90.3, etc.), die durch einen separaten Scraper in eine PostgreSQL-Datenbank gespeichert werden.

---

## 🎯 Features

- Live-Datenanzeige direkt aus der Datenbank
- Filter nach Sender und Datum
- CSV-Export der Ergebnisse
- Saisonale Auswertung:
  - 📅 Monatlich
  - 🌞 Jahreszeiten
  - 🗓️ Wochentag vs. Wochenende
  - ⏰ Uhrzeitverlauf (Morgen vs. Abend)
- Top 10 Künstler & Titel
- Deployment via Docker & Portainer

---

## 🚀 Setup & Deployment (Docker)

### 1. Projekt klonen

```bash
git clone https://github.com/kajoty/NDR-scraper-dashboard.git
cd NDR-scraper-dashboard
```

### 2. `.env` Datei erstellen

```env
PG_HOST=192.168.178.100
PG_PORT=5432
PG_USER=admin
PG_PASSWORD=admin
PG_DB=playlist
```

> Diese Datei enthält die Zugangsdaten zur PostgreSQL-Datenbank.

---

### 3. Container starten

```bash
docker compose up --build -d
```

Das Dashboard ist anschließend erreichbar unter:

```
http://localhost:80
```

---

## 📂 Projektstruktur

```
dashboard/
├── app.py
├── Dockerfile
├── requirements.txt
docker-compose.yml
.env
```

---

## 🛠 Anforderungen

- Docker + Docker Compose
- PostgreSQL-Datenbank mit Tabelle `ndr_playlist`
- Scraper (läuft getrennt, nicht Teil dieses Repos)

---

## 📄 Lizenz

MIT License – feel free to fork, use & improve.  
Made with ❤️ by [kajoty](https://github.com/kajoty)
