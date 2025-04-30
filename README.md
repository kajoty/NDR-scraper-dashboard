# 📻 NDR Scraper Dashboard

Ein interaktives Dashboard zur Visualisierung von Radiosender-Playlists (z. B. NDR 2, NDR 90.3), die regelmäßig durch einen separaten Scraper in eine PostgreSQL-Datenbank gespeichert werden.

> 🎧 **Inspiriert von „RadioMining – Die musikalische Vermessung des Äthers“ (38C3)**  
> [PDF-Link zur Präsentation](https://www.anginf.de/wp-content/uploads/RadioMining-38c3.pdf)

---

## 🧠 Hintergrund & Ziel

Ziel des Projekts ist es, Sendeverhalten öffentlich-rechtlicher Radiosender sichtbar zu machen. Basierend auf der automatischen Sammlung von Playlist-Daten werden Analysen möglich wie:

- Wiederholungen im Programm
- Häufig gespielte Künstler:innen & Titel
- Zeitliche Muster (Uhrzeit, Wochentage, Jahreszeiten)
- Unterschiede zwischen verschiedenen Sendern

Das Projekt richtet sich an Musikliebhaber:innen, Medienanalyst:innen oder alle, die das Radioprogramm datengetrieben untersuchen möchten.

---

## 🎯 Features

- 🔍 **Live-Datenanzeige** direkt aus der PostgreSQL-Datenbank
- 🎛️ **Filter** nach Sender & Datum
- 📄 **CSV-Export** der angezeigten Daten
- 📊 **Saisonale Auswertungen**:
  - Monatlich
  - Jahreszeitlich
  - Wochentag vs. Wochenende
  - Tageszeit-Analyse (Morgen vs. Abend)
- ⭐ **Top 10** Künstler & Titel
- 🐳 **Deployment via Docker** & einfache Verwaltung via Portainer

---

## 🚀 Setup & Deployment (Docker)

### 1. Projekt klonen

```bash
git clone https://github.com/kajoty/NDR-scraper-dashboard.git
cd NDR-scraper-dashboard
```

### 2. `.env` Datei erstellen

Erstelle eine `.env`-Datei im Projektverzeichnis mit folgendem Inhalt:

```env
PG_HOST=192.168.178.100
PG_PORT=5432
PG_USER=admin
PG_PASSWORD=admin
PG_DB=playlist
```

> ⚠️ Diese Zugangsdaten müssen zu deiner PostgreSQL-Instanz passen.  
> Die Tabelle `ndr_playlist` muss bereits vorhanden sein (wird vom Scraper gefüllt).

---

### 3. Dashboard starten

```bash
docker compose up --build -d
```

📍 Danach ist das Dashboard erreichbar unter:

```
http://localhost:80
```

---

## 📂 Projektstruktur

```text
dashboard/
├── app.py             # Hauptlogik des Dashboards (Streamlit)
├── Dockerfile         # Container-Buildfile
├── requirements.txt   # Python-Abhängigkeiten
docker-compose.yml     # Multi-Container-Konfiguration
.env                   # Zugangsdaten (nicht im Repo enthalten)
```

---

## 🛠 Voraussetzungen

- Docker + Docker Compose
- Eine laufende PostgreSQL-Datenbank mit einer Tabelle `ndr_playlist`
- Separater Scraper (nicht Teil dieses Repositories)

---

## 🔍 Datenbankstruktur (Beispiel)

Die Tabelle `ndr_playlist` sollte mindestens folgende Spalten enthalten:

| Spalte         | Typ         | Beschreibung                         |
|----------------|-------------|--------------------------------------|
| `timestamp`    | TIMESTAMP   | Zeitpunkt der Ausstrahlung           |
| `artist`       | TEXT        | Interpret                            |
| `title`        | TEXT        | Songtitel                            |
| `station`      | TEXT        | Radiosender                          |

---

## 🧪 Beispielanalyse (Ideen)

- 🎼 Wie oft wird „Ed Sheeran“ im Monat gespielt?
- 🕒 Gibt es Wiederholungen zur gleichen Uhrzeit?
- 📆 Spielt NDR 2 am Wochenende andere Musik als unter der Woche?
- 🔁 Wie hoch ist die Wiederholungsrate innerhalb eines Tages?

---

## 📄 Lizenz

MIT License – feel free to fork, use & improve.  
Made with ❤️ by [kajoty](https://github.com/kajoty)

---

## 📎 Verwandte Projekte & Links

- [RadioMining – 38C3 Präsentation (PDF)](https://www.anginf.de/wp-content/uploads/RadioMining-38c3.pdf)
- [Streamlit – Open Source App Framework](https://streamlit.io/)
- [PostgreSQL – Datenbank-System](https://www.postgresql.org/)

---

## 🤖 KI-Hinweis

Dieses Projekt wurde mit Unterstützung von [ChatGPT](https://openai.com/chatgpt) erstellt, um Struktur, Klarheit und Dokumentation zu verbessern.
