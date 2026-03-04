## 🇮🇹 README Italiano

# 🌤️ Foreca 1 Weather Forecast – Plugin per Enigma2

<p align="center">
  <img src="https://github.com/Belfagor2005/ForecaOne/blob/main/usr/lib/enigma2/python/Plugins/Extensions/Foreca1/plugin.png" alt="Foreca1 Screenshot" width="600">
</p>

<p align="center">
  <a href="https://github.com/Belfagor2005/ForecaOne/actions/workflows/pylint.yml">
    <img src="https://github.com/Belfagor2005/ForecaOne/actions/workflows/pylint.yml/badge.svg" alt="Python package">
  </a>
  <a href="https://github.com/Belfagor2005/ForecaOne">
    <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  </a>
  <a href="https://www.gnu.org/licenses/gpl-3.0.html">
    <img src="https://img.shields.io/badge/License-GPLv3-blue.svg" alt="License">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.x-yellow.svg" alt="Python">
  </a>
</p>

---

## 📋 Indice

- [Introduzione](#introduzione)
- [Caratteristiche principali](#caratteristiche-principali)
- [Installazione](#installazione)
- [Configurazione iniziale](#configurazione-iniziale)
- [Utilizzo del plugin](#utilizzo-del-plugin)
  - [Schermata principale](#schermata-principale)
  - [Menu principale](#menu-principale)
  - [Selezione città](#selezione-città)
  - [Previsione giornaliera (7 giorni)](#previsione-giornaliera-7-giorni)
  - [Meteogramma](#meteogramma)
  - [Stazioni di osservazione](#stazioni-di-osservazione)
  - [Mappe meteorologiche](#mappe-meteorologiche)
  - [Impostazioni unità di misura](#impostazioni-unità-di-misura)
  - [Colore e trasparenza](#colore-e-trasparenza)
  - [Info plugin](#info-plugin)
- [Configurazione delle API autenticate (opzionale)](#configurazione-delle-api-autenticate-opzionale)
- [Risoluzione dei problemi](#risoluzione-dei-problemi)
- [Crediti](#crediti)
- [Licenza](#licenza)

---

## Introduzione

**Foreca 1 Weather Forecast** è un plugin completo per Enigma2 che fornisce previsioni meteorologiche dettagliate fino a 10 giorni, utilizzando i dati pubblici del sito **Foreca**. Grazie a un’interfaccia intuitiva e a numerose opzioni di personalizzazione, puoi tenere sempre sotto controllo il meteo direttamente dal tuo decoder.

---

## Caratteristiche principali

### ✅ Funziona con o senza API
- **Modalità gratuita** – utilizza gli endpoint pubblici di Foreca e lo scraping per la maggior parte delle funzionalità.
- **Modalità API** – sblocca mappe live, stazioni di osservazione e altri dati avanzati con un **trial gratuito di 30 giorni**.

### 📊 Dati meteorologici
- **Condizioni attuali** dettagliate:
  - Temperatura, percepita, punto di rugiada
  - Vento (velocità, raffiche, direzione)
  - Umidità, pressione, indice UV, AQI
  - Probabilità e quantità di pioggia/neve
  - Orario dell’ultimo aggiornamento
- **Previsione giornaliera a 10 giorni** (min/max, vento, precipitazioni, simbolo meteo)
- **Previsione oraria** per il giorno selezionato (lista scorrevole con icone)
- **Meteogramma a 7 giorni** – curva temperature, barre pioggia, icone e vento

### 🌙 Luna
- Fase lunare con icona
- Percentuale di illuminazione
- Distanza Terra–Luna
- Orari di levata e tramonto (da API USNO, chiamata asincrona)

### 📡 Stazioni di osservazione
- Elenco delle stazioni vicine (da API autenticata o scraping)
- Temperatura, percepita, umidità, pressione, vento, visibilità

### 🗺️ Mappe meteorologiche
- **Wetterkontor** – slideshow di mappe regionali (Europa, Germania, continenti)
- **Foreca Live Maps (API)** – temperature, vento, precipitazioni, nuvole, radar
  - Griglia 3×3 di tile con zoom avanti/indietro
  - Supporto per diversi orari della previsione
  - Sovrapposizione su sfondi geografici
  - Cache locale delle tile per rispettare i limiti dell’API

### ⚙️ Gestione avanzata delle unità
- Scegli tra **sistema metrico** e **imperiale**
- **Personalizza singole unità**:
  - Vento: km/h, m/s, mph, nodi
  - Pressione: hPa, mmHg, inHg
  - Temperatura: °C, °F
  - Precipitazioni: mm, in
- Le modifiche si applicano immediatamente, senza riavviare il plugin

### 🎨 Interfaccia utente
- **Tema globale** – imposta un colore di sfondo una volta, viene applicato a tutte le schermate
- **Trasparenza** regolabile per gli overlay
- **Multilingua** – supporto GetText integrato, con fallback su Google Translate
- **Navigazione completa da telecomando** – tutte le schermate sono accessibili con i tasti

### 🔧 Aspetti tecnici
- Compatibile con Python 3
- Download asincroni (luna, mappe, stazioni)
- Modalità debug con log dettagliati
- Sistema di caching intelligente (traduzioni, token API, tile mappe)
- Skin per risoluzioni FHD, HD, WQHD

---

## Installazione

1. Copia la cartella `Foreca1` nella directory dei plugin di Enigma2:
   ```
   /usr/lib/enigma2/python/Plugins/Extensions/
   ```
2. Imposta i permessi corretti:
   ```
   chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/Foreca1
   ```
3. Riavvia Enigma2 o il menu plugin per rendere visibile il plugin.

---

## Configurazione iniziale

### Lista città offline
Il plugin utilizza un file `new_city.cfg` contenente l’elenco delle città supportate (formato: `ID/Nome_Città` per riga). Se il file non esiste, viene usata la ricerca online. Puoi generarlo manualmente o lasciare che il plugin lo crei automaticamente durante la ricerca.

### Credenziali API (opzionale)
Per attivare le mappe live e le stazioni via API, è necessario un account Foreca (trial gratuito di 30 giorni, 1000 richieste/giorno).

1. Registrati su [https://developer.foreca.com](https://developer.foreca.com)
2. Crea il file `api_config.txt` nella cartella del plugin:
   ```
   /usr/lib/enigma2/python/Plugins/Extensions/Foreca1/api_config.txt
   ```
3. Inserisci le tue credenziali:
   ```ini
   API_USER=tuo_username
   API_PASSWORD=tua_password
   TOKEN_EXPIRE_HOURS=720
   MAP_SERVER=map-eu.foreca.com
   AUTH_SERVER=pfa.foreca.com
   ```
   (modifica i server se necessario, ad esempio `map-us.foreca.com` per le mappe USA)

Un file di esempio `api_config.txt.example` viene creato automaticamente se il file principale non esiste.

**Nota:** senza queste credenziali, il plugin continua a funzionare perfettamente usando i dati pubblici.

---

## Utilizzo del plugin

### Schermata principale
All’avvio viene mostrata la schermata principale con:
- Città, data e nome del giorno
- Meteo attuale (icona, temperatura, descrizione)
- Dettagli estesi (percepita, rugiada, vento, raffiche, pioggia, umidità, pressione, UV, AQI, probabilità, aggiornamento)
- Informazioni sul sole (alba, tramonto, durata del giorno)
- Fase lunare (icona, nome, illuminazione, distanza, orari)
- Stazione di osservazione più vicina (se disponibile)
- Lista oraria per il giorno selezionato (scorrevole con SU/GIÙ)

**Tasti funzione:**
- **0‑9** – passa direttamente al giorno corrispondente (0 = oggi, 1 = domani, … 9 = oggi+9)
- **←/→** – giorno precedente/successivo
- **OK** – apre la schermata di dettaglio oggi/domani (con periodi e mappa radar)
- **ROSSO** – apre il selettore colore
- **VERDE** – carica il favorito 1 (`fav1.cfg`)
- **GIALLO** – carica il favorito 2 (`fav2.cfg`)
- **BLU** – carica la città home (`home.cfg`)
- **MENU** – apre il menu principale
- **INFO** – informazioni sul plugin
- **EXIT** – esce dal plugin (torna alla TV o al menu plugin)

### Menu principale
Premendo **MENU** si apre un menu con le seguenti opzioni:

- **Selezione città** – cerca e assegna città ai preferiti
- **Mappe meteo** – sottomenu per scegliere tra Wetterkontor e Foreca Live Maps
- **Previsione settimanale** – schermata con i 7 giorni dettagliati
- **Meteogramma** – grafico dell’andamento meteo
- **Osservazioni stazioni** – elenco delle stazioni vicine
- **Impostazioni unità (Semplice)** – scelta rapida tra metrico e imperiale
- **Impostazioni unità (Avanzate)** – personalizzazione di vento, pressione, temperatura, precipitazioni
- **Selezione colore** – cambia il colore di sfondo globale
- **Trasparenza** – regola la trasparenza degli overlay
- **Info** – versione e crediti
- **Exit** – chiude il menu (torna alla schermata principale)

### Selezione città
- **ROSSO** – apre la tastiera virtuale per inserire il nome della città
- La ricerca viene effettuata prima online (API Foreca) e, in caso di fallimento, offline su `new_city.cfg`
- **VERDE** – assegna la città selezionata al favorito 1
- **GIALLO** – assegna al favorito 2
- **BLU** – assegna come home
- **OK** – carica la città nella schermata principale e chiude il pannello
- **EXIT** – torna al menu senza modifiche

### Previsione giornaliera (7 giorni)
Ogni riga contiene:
- Nome del giorno abbreviato e data
- Temperature min/max (convertite secondo le unità scelte)
- Descrizione meteo abbreviata
- Probabilità di precipitazione
- Velocità e direzione del vento

**Navigazione:**
- **SU/GIÙ** – sposta la selezione
- **PAG SU/PAG GIÙ** – salta di una pagina
- **OK** – apre una finestra con i dettagli completi del giorno selezionato
- **EXIT** – torna al menu principale

### Meteogramma
Mostra l’andamento di temperature (curva colorata), precipitazioni (barre), icone meteo e vento per intervalli di 3 ore, per i prossimi 7 giorni. Include scale di temperatura e precipitazione e indicatori delle date.

**Tasti:**
- **OK/EXIT** – chiude il meteogramma

### Stazioni di osservazione
I dati provengono da:
1. API autenticata (se configurata)
2. Fallback: scraping del sito Foreca

Per ogni stazione vengono visualizzati: nome, distanza, temperatura, percepita, rugiada, umidità, pressione, visibilità, orario aggiornamento.
- **SU/GIÙ** – naviga tra le stazioni
- **OK** – mostra i dettagli della stazione selezionata (se non già visibili)

### Mappe meteorologiche
Il sottomenù **Mappe meteo** offre due opzioni:

#### Mappe Wetterkontor (slideshow)
- **ROSSO** – play/pausa
- **VERDE** – immagine successiva
- **GIALLO** – immagine precedente
- **BLU** – esce
- **SU/GIÙ** – aumenta/diminuisce la velocità dello slideshow

#### Mappe live Foreca (API)
Richiede credenziali valide. Mostra l’elenco dei layer disponibili (temperatura, vento, precipitazioni, nuvole, radar). Dopo la selezione si apre il visualizzatore:
- **←/→** – cambia l’orario (se disponibile)
- **VERDE** – zoom avanti
- **GIALLO** – zoom indietro
- **ROSSO/EXIT** – chiude

**Nota:** senza credenziali, questa voce di menu non appare.

### Impostazioni unità di misura

#### Semplice
Scegli tra **metrico** (Celsius, km/h, hPa, mm) e **imperiale** (Fahrenheit, mph, inHg, in) con i tasti SU/GIÙ e conferma con VERDE.

#### Avanzata
Personalizza singole categorie:
- Vento: km/h, m/s, mph, kts
- Pressione: hPa, mmHg, inHg
- Temperatura: °C, °F
- Precipitazioni: mm, in

Naviga tra le categorie con GIALLO (next) e BLU (prev). All’interno di una categoria seleziona l’unità con OK (appare un segno di spunta). Salva tutto con VERDE.

Dopo il salvataggio, la schermata principale si aggiorna immediatamente con le nuove unità.

### Colore e trasparenza
- **Selezione colore** – elenca colori predefiniti (da `color_database.txt`). Con SU/GIÙ ci si sposta, OK conferma. Il colore viene applicato a tutte le schermate (tema globale).
- **Trasparenza** – elenca livelli dal 6% al 56%. OK conferma, il cambiamento è visibile subito.

### Info plugin
Mostra versione, autori e crediti. Premere OK o EXIT per chiudere.

---

## Configurazione delle API autenticate (opzionale)

1. Ottieni username e password da [Foreca Developer](https://developer.foreca.com) (trial gratuito).
2. Crea il file `api_config.txt` nella cartella del plugin con il seguente contenuto:
   ```ini
   API_USER=tuo_username
   API_PASSWORD=tua_password
   TOKEN_EXPIRE_HOURS=720
   MAP_SERVER=map-eu.foreca.com
   AUTH_SERVER=pfa.foreca.com
   ```
3. (Opzionale) Modifica i parametri secondo le tue esigenze (es. `MAP_SERVER=map-us.foreca.com` per le mappe USA).

Un file di esempio `api_config.txt.example` viene creato automaticamente.

---

## Risoluzione dei problemi

### 1. La schermata principale non mostra i dati meteorologici
- Controlla la connessione internet.
- Verifica che la città selezionata sia valida.
- Esamina i file di debug nella cartella `debug/` del plugin.

### 2. La ricerca città non trova risultati
- La ricerca online potrebbe essere temporaneamente fuori servizio. Assicurati che `api.foreca.net` sia raggiungibile.
- Controlla che il file `new_city.cfg` esista e contenga almeno alcune città.
- Prova con un termine più generico (es. “Roma” invece di “Roma, Italia”).

### 3. Le mappe live non funzionano
- Verifica che `api_config.txt` esista e contenga credenziali corrette.
- Controlla che il tuo account Foreca abbia accesso alle API mappe.
- Abilita il debug (`DEBUG = True` in `plugin.py`) e analizza i log.

### 4. La navigazione in DailyForecast non risponde
- Assicurati di premere SU/GIÙ, non i tasti numerici (che nella schermata principale cambiano giorno).
- Verifica che la skin abbia un widget `list` con dimensioni adeguate.

### 5. Le unità di misura non si aggiornano dopo il salvataggio
- Questo problema è stato risolto nelle versioni recenti. Controlla che il callback `units_closed` sia presente in `plugin.py` e che le schermate unità restituiscano `True` al salvataggio.

### 6. Il colore non viene applicato a tutte le schermate
- La funzione `apply_global_theme` deve essere chiamata in ogni schermata secondaria (già fatto per tutte). Se qualche schermata personalizzata non ha i widget `background_plate` e `selection_overlay`, il tema non verrà applicato.

---

## Crediti

- **Progetto originale e idea:** @Bauernbub
- **Modifiche e sviluppo successivo:** @Lululla
- **Contributi:** Assistente (refactoring API, meteogramma, integrazione nuovi dati, debug esteso, navigazione menu, scraping stazioni, integrazione dati lunari, unità avanzate, tema globale, correzioni DailyForecast)

Grazie a @Orlandox e a tutti gli amici che hanno fornito suggerimenti e testato il plugin.

---

## Licenza

Questo progetto è distribuito sotto licenza **GNU General Public License v3.0**.  
Vedi il file [LICENSE](LICENSE) per maggiori dettagli.

---

<p align="center">
  <i>Buon meteo, con sole o con pioggia! ☀️🌧️</i><br>
  © Lululla 2026
</p>
