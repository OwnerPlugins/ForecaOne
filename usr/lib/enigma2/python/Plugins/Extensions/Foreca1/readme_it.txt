# 🌤️ Foreca One Previsioni Meteo – Plugin Enigma2

<p align="center">
  <img src="https://github.com/Belfagor2005/ForecaOne/blob/main/usr/lib/enigma2/python/Plugins/Extensions/Foreca1/buttons/ForecaOne.png" alt="Screenshot Foreca1" width="300">
</p>

<p align="center">
  <a href="https://github.com/Belfagor2005/ForecaOne/actions/workflows/pylint.yml">
    <img src="https://github.com/Belfagor2005/ForecaOne/actions/workflows/pylint.yml/badge.svg" alt="Python package">
  </a>
  <a href="https://github.com/Belfagor2005/ForecaOne">
    <img src="https://img.shields.io/badge/Versione-1.0.6-blue.svg" alt="Versione">
  </a>
  <a href="https://www.gnu.org/licenses/gpl-3.0.html">
    <img src="https://img.shields.io/badge/Licenza-GPLv3-blue.svg" alt="Licenza">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.x-yellow.svg" alt="Python">
  </a>
</p>

## 📋 Indice

- [Introduzione](#introduzione)
- [Caratteristiche principali](#caratteristiche-principali)
- [Installazione](#installazione)
- [Configurazione iniziale](#configurazione-iniziale)
- [Utilizzo del Plugin](#utilizzo-del-plugin)
  - [Schermata Principale](#schermata-principale)
  - [Menu Principale](#menu-principale)
  - [Selezione Città](#selezione-città)
  - [Previsioni Giornaliere (7 giorni)](#previsioni-giornaliere-7-giorni)
  - [Meteogramma](#meteogramma)
  - [Stazioni di Osservazione](#stazioni-di-osservazione)
  - [Calendario Lunare (NUOVO)](#calendario-lunare-nuovo)
  - [Mappe Meteo](#mappe-meteo)
  - [Impostazioni Unità di Misura](#impostazioni-unità-di-misura)
  - [Colore e Trasparenza](#colore-e-trasparenza)
  - [Controllo Aggiornamenti](#controllo-aggiornamenti)
  - [Info Plugin](#info-plugin)
- [Configurazione API Autenticata (Opzionale)](#configurazione-api-autenticata-opzionale)
- [Risoluzione dei Problemi](#risoluzione-dei-problemi)
- [Riconoscimenti](#riconoscimenti)
- [Licenza](#licenza)

## Introduzione

**Foreca 1 Previsioni Meteo** è un plugin completo per Enigma2 che fornisce previsioni meteo dettagliate fino a 10 giorni utilizzando i dati pubblici di **Foreca**. Con un'interfaccia intuitiva e ampie opzioni di personalizzazione, puoi tenere sempre d'occhio il tempo direttamente dal tuo ricevitore. Il plugin ora include anche un **calendario lunare completo** con precisi calcoli astronomici.

## Caratteristiche principali

### ✅ Funziona con o senza API
- **Modalità gratuita** – utilizza endpoint pubblici di Foreca e lo scraping per la maggior parte delle funzionalità.
- **Modalità API** – sblocca mappe live, stazioni di osservazione e altro con una **prova gratuita di 30 giorni**.

### 📊 Dati Meteo
- **Condizioni attuali** con dettagli estesi:
  - Temperatura, percepita, punto di rugiada
  - Vento (velocità, raffiche, direzione)
  - Umidità, pressione, indice UV, AQI
  - Probabilità e quantità di pioggia/neve
  - Ora dell'ultimo aggiornamento
- **Previsioni giornaliere a 10 giorni** (temp min/max, vento, precipitazioni, simbolo meteo)
- **Previsioni orarie** per il giorno selezionato (lista scorrevole con icone)
- **Meteogramma a 7 giorni** – curva della temperatura, barre della pioggia, icone e vento

### 🌙 Informazioni Lunari (Migliorate)
- **Calendario Lunare** – una schermata dedicata che mostra tutte le fasi lunari per i prossimi 12 mesi
- Per ogni fase: data, ora, nome della fase, illuminazione, distanza Terra‑Luna e l'icona corrispondente
- Calcoli accurati basati sugli algoritmi di Meeus, fallback all'API USNO
- Fase lunare con icona sulla schermata principale
- Orari di sorgere e tramonto della luna (dall'API USNO, asincrono)

### 📡 Stazioni di Osservazione
- Stazioni vicine (da API autenticata o scraping)
- Temperatura, percepita, umidità, pressione, vento, visibilità

### 🗺️ Mappe Meteo (Migliorate)
- **Wetterkontor** – slideshow di mappe regionali (Europa, Germania, continenti)
- **Mappe Live Foreca (API)** – temperatura, vento, precipitazioni, nuvole, radar
  - Griglia 3×3 di tile con zoom in/out
  - Molteplici orari di previsione
  - Sovrapposizione su sfondi geografici (ora supporta **Nord America, Sud America, Asia, Australia, Africa e fallback mondiale**)
  - Cache locale delle tile per rispettare i limiti API

### ⚙️ Gestione Avanzata delle Unità di Misura
- Scegli tra sistemi **metrico** e **imperiale**
- **Personalizza le singole unità**:
  - Vento: km/h, m/s, mph, nodi
  - Pressione: hPa, mmHg, inHg
  - Temperatura: °C, °F
  - Precipitazioni: mm, in
- Le modifiche si applicano immediatamente, senza bisogno di riavviare

### 🎨 Interfaccia Utente
- **Tema globale** – imposta un colore di sfondo una volta, applicato a tutte le schermate
- **Trasparenza regolabile** per le sovrapposizioni
- **Multilingua** – supporto integrato GetText con fallback a Google Translate
- **Navigazione completa con telecomando** – tutte le schermate accessibili tramite tasti
- **Skin per FHD, HD, WQHD** – perfetto su qualsiasi schermo

### 🔧 Punti di Forza Tecnici
- Compatibile con Python 3
- Download asincroni (luna, mappe, stazioni)
- Modalità di debug con log dettagliati
- Cache intelligente (traduzioni, token API, tile delle mappe)

## Installazione

1. Copia la cartella `Foreca1` nella directory dei plugin di Enigma2:
   ```
   /usr/lib/enigma2/python/Plugins/Extensions/
   ```
2. Imposta i permessi corretti:
   ```
   chmod -R 755 /usr/lib/enigma2/python/Plugins/Extensions/Foreca1
   ```
3. Riavvia Enigma2 o il menu dei plugin per rendere visibile il plugin.

## Configurazione iniziale

### Elenco Città Offline
Il plugin utilizza un file `new_city.cfg` contenente l'elenco delle città supportate (formato: `ID/Nome_Città` per riga). Se il file non esiste, viene utilizzata la ricerca online. Puoi generarlo manualmente o lasciare che il plugin lo crei automaticamente durante una ricerca.

### Credenziali API (Opzionali)
Per abilitare le mappe live e le stazioni API, è necessario un account Foreca (prova gratuita di 30 giorni, 1000 richieste/giorno).

1. Registrati su [https://developer.foreca.com](https://developer.foreca.com)
2. Crea il file `api_config.txt` nella cartella del plugin:
   ```
   /usr/lib/enigma2/python/Plugins/Extensions/Foreca1/api_config.txt
   ```
3. Inserisci le tue credenziali:
   ```ini
   API_USER=il_tuo_username
   API_PASSWORD=la_tua_password
   TOKEN_EXPIRE_HOURS=720
   MAP_SERVER=map-eu.foreca.com
   AUTH_SERVER=pfa.foreca.com
   ```
   (cambia i server se necessario, ad es. `map-us.foreca.com` per le mappe USA)

Un file di esempio `api_config.txt.example` viene creato automaticamente se il file principale non esiste.

**Nota:** senza queste credenziali, il plugin funziona comunque perfettamente utilizzando i dati pubblici.

## Utilizzo del Plugin

### Schermata Principale
All'avvio, la schermata principale mostra:
- Città, data e nome del giorno
- Meteo attuale (icona, temperatura, descrizione)
- Dettagli estesi (percepita, punto di rugiada, vento, raffiche, pioggia, umidità, pressione, UV, AQI, probabilità, ora aggiornamento)
- Informazioni sul sole (alba, tramonto, durata del giorno)
- **Fase lunare** (icona, nome, illuminazione, distanza, orari di sorgere/tramonto) – ora utilizza calcoli astronomici precisi
- Stazione di osservazione più vicina (se disponibile)
- Elenco orario per il giorno selezionato (scorribile con SU/GIÙ)

**Tasti funzione:**
- **0‑9** – salta direttamente al giorno corrispondente (0 = oggi, 1 = domani, … 9 = oggi+9)
- **←/→** – giorno precedente/successivo
- **OK** – apre la schermata dettagliata di oggi/domani (con periodi e mappa radar)
- **ROSSO** – apre il selettore colore
- **VERDE** – carica il preferito 1 (`fav1.cfg`)
- **GIALLO** – carica il preferito 2 (`fav2.cfg`)
- **BLU** – carica la città home (`home.cfg`)
- **MENU** – apre il menu principale
- **INFO** – informazioni sul plugin
- **ESCI** – esce dal plugin (ritorna alla TV o al menu dei plugin)

### Menu Principale
Premendo **MENU** si apre una scelta con le seguenti opzioni:

- **Selezione Città** – cerca e assegna città ai preferiti
- **Mappe Meteo** – sottomenu per scegliere tra Wetterkontor e Mappe Live Foreca
- **Previsioni Settimanali** – schermata dettagliata delle previsioni a 7 giorni
- **Meteogramma** – andamento grafico del tempo
- **Stazioni di Osservazione** – elenco delle stazioni vicine
- **Calendario Lunare (NUOVO)** – visualizza tutte le fasi lunari per i prossimi 12 mesi
- **Impostazioni Unità (Semplice)** – scelta rapida tra metrico e imperiale
- **Impostazioni Unità (Avanzate)** – personalizza vento, pressione, temperatura, precipitazioni
- **Selettore Colore** – cambia il colore di sfondo globale
- **Trasparenza** – regola la trasparenza delle sovrapposizioni
- **Controllo Aggiornamenti** – aggiornamento della versione da github
- **Info** – versione e riconoscimenti
- **Esci** – chiude il menu (ritorna alla schermata principale)

### Selezione Città
- **ROSSO** – apre la tastiera virtuale per inserire il nome della città
- La ricerca viene eseguita prima online (API Foreca), poi offline su `new_city.cfg` se non ci sono risultati
- **VERDE** – assegna la città selezionata al preferito 1
- **GIALLO** – assegna al preferito 2
- **BLU** – assegna come home
- **OK** – carica la città nella schermata principale e chiude il pannello
- **ESCI** – torna al menu senza modifiche

### Previsioni Giornaliere (7 giorni)
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
- **ESCI** – torna al menu principale

### Meteogramma
Mostra l'andamento della temperatura (curva colorata), le barre delle precipitazioni, le icone meteo e il vento per intervalli di 3 ore nei prossimi 7 giorni. Include scale di temperatura e precipitazioni e indicatori di data.

**Tasti:**
- **OK/ESCI** – chiude il meteogramma

### Stazioni di Osservazione
I dati provengono da:
1. API autenticata (se configurata)
2. Fallback: scraping del sito web di Foreca

Per ogni stazione: nome, distanza, temperatura, percepita, punto di rugiada, umidità, pressione, visibilità, ora aggiornamento.
- **SU/GIÙ** – naviga tra le stazioni
- **OK** – mostra i dettagli della stazione selezionata (se non già visibili)

### 🌙 Calendario Lunare (NUOVO)
Questa nuova schermata visualizza una tabella di **tutte le fasi lunari per i prossimi 12 mesi**, a partire dal mese successivo. Per ogni fase vedrai:

- Mese e anno
- Icona della fase lunare (utilizzando lo stesso set di 101 icone della schermata principale)
- Nome della fase (es. "Luna Piena")
- Giorno del mese
- Ora (in UTC)

**Navigazione:**
- **SU/GIÙ** – scorri le fasi
- **PAG SU/PAG GIÙ** – salta di una pagina
- **OK** – mostra informazioni dettagliate: data/ora esatta, percentuale di illuminazione, distanza Terra‑Luna

I calcoli vengono eseguiti offline utilizzando precisi algoritmi astronomici (Meeus), quindi non è necessaria una connessione Internet. I dati sono coerenti e accurati per qualsiasi località (geocentrici).

### Mappe Meteo
Il sottomenu **Mappe Meteo** offre due opzioni:

#### Mappe Wetterkontor (slideshow)
- **ROSSO** – play/pausa
- **VERDE** – immagine successiva
- **GIALLO** – immagine precedente
- **BLU** – esci
- **SU/GIÙ** – aumenta/diminuisce la velocità dello slideshow

#### Mappe Live Foreca (API)
Richiede credenziali valide. Mostra l'elenco dei livelli disponibili (temperatura, vento, precipitazioni, nuvole, radar). Dopo la selezione, si apre il visualizzatore:
- **←/→** – cambia l'orario di previsione (se disponibile)
- **VERDE** – zoom avanti
- **GIALLO** – zoom indietro
- **ROSSO/ESCI** – chiudi

**Nota:** senza credenziali, questa voce di menu è nascosta.

### Impostazioni Unità di Misura

#### Semplice
Scegli tra **metrico** (Celsius, km/h, hPa, mm) e **imperiale** (Fahrenheit, mph, inHg, in) con SU/GIÙ e conferma con VERDE.

#### Avanzate
Personalizza le singole categorie:
- Vento: km/h, m/s, mph, nodi
- Pressione: hPa, mmHg, inHg
- Temperatura: °C, °F
- Precipitazioni: mm, in

Naviga tra le categorie con GIALLO (successiva) e BLU (precedente). All'interno di una categoria, seleziona l'unità con OK (appare un segno di spunta). Salva tutto con VERDE.

Dopo il salvataggio, la schermata principale si aggiorna immediatamente con le nuove unità.

### Colore e Trasparenza
- **Selettore Colore** – elenca i colori predefiniti (da `color_database.txt`). Usa SU/GIÙ per spostarti, OK per confermare. Il colore viene applicato a tutte le schermate (tema globale).
- **Trasparenza** – elenca livelli dal 6% al 56%. OK conferma, la modifica è visibile immediatamente.

### Controllo Aggiornamenti
Controlla se è stato rilasciato un aggiornamento online e lo esegue.

### Info Plugin
Mostra versione, autori e riconoscimenti. Premi OK o ESCI per chiudere.

## Configurazione API Autenticata (Opzionale)

1. Ottieni nome utente e password da [Foreca Developer](https://developer.foreca.com) (prova gratuita).
2. Crea il file `api_config.txt` nella cartella del plugin con il seguente contenuto:
   ```ini
   API_USER=il_tuo_username
   API_PASSWORD=la_tua_password
   TOKEN_EXPIRE_HOURS=720
   MAP_SERVER=map-eu.foreca.com
   AUTH_SERVER=pfa.foreca.com
   ```
3. (Opzionale) Modifica i parametri secondo necessità (es. `MAP_SERVER=map-us.foreca.com` per le mappe USA).

Un file di esempio `api_config.txt.example` viene creato automaticamente.

## Risoluzione dei Problemi

### 1. La schermata principale non mostra dati meteo
- Controlla la connessione Internet.
- Verifica che la città selezionata sia valida.
- Guarda i file di debug nella cartella `debug/` del plugin.

### 2. La ricerca della città non trova risultati
- La ricerca online potrebbe essere temporaneamente non disponibile. Assicurati che `api.foreca.net` sia raggiungibile.
- Assicurati che `new_city.cfg` esista e contenga almeno alcune città.
- Prova un termine più generico (es. “Roma” invece di “Roma, Italia”).

### 3. Le mappe live non funzionano
- Controlla che `api_config.txt` esista e contenga credenziali corrette.
- Verifica che il tuo account Foreca abbia accesso alle API delle mappe.
- Abilita il debug (`DEBUG = True` in `plugin.py`) ed esamina i log.

### 4. La navigazione in DailyForecast non risponde
- Assicurati di premere SU/GIÙ, non i tasti numerici (che cambiano il giorno nella schermata principale).
- Verifica che la skin abbia un widget `list` con dimensioni adeguate.

### 5. Le unità non si aggiornano dopo il salvataggio
- Questo problema è stato risolto nelle versioni recenti. Controlla che il callback `units_closed` sia presente in `plugin.py` e che le schermate delle unità restituiscano `True` al momento del salvataggio.

### 6. Il colore non viene applicato a tutte le schermate
- La funzione `apply_global_theme` deve essere chiamata in ogni schermata secondaria (già fatto per tutte le schermate principali). Se una schermata personalizzata manca dei widget `background_plate` e `selection_overlay`, il tema non verrà applicato.

### 7. Le fasi lunari sembrano imprecise
- Il plugin ora utilizza algoritmi ad alta precisione (Meeus). Se sospetti ancora errori, abilita il debug e controlla il Giorno Giuliano calcolato rispetto a fonti ufficiali.

## Riconoscimenti

- **Design e idea originale:** @Bauernbub
- **Modifiche e sviluppo successivo:** @Lululla
- **Contributi:** Assistente (refactoring API, meteogramma, integrazione nuovi dati, debug esteso, navigazione menu, scraping stazioni, **calendario lunare**, unità avanzate, tema globale, correzioni DailyForecast, miglioramenti mappe)

Grazie a @Orlandox e a tutti gli amici che hanno fornito suggerimenti e testato il plugin.

## Licenza

Questo progetto è concesso in licenza **GNU General Public License v3.0**.  
Vedi il file [LICENSE](LICENSE) per i dettagli.

<p align="center">
  <i>Goditi il meteo, con il sole o con la pioggia! ☀️🌧️</i><br>
  © Lululla 2026
</p>
