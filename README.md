# Sistem de Fisiere Distribuit

## Descriere

Un sistem de fișiere distribuit în care server-ul expune un anumit director de pe mașina sa și permite clienților să se conecteze și să sincronizeze conținutul directorului local cu cel de pe server.

## Funcționalități

1. **Expunerea Directorului**
   - Server-ul expune un anumit director de pe mașina sa.

2. **Sincronizarea Continutului**
   - Când un client se conectează, solicită informații despre directoarele și fișierele expuse de server.
   - Clientul își sincronizează conținutul unui director local cu cel de pe server, prin:
     - Crearea
     - Redenumirea
     - Ștergerea
     - Modificarea conținutului resurselor afectate

3. **Propagarea Modificărilor**
   - Când un client efectuează modificări asupra directorului său local, aceste modificări sunt transmise server-ului.
   - Server-ul efectuează aceleași modificări asupra directorului server.
   - Server-ul notifică toți clienții conectați pentru a-și sincroniza conținutul directorului lor local cu cel de pe server.

## Fluxul Procesului

1. **Conectarea Clientului**
   - Clientul se conectează la server.
   - Solicită informații despre directoarele și fișierele expuse.

2. **Sincronizarea Inițială**
   - Clientul sincronizează conținutul directorului local cu cel de pe server.

3. **Monitorizarea și Propagarea Modificărilor**
   - Clientul monitorizează modificările locale și le transmite server-ului.
   - Server-ul aplică modificările și notifică toți clienții conectați.

## Notificări

- Server-ul notifică clienții despre:
  - Modificarea conținutului directorului de pe server

