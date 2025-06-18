# Deployment einer Web-Applikation auf einem Debian-Server

## 1. Serverbereitstellung bei Hetzner

### 1.1 Server anlegen und Debian installieren

Zunächst bestellen wir bei **Hetzner Cloud** einen neuen Server. Nach der Bereitstellung verwenden wir das Tool `installimage`, um ein frisches und sauberes Betriebssystem zu installieren, z.B. **Debian 12**.

→ Das stellt sicher, dass keine Altlasten vorhanden sind und wir vollständige Kontrolle (Root-Rechte) über das System haben.

### 1.2 Hostnamen setzen

Ein Hostname wie `api.sitouni.de` wird festgelegt.

→ Dieser Name identifiziert den Server im Netzwerk und spielt später eine wichtige Rolle für:

- SSL-Zertifikate
- DNS-Auflösung
- Webserver-Konfiguration (z. B. Nginx)

---

## 2. Grundkonfiguration des Servers

### 2.1 System aktualisieren

```bash
sudo apt update && sudo apt upgrade -y
```

- `apt update`: Aktualisiert die Paketlisten.
- `apt upgrade`: Installiert alle verfügbaren Updates.
- `-y`: Bestätigt automatisch alle Rückfragen.

→ Dadurch ist das System auf dem aktuellen Stand und eventuelle Sicherheitslücken sind geschlossen.

---

### 2.2 Benutzer anlegen

```bash
sudo adduser willi
sudo adduser fernzugriff
sudo usermod -aG sudo fernzugriff
```

* `adduser willi`: Erstellt einen normalen Benutzeraccount ohne besondere Rechte. Dieser kann z.B. für Anwendungen oder Dienste genutzt werden.
* `adduser fernzugriff`: Erstellt einen Benutzer, der zur Serveradministration vorgesehen ist.
* `usermod -aG sudo fernzugriff`: Fügt `fernzugriff` zur Gruppe `sudo` hinzu. Damit kann dieser Benutzer administrative Befehle ausführen (z.B. `sudo apt install nginx`).

→ Das Prinzip dahinter: Nicht direkt als Root arbeiten, sondern über einen autorisierten, nachvollziehbaren Benutzer mit erhöhten Rechten.

---

### 2.3 SSH-Zugang mit Schlüsselpaar einrichten

```bash
su - fernzugriff
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 AAAA...dein_public_key..." >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

* `su - fernzugriff`: Wechselt in das Benutzerkonto von `fernzugriff`.
* `mkdir -p ~/.ssh`: Erstellt das `.ssh`-Verzeichnis, in dem SSH-Konfigurationsdateien gespeichert werden.
* `chmod 700 ~/.ssh`: Setzt die Berechtigungen so, dass nur der Benutzer selbst darauf zugreifen darf.
* `echo "..." >> ~/.ssh/authorized_keys`: Fügt den öffentlichen SSH-Schlüssel in die Liste erlaubter Zugriffe ein.
* `chmod 600 ~/.ssh/authorized_keys`: Schützt die Datei mit den autorisierten Schlüsseln vor fremdem Zugriff.

→ SSH-Schlüssel sind sicherer als Passwörter. Nur wer den **privaten** Schlüssel besitzt, kann sich einloggen.

---

### 2.4 SSH-Server absichern

In der Datei `/etc/ssh/sshd_config` folgende Einstellungen:

```text
Port 2246
PermitRootLogin no
PasswordAuthentication no
PermitEmptyPasswords no
```

→ Bedeutung:

- Ändert den Standardport (22 → 2246).
- Deaktiviert Root-Logins und Passwort-Logins.
- Erhöht die Systemsicherheit erheblich.

Neustart des SSH-Dienstes:

```bash
sudo systemctl restart ssh
```

Künftiger Login:

```bash
ssh fernzugriff@api.sitouni.de -p 2246
```

---

## 3. Nginx installieren

```bash
sudo apt install nginx -y
```

* `nginx`: Ein sehr effizienter Webserver, der oft als **Reverse Proxy** genutzt wird.
* `-y`: Bestätigt automatisch die Installation.

→ Nginx leitet eingehende Webanfragen an andere Dienste weiter – in unserem Fall an die Flask-App im Docker-Container.

---

## 4. Docker einrichten

### 4.1 Docker installieren

Die folgenden Schritte installieren Docker aus dem offiziellen Docker-Repository – nicht aus den Debian-Standardquellen (diese sind oft veraltet).

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release
```

* Installiert Tools, um sichere Verbindungen aufzubauen (`curl`, `ca-certificates`) und GPG-Schlüssel zu verarbeiten (`gnupg`).

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

* Fügt den GPG-Schlüssel hinzu, um sicherzustellen, dass Docker-Pakete echt und vertrauenswürdig sind.

```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

* Fügt das Docker-Repository zur Paketverwaltung hinzu – abhängig von Architektur (`amd64`, `arm64`) und Codename (z.B. `bookworm` für Debian 12).

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

* Installiert Docker und zugehörige Werkzeuge (Docker Engine, CLI, Container Runtime, Buildx, Compose Plugin).

---

### 4.2 Docker-Berechtigung für `fernzugriff`

```bash
sudo usermod -aG docker fernzugriff
```

→ Fügt den Benutzer der Gruppe `docker` hinzu. Damit kann `fernzugriff` Docker-Befehle **ohne `sudo`** ausführen. Erst nach Ab- und Anmelden wird diese Änderung aktiv.

---

## 5. Projekt klonen und starten

```bash
sudo apt install git -y
cd /var/www/
git clone https://github.com/ilsit/legendary-list.git
cd legendary-list
```

* `git`: Versionierungstool, um Projektquellen herunterzuladen.
* `clone`: Lädt das Repository.
* `cd /var/www`: Hier befinden sich üblicherweise Webanwendungen – gute Praxis für Struktur.
* `cd legendary-list`: Wechselt ins geklonte Projekt.

```bash
docker build -t todo_api_list .
```

* Erstellt ein **Docker-Image** mit dem Namen `todo_api_list` aus dem aktuellen Verzeichnis (`.`).
* Dabei wird das `Dockerfile` im Projekt verwendet.

```bash
docker run --restart=always -p 5000:5000 todo_api_list
```

* Startet den Container aus dem Image.
* `--restart=always`: Startet den Container nach einem Reboot automatisch neu.
* `-p 5000:5000`: Verbindet den Host-Port 5000 mit dem Container-Port 5000 – die API ist somit extern erreichbar.

---

## 6. Nginx vorbereiten (HTTP + Zertifikatschallenge)

```nginx
server {
    listen 80;
    server_name api.sitouni.de;

    error_log /var/log/nginx/api_error.log;
    access_log /var/log/nginx/api_access.log;

    location /.well-known/acme-challenge/ {
        root /var/www/public;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}
```

→ Diese Konfiguration erlaubt es Let's Encrypt, über HTTP (`Port 80`) die **Domain zu validieren**.

* `/.well-known/acme-challenge/`: Challenge-Verzeichnis für Let's Encrypt.
* `return 301`: Leitet alle anderen Anfragen auf HTTPS um – sorgt dafür, dass niemand unverschlüsselt kommuniziert.

Dann:

```bash
sudo ln -s /etc/nginx/sites-available/api.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

* Verlinkt die Konfigurationsdatei.
* `nginx -t`: Testet die Syntax.
* `reload`: Lädt neue Konfiguration ohne Neustart.

---

## 7. SSL-Zertifikat mit Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d api.sitouni.de
```

* `certbot`: Tool zur Ausstellung kostenloser TLS-Zertifikate.
* `--nginx`: Certbot konfiguriert Nginx automatisch.
* `-d`: Gibt die Domain an.

→ Nach dem Befehl wird automatisch ein gültiges Zertifikat bezogen und eingebunden.

---

## 8. HTTPS-Serverblock mit Reverse Proxy

```nginx
server {
    listen 443 ssl;
    server_name api.sitouni.de;

    ssl_certificate /etc/letsencrypt/live/api.sitouni.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.sitouni.de/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location ~ /\.ht {
        deny all;
    }
}
```

→ Dieser Block:

* Hört auf HTTPS (Port 443).
* Nutzt Zertifikate von Let's Encrypt.
* Leitet Anfragen an die lokale Anwendung (Docker) weiter.
* Leitet Header wie IP-Adresse und Protokoll an die App weiter.
* Blockiert `.ht`-Dateien (Sicherheitsmaßnahme).

---

## 9. Firewall konfigurieren (empfohlen)

Zur Absicherung des Servers verwenden wir **UFW (Uncomplicated Firewall)** – ein einfaches Tool zur Verwaltung von Firewall-Regeln.

Zuerst installieren und aktivieren wir UFW, dann erlauben wir gezielt den Zugriff auf bestimmte Ports:

```bash
sudo apt install ufw -y

sudo ufw allow 2246/tcp    # SSH (nicht Standardport 22!)
sudo ufw allow 80/tcp      # HTTP (für automatische Zertifikatserstellung via Let's Encrypt)
sudo ufw allow 443/tcp     # HTTPS (für sicheren Zugriff per Webbrowser)
sudo ufw allow 5000/tcp    # API (direkter Zugriff auf die Anwendung, falls gewünscht)
sudo ufw enable
```

### Erklärung der freigegebenen Ports:

- **Port 2246**: Unser SSH-Zugang läuft nicht über den Standardport 22, sondern über 2246 – das erschwert automatisierte Angriffe.
- **Port 80 (HTTP)**: Wird benötigt, damit Let's Encrypt Zertifikate über eine HTTP-Challenge ausstellen kann.
- **Port 443 (HTTPS)**: Für den normalen verschlüsselten Zugriff auf die Web-Anwendung über den Browser.
- **Port 5000 (API)**: Die Docker-Anwendung hört direkt auf diesem Port. Wird über Nginx weitergeleitet, kann aber auch explizit geschützt oder sogar geschlossen werden, wenn nur Nginx Zugriff haben soll.

→ UFW sorgt dafür, dass **nur notwendiger Netzwerkverkehr erlaubt ist** – alles andere wird standardmäßig blockiert. Damit erhöhen wir die Sicherheit des Systems erheblich.

---

## Fazit

Der Server `api.sitouni.de` ist nun:

- ✅ Sicherer SSH-Zugang über eigenen Port und SSH-Key
- ✅ Docker-Container für die Flask-API läuft stabil
- ✅ HTTPS-Zertifikat von Let's Encrypt aktiv
- ✅ Reverse Proxy über Nginx sorgt für sicheren Zugriff
- ✅ UFW-Firewall schützt offene Ports
