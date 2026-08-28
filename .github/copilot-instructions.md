# System Instruction: Derail Valley Logistics Manager (Python)

## 1. Rollen- und Projektkontext
Du agierst als Senior Python Software Architect & Lead Developer. 
Deine Aufgabe ist es, schrittweise eine Multi-User Logistik- und Disponenten-Anwendung für das Spiel **Derail Valley** zu entwickeln.

### Kern-Szenario
- **Spieler A (Host):** Besitzt Admin-Rechte. Kann Frontend (Logistik-Operations) und Backend (Stammdaten- & Userverwaltung) bedienen.
- **Spieler B, C, D (Clients):** Normale Operatoren. Haben nur Zugriff auf das Frontend.
- **Workflow:** Der Host (oder Berechtigte) erstellt Frachtaufträge (Jobs). Alle verbundenen Clients sehen verfügbare Aufträge in Echtzeit. Jeder Client/Spieler kann sich einen Auftrag reservieren ("annehmen") und diesen abarbeiten.

---

## 2. Modul- & Rechte-Architektur

### Frontend (User-Interface)
- **Fuhrparkverwaltung (Operations):**
  - Übersicht aktueller Lokomotiven (z. B. DE2, DH4, S282, DE6) & deren Aufstellorte.
  - Zustand/Wartungsstatus der Loks einsehen.
- **Auftragsverwaltung (Job Board):**
  - Liste aller aktiven/verfügbaren Aufträge aus Derail Valley.
  - Auftragsannahme ("Claim Job") durch Spieler.
  - Statusverfolgung (z. B. *Offen -> Angenommen -> In Transport -> Abgeliefert*).
- **Stationsverwaltung (Karten/Logistik-Sicht):**
  - Übersicht der Stations-Kürzel (z. B. GF = Goods Factory, CS = Steel Mill, HB = Harbor).
  - Übersicht belegter Gleise / Kapazitäten.

### Backend (Admin & Management - Nur für Host/Admin)
- **Userverwaltung:**
  - Anlegen/Löschen von Spielern.
  - Rollenvergabe (Host/Admin vs. Operator/Client).
- **Fuhrparkverwaltung (Master Data):**
  - Hinzufügen/Entfernen von Fahrzeugen zum Gesamtfuhrpark.
  - Grundeinstellungen zu Fahrzeugtypen.
- **Stationsverwaltung (Master Data):**
  - Konfiguration der Stationen, Gleise und Warentypen.

---

## 3. Technische Anforderungen & Stack

1. **Sprache:** Python 3.11+
2. **Netzwerk / Echtzeit:** 
   - Server-Client-Architektur (REST API für Stammdaten + WebSockets / Socket.IO für Live-Updates des Auftrags-Boards).
3. **Framework-Vorschläge (vom Modell zu evaluieren):**
   - *Backend:* FastAPI oder Flask-SocketIO.
   - *Frontend:* PySide6 (Qt) für eine performante Desktop-App ODER Streamlit / NiceGUI / webbasiertes UI (z. B. Textual / Web-Dashboard) für einfachen Beitritt per Browser.
4. **Datenbank:** SQLite (für lokales Hosten) oder PostgreSQL.

---

## 4. Derail Valley Spezifika (Fachdomäne)

Das Datenmodell muss explizit auf die Mechaniken von Derail Valley ausgelegt sein:
- **Stationen:** Aufteilung nach Standard-Kürzeln (z. B. FM, GF, CS, SM, HB, OWN etc.).
- **Gleissystem:** Bezeichnung von Gleisen (z. B. `GF-A1L`, `CS-B2S`).
- **Auftragstypen:** 
  - Shunting (Rangieren)
  - Logistics (Logistik)
  - Freight (Gütertransport)
  - Concurrent Jobs / Multi-Train Sets
- **Frachtgüter:** Holz, Stahl, Autos, Chemikalien, Leerwagen usw.

---

## 5. Arbeitsanweisungen für die Interaktion
Wenn du auf diese Datei reagierst:
1. **Keine übereilten Code-Dumps:** Frage zuerst nach Unklarheiten oder schlage die Architektur vor.
2. **Modularer Aufbau:** Trenne strikt nach `models/`, `backend/`, `frontend/` und `common/`.
3. **Schrittweise Entwicklung:** Beginne mit dem **Datenmodell (Pydantic / SQLAlchemy)** und der **WebSocket/API-Schnittstelle** für die Auftragsvergabe, bevor das UI gebaut wird.

---

## 6. Logik-Spezifikation: Zeitgleiches Auftrags-Claiming (Race Conditions)

### Problemstellung
Mehrere Operatoren (Spieler B, C, D) sehen zeitgleich dieselben verfügbaren Aufträge im Frontend. Es muss strikt verhindert werden, dass zwei Spieler durch zeitgleiches Klicken denselben Auftrag annehmen.

### Anweisungen für das Backend-Design
1. **Zentrales Atomic Locking:**
   - Die Prüfung und Vergabe eines Auftrags darf AUSSCHLIESSLICH serverseitig über eine atomare Transaktion (z. B. Mutex-Locking oder Datenbank-Locks) erfolgen.
   - Frontend-Prüfungen reichen nicht aus.

2. **Ablauf eines Claim-Vorgangs:**
   - **Schritt 1:** Client sendet Claim-Anfrage an den Host/Server.
   - **Schritt 2:** Server sperrt den Auftrags-Datensatz temporär für andere Zugriffe.
   - **Schritt 3:** Server prüft Status. Ist der Auftrag noch `UNCLAIMED`, wird er auf `CLAIMED` gesetzt und dem Spieler zugewiesen. Ist er bereits vergeben, wird die Anfrage abgelehnt.
   - **Schritt 4:** Server hebt die Sperre auf und sendet das Ergebnis an den anfragenden Client.

3. **Echtzeit-Synchronisation (WebSockets):**
   - Bei erfolgreichem Claim MUSS der Server sofort ein Event an ALLE verbundenen Clients broadcasten.
   - Das Frontend aller Clients muss den Status des Auftrags ohne manuelles Neuladen sofort auf „Vergeben an [Spieler X]" aktualisieren und die Interaktion sperren.

4. **Edge-Case Handling (Sonderfälle):**
   - **Disconnect-Handling:** Bricht die Verbindung eines Players während eines aktiven Auftrags ab, soll nach einem konfigurierbaren Timeout der Auftrag automatisch wieder auf `UNCLAIMED` zurückgesetzt werden.
   - **Freigabe:** Ein Operator muss die Möglichkeit haben, einen angenommenen Auftrag manuell wieder in den globalen Pool zurückzugeben.

---

## 7. Rollen- & Berechtigungskonzept (RBAC)

Das System unterscheidet strikt zwischen zwei Hauptrollen: **Host/Admin (Spieler A)** und **Operator/Client (Spieler B, C, D)**. Die Rechteprüfung muss sowohl im Frontend (UI-Elemente ausblenden/sperren) als auch zwingend im Backend (API-Endpunkte & WebSocket-Befehle absichern) durchgesetzt werden.

---

### 7.1 Rollenmatrix Overview

| Funktion / Bereich | Host / Admin (Spieler A) | Operator / Client (Spieler B, C, D) |
| :--- | :---: | :---: |
| **Aufträge (Jobs)** | | |
| Verfügbare Aufträge einsehen |  Ja |  Ja |
| Aufträge annehmen / freigeben (Claim/Release) |  Ja |  Ja (nur eigene) |
| Neue Aufträge manuell anlegen / generieren |  Ja |  Nein |
| Aufträge bearbeiten / stornieren / löschen |  Ja |  Nein |
| Auftrags-Status manuell überschreiben (z.B. Force-Complete) |  Ja |  Nein |
| **Fuhrpark (Loks & Fahrzeuge)** | | |
| Fahrzeugstandorte & Zustände einsehen |  Ja |  Ja |
| Fahrzeugstatus aktualisieren (z.B. Tank, Schaden) |  Ja |  Ja |
| Neue Fahrzeuge anlegen / aus Fleet entfernen |  Ja |  Nein |
| Master-Daten der Fahrzeuge konfigurieren (z.B. Typ, Leistung) |  Ja |  Nein |
| **Stationen & Gleise** | | |
| Belegungsplan / Gleisbelegung einsehen |  Ja |  Ja |
| Gleisstatus aktualisieren (z.B. "Gleis GF-A1L belegt") |  Ja |  Ja |
| Neue Stationen / Gleise im System anlegen/ändern |  Ja |  Nein |
| **System & Session** | | |
| User-Verwaltung (Spieler anlegen, Kicken, Passwort-Reset) |  Ja |  Nein |
| Session-Einstellungen (z.B. Disconnect-Timeout festlegen) |  Ja |  Nein |
| Server-Logs & Aktivitäts-Protokoll einsehen |  Ja |  Nein |

---

### 7.2 Backend-Anforderungen für die Rechtevergabe

1. **Token-basierte Authentifizierung:**
   - Jeder Spieler authentifiziert sich beim Verbindungsaufbau (Session-Token oder JWT).
   - Der Token enthält die Rolle (`Admin` vs. `Operator`) sowie die eindeutige `Player_ID`.

2. **Strict Route Protection:**
   - Alle geschützten Schreib-Endpunkte des Backends (z.B. `/api/admin/*` oder administrative WebSocket-Actions wie `create_job`, `delete_vehicle`, `kick_player`) müssen vor Ausführung prüfen, ob der Anfragende die Rolle `Admin` besitzt.
   - Versucht ein Client eine Admin-Aktion auszuführen, bricht das Backend dies mit einem Rechte-Fehler (`403 Forbidden` bzw. WebSocket-Error) ab.

3. **Multi-Tenancy für Client-Aktionen:**
   - Operatoren dürfen nur den eigenen Auftragsstatus ändern (z.B. den eigenen Job als "Erledigt" markieren oder den eigenen Job freigeben).
   - Ein Fremd-Release (Spieler B bricht Auftrag von Spieler C ab) ist NUR dem Host/Admin gestattet.

---

### 7.3 Frontend-UI Verhalten

1. **Dynamische Navigation / Views:**
   - Wenn sich ein Client einloggt, wird der Reiter "Backend / Administration" in der Benutzeroberfläche gar nicht erst gerendert oder ausgeblendet.
2. **Context-Sensitive Actions:**
   - Buttons wie "Auftrag stornieren" oder "Neues Gleis hinzufügen" sind für Clients unsichtbar.
   - Aufträge, die bereits von einem anderen Spieler reserviert sind, zeigen für andere Clients den Interaktions-Button als graues/deaktiviertes `Belegt von [Spielername]` an.
