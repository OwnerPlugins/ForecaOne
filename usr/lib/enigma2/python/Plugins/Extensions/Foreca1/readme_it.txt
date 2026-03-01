# Documentazione Plugin Foreca 1 per Enigma2

## Indice
1. [Introduzione](#introduzione)
2. [Installazione](#installazione)
3. [Configurazione iniziale](#configurazione-iniziale)
4. [Utilizzo del plugin](#utilizzo-del-plugin)
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
5. [Configurazione delle API autenticate (opzionale)](#configurazione-delle-api-autenticate-opzionale)
6. [Risoluzione dei problemi](#risoluzione-dei-problemi)
7. [Crediti](#crediti)

---

## Introduzione
**Foreca 1 Weather Forecast** è un plugin per Enigma2 che fornisce previsioni meteorologiche dettagliate fino a 10 giorni, utilizzando i dati pubblici del sito Foreca. Include funzionalità come:

- Meteo attuale con dettagli estesi (temperatura percepita, punto di rugiada, vento, raffiche, umidità, pressione, UV, AQI, probabilità pioggia/neve, aggiornamento).
- Previsione oraria per il giorno selezionato.
- Previsione giornaliera a 7 giorni con temperature min/max, vento, precipitazioni e descrizione.
- Meteogramma con curve di temperatura, barre di pioggia, icone orarie e vento.
- Stazioni di osservazione vicine (tramite scraping o API autenticata).
- Mappe meteorologiche: Wetterkontor (slideshow) e, se configurate, mappe live di Foreca (richiedono credenziali).
- Fasi lunari con orari di levata/tramonto e distanza Terra-Luna.
- Supporto multilingua (traduzioni integrate).
- Personalizzazione di colori e trasparenza.
- Scelta tra sistema metrico e imperiale, con possibilità di personalizzare singole unità (vento, pressione, temperatura, precipitazioni).

---

## Installazione
1. Copiare la cartella `Foreca1` nella directory dei plugin di Enigma2:  
   `/usr/lib/enigma2/python/Plugins/Extensions/`
2. Assicurarsi che i permessi siano corretti (755 per le cartelle, 644 per i file).
3. Riavviare Enigma2 o il menu plugin per rendere visibile il plugin.

---

## Configurazione iniziale

### Lista città offline
Il plugin utilizza un file `new_city.cfg` contenente l'elenco delle città supportate. Se il file non esiste, verrà utilizzata la ricerca online (vedi sotto). È possibile generarlo manualmente (formato: `ID/Nome_Città` per riga) oppure lasciare che il plugin lo crei automaticamente durante la ricerca online.

### Credenziali API (opzionale)
Alcune funzionalità avanzate (mappe live Foreca 1, stazioni di osservazione via API) richiedono un account Foreca e credenziali valide.  
Per configurarle:
1. Creare un file `api_config.txt` nella cartella del plugin (`/usr/lib/enigma2/python/Plugins/Extensions/Foreca1/api_config.txt`).
2. Inserire le seguenti righe (sostituire con i propri dati):
   ```
   API_USER=tuo_username
   API_PASSWORD=tua_password
   ```
3. Opzionalmente è possibile modificare altri parametri come il server mappe o la durata del token (vedi il file di esempio `api_config.txt.example`).

Senza queste credenziali, le mappe live e le stazioni via API non funzioneranno; verrà comunque tentato il fallback allo scraping (dove possibile).

---

## Utilizzo del plugin

### Schermata principale
All'avvio del plugin viene mostrata la schermata principale con:
- Città selezionata, data e nome del giorno.
- Meteo attuale: icona, temperatura, descrizione.
- Dettagli: temperatura percepita, punto di rugiada, vento (velocità e direzione), raffiche, pioggia, umidità, pressione, UV, AQI, probabilità pioggia/neve, orario aggiornamento.
- Informazioni sul sole: alba, tramonto, durata del giorno.
- Fase lunare: icona, nome fase, illuminazione, distanza, orari di levata e tramonto.
- Stazione di osservazione più vicina (se disponibile).
- Lista oraria per il giorno selezionato (scorrevole con i tasti SU/GIÙ).

**Tasti funzione:**
- **0-9**: passa direttamente al giorno corrispondente (0 = oggi, 1 = domani, ... 9 = oggi+9).
- **FRECCIA SINISTRA/DESTRA**: giorno precedente/successivo.
- **OK**: apre la schermata di dettaglio oggi/domani (con periodi e mappa radar).
- **ROSSO**: apre il selettore colore.
- **VERDE**: carica il favorito 1 (città salvata in `fav1.cfg`).
- **GIALLO**: carica il favorito 2 (`fav2.cfg`).
- **BLU**: carica la città home (`home.cfg`).
- **MENU**: apre il menu principale.
- **INFO**: apre la finestra con le informazioni sul plugin.
- **EXIT**: esce dal plugin (torna alla TV o al menu plugin).

### Menu principale
Premendo **MENU** si apre una scelta con le seguenti opzioni:

- **Selezione città**: apre il pannello di ricerca città.
- **Mappe meteo**: sottomenu per scegliere tra mappe Wetterkontor (slideshow) e mappe live Foreca1 (se configurate).
- **Previsione settimanale**: apre la schermata con i 7 giorni dettagliati.
- **Meteogramma**: visualizza il meteogramma a 7 giorni.
- **Osservazioni stazioni**: mostra le stazioni meteorologiche vicine.
- **Impostazioni unità (Semplice)**: scelta rapida tra sistema metrico e imperiale.
- **Impostazioni unità (Avanzate)**: permette di personalizzare singole unità (vento, pressione, temperatura, precipitazioni).
- **Selezione colore**: cambia il colore di sfondo del plugin.
- **Trasparenza**: regola la trasparenza degli overlay.
- **Info**: informazioni sul plugin e crediti.
- **Exit**: chiude il plugin.

### Selezione città
La schermata `Selezione città` permette di cercare una città:
- **ROSSO**: apre la tastiera virtuale per inserire il nome della città.
- La ricerca viene effettuata prima online (tramite API Foreca) e, se non ci sono risultati, viene eseguita una ricerca offline sul file `new_city.cfg`.
- **VERDE**: assegna la città selezionata al favorito 1.
- **GIALLO**: assegna al favorito 2.
- **BLU**: assegna alla home.
- **OK**: carica la città selezionata nella schermata principale e chiude il pannello.
- **EXIT**: torna al menu senza modifiche.

### Previsione giornaliera (7 giorni)
Mostra una lista con i prossimi 7 giorni. Ogni riga contiene:
- Nome del giorno abbreviato e data.
- Temperature min/max (convertite secondo le unità scelte).
- Descrizione meteo abbreviata.
- Probabilità di precipitazione.
- Velocità e direzione del vento.

**Navigazione:**
- **SU/GIÙ**: sposta la selezione.
- **PAG SU/PAG GIÙ**: salta di una pagina.
- **OK**: apre una finestra con i dettagli completi del giorno selezionato.
- **EXIT**: torna al menu principale.

### Meteogramma
Schermata grafica che mostra l'andamento delle temperature (con curva colorata), le barre di precipitazione, le icone meteo e la direzione del vento per ogni intervallo di 3 ore, per i prossimi 7 giorni. Include anche le scale di temperatura e precipitazione e le date.

**Tasti:**
- **OK/EXIT**: chiude il meteogramma.

### Stazioni di osservazione
Mostra un elenco delle stazioni meteorologiche vicine alla località selezionata. I dati provengono da:
1. API autenticata (se configurata e disponibile).
2. Fallback: scraping del sito Foreca.

Per ogni stazione vengono visualizzati:
- Nome, distanza (se disponibile), temperatura, temperatura percepita, punto di rugiada, umidità, pressione, visibilità, orario aggiornamento.
- **SU/GIÙ**: naviga tra le stazioni.
- **OK**: aggiorna i dettagli (se non già visibili).

### Mappe meteorologiche
Il sottomenù **Mappe meteo** offre due opzioni:

#### Mappe Wetterkontor (slideshow)
Mostra una serie di mappe (6 immagini) per la regione selezionata (Europa, Germania, continenti).  
- **ROSSO**: play/pausa slideshow.
- **VERDE**: immagine successiva.
- **GIALLO**: immagine precedente.
- **BLU**: esce.
- **SU/GIÙ**: aumenta/diminuisce la velocità dello slideshow.

#### Mappe live Foreca 1 (API)
Richiede credenziali valide. Se configurato, mostra un elenco di layer disponibili (temperatura, vento, nuvole, ecc.). Dopo la selezione si apre il visualizzatore con:
- **FRECCIA SINISTRA/DESTRA**: cambia il tempo (se disponibili più orari).
- **VERDE**: zoom avanti.
- **GIALLO**: zoom indietro.
- **ROSSO/EXIT**: chiude.

Nota: senza credenziali, questa opzione non sarà disponibile.

### Impostazioni unità di misura
Due modalità:

**Semplice**: consente di scegliere tra sistema metrico (Celsius, km/h, hPa, mm) e imperiale (Fahrenheit, mph, inHg, in). La selezione avviene con i tasti SU/GIÙ e si conferma con VERDE.

**Avanzata**: permette di personalizzare ogni categoria:
- Vento: km/h, m/s, mph, kts.
- Pressione: hPa, mmHg, inHg.
- Temperatura: °C, °F.
- Precipitazioni: mm, in.

La navigazione tra le categorie avviene con i tasti GIALLO (next) e BLU (prev). All'interno di una categoria si seleziona l'unità con OK (appare un segno di spunta). Alla fine si preme VERDE per salvare tutto.

Dopo il salvataggio, la schermata principale si aggiorna immediatamente con le nuove unità.

### Colore e trasparenza
- **Selezione colore**: elenca una serie di colori predefiniti (dal file `color_database.txt`). Con SU/GIÙ ci si sposta, OK conferma. Il colore viene applicato immediatamente a tutte le schermate (tema globale).
- **Trasparenza**: elenca diversi livelli di trasparenza (dal 6% al 56%). OK conferma, il cambiamento è visibile subito.

### Info plugin
Mostra la versione, gli autori e i crediti. Premere OK o EXIT per chiudere.

---

## Configurazione delle API autenticate (opzionale)

Per utilizzare le mappe live Foreca 1 e le stazioni di osservazione via API, è necessario disporre di un account Foreca valido. Seguire questi passaggi:

1. Ottenere username e password dal servizio Foreca (non forniti dal plugin).
2. Creare il file `api_config.txt` nella cartella del plugin con il seguente contenuto:
   ```
   API_USER=tuo_username
   API_PASSWORD=tua_password
   ```
3. (Opzionale) Modificare altri parametri come:
   - `TOKEN_EXPIRE_HOURS` (default 720) – durata del token di accesso.
   - `MAP_SERVER` (default map-eu.foreca.com) – server per le mappe.
   - `AUTH_SERVER` (default pfa.foreca.com) – server di autenticazione.

Un file di esempio (`api_config.txt.example`) viene creato automaticamente se il file principale non esiste.

**Nota bene**: senza queste credenziali, le voci di menu relative alle mappe live potrebbero non apparire o mostrare un errore. Il plugin funziona comunque perfettamente per tutte le altre funzionalità.

---

## Risoluzione dei problemi

### 1. La schermata principale non mostra i dati meteorologici
- Verificare la connessione internet.
- Controllare che la città selezionata sia valida (riprovare con un'altra città).
- Guardare i file di debug nella cartella `debug/` del plugin per eventuali errori.

### 2. La ricerca città non trova risultati
- La ricerca online potrebbe essere temporaneamente non disponibile. Verificare che `api.foreca.net` sia raggiungibile.
- Assicurarsi che il file `new_city.cfg` esista e contenga almeno alcune città (se si preferisce la modalità offline).
- Provare a cercare con un termine più generico (es. "Roma" invece di "Roma, Italia").

### 3. Le mappe live non funzionano
- Controllare che il file `api_config.txt` esista e contenga credenziali corrette.
- Verificare che l'account Foreca abbia accesso alle API mappe (alcuni account potrebbero essere limitati).
- Abilitare il debug (`DEBUG = True` in `plugin.py`) e controllare i log per errori di autenticazione.

### 4. La navigazione in DailyForecast non risponde
- Assicurarsi di aver premuto i tasti SU/GIÙ, non i tasti numerici (che nella schermata principale cambiano giorno). Nella schermata previsione settimanale, i tasti numerici non hanno effetto.
- Verificare che la skin abbia un widget `list` con dimensioni adeguate.

### 5. Le unità di misura non si aggiornano dopo il salvataggio
- Questo problema è stato risolto nelle versioni recenti. Se persiste, controllare che il callback `units_closed` sia presente in `plugin.py` e che le schermate unità restituiscano `True` al salvataggio.

### 6. Il colore non viene applicato a tutte le schermate
- La funzione `apply_global_theme` deve essere chiamata in ogni schermata secondaria (già fatto per tutte le schermate principali). Se qualche schermata personalizzata non ha i widget `background_plate` e `selection_overlay`, il tema non verrà applicato.

---

## Crediti
- **Autore originale Progetto ideato da)**: @Bauernbub
- **Mod e sviluppi successivi**: @Lululla
- **Contributi**: Assistente (refactoring API, implementazione meteogramma, integrazione nuovi dati, debug esteso, navigazione menu, scraping stazioni, integrazione dati lunari, unità avanzate, color global, correzioni DailyForecast)

Grazie per aver scelto Foreca 1 Weather Forecast! Per suggerimenti o segnalazioni, visitare i forum di riferimento (LinuxSatSupport, Corvoboys).