# Hlasování valné hromady — Vercel + Neon (bezpečné přihlášení správce)

Převedený projekt ze stávajícího `voting.py`. Zachovává `/`, `/admin`, `/screen`, `/vysledky`, import CSV, Excel a hlasovací rozhraní. Backend používá PostgreSQL namísto lokální SQLite. Správce používá **uživatelské jméno + heslo** a serverové relace v databázi.

## 1. Instalace a migrace databáze

1. Vytvoř bezplatný projekt na https://neon.com. Zkopíruj **pooled connection string** (hostitel zpravidla obsahuje `-pooler`). Heslo databáze neukládej do veřejného repozitáře.
2. Stáhni tento ZIP, rozbal jej a otevři PowerShell ve složce `voting-vercel`.
3. Nainstaluj závislosti a nastav připojení k Neon:

   ```powershell
   py -m pip install -r requirements.txt
   $env:DATABASE_URL = "postgresql://UZIVATEL:HESLO@HOST/DB?sslmode=require"
   ```

4. Pokud ještě nemáš data v Neon, spusť původní migraci:

   ```powershell
   py migrate.py "C:\cesta\voting.db" "C:\cesta\clenove.db"
   ```

   Migrace vytvoří tabulky včetně `admin_users`, importuje historii, přidělené hlasy, PINy, potvrzení a seznam členů. Migraci nespouštěj znovu do již naplněné databáze. Původní `.db` a `.csv` soubory nikdy neposílej do veřejného Git repozitáře.

5. **Pokud už máš databázi Neon z původní verze projektu**, neprováděj znovu migraci! Stačí při vytvoření administrátora níže automaticky vytvořit nové autentizační tabulky. Stávající hlasy zůstanou zachovány.

## 2. Založení administrátora

Na svém počítači se stále nastavenou proměnnou `DATABASE_URL` spusť:

```powershell
py init_admin.py --username admin
```

Program se dvakrát zeptá na nové heslo (**alespoň 14 znaků**). Při psaní se heslo nezobrazuje. Heslo se **neukládá jako čitelný text**, ale jako `scrypt` hash do tabulky `admin_users`.

Můžeš si zvolit jiné jméno, např. `--username predseda`. Při opětovném spuštění se stejným jménem resetuje heslo a odhlásí aktivní relace tohoto účtu. Skript se spouští **lokálně**, nemá veřejný webový endpoint.

## 3. Nasazení na Vercel

1. Nahraj pouze zdrojové soubory projektu na GitHub (bez databází a citlivých `.env` souborů; `.gitignore` je součástí projektu).
2. Na https://vercel.com/new naimportuj GitHub repozitář, root directory nastav na složku obsahující `app.py` (pokud je repozitář o úroveň výš, zvol `voting-vercel`).
3. Ve **Settings → Environment Variables** nastav `DATABASE_URL` na Neon PostgreSQL connection string. `PUBLIC_URL` je volitelné a může obsahovat např. `https://nazev.vercel.app/`.
4. **`ADMIN_KEY` už nenastavuj** — byl z aplikace odstraněn. Administrátor se ověřuje proti hashovanému heslu v PostgreSQL.
5. Deploy; otevři `https://nazev.vercel.app/admin`, zadej jméno a heslo vytvořené v kroku 2.

## Jak funguje přihlášení

- V administraci se zadává **uživatelské jméno a heslo**. Heslo se ověřuje vůči `scrypt` hashi.
- Server vytvoří náhodnou relaci, do databáze uloží **pouze hash relačního tokenu** a do prohlížeče pošle cookie `HttpOnly`, `Secure` (na Vercelu) a `SameSite=Strict`.
- Přihlášení trvá maximálně **8 hodin**. Obnova stránky ponechá přihlášení. Odhlášení zneplatní relaci na serveru.
- Změny v administraci vyžadují samostatný CSRF token; pokusy o přihlášení jsou omezeny záznamy v DB.
- Export Excelu/CSV neobsahuje heslo v URL; přístup je ověřen session cookie.
- Promítání `/screen` je otevřené, ale **čtyřmístný potvrzovací kód se zobrazí pouze v prohlížeči s aktivní administrátorskou relací**. Pro promítání proto používej stejný prohlížeč (novou kartu či okno), případně se na promítacím zařízení přihlas jako administrátor.

## Lokální vývoj

```powershell
$env:DATABASE_URL = "postgresql://..."
py -m pip install -r requirements.txt
py app.py
```

Otevři `http://127.0.0.1:8000/admin`. Pro místní HTTP se používá jiná cookie bez `Secure`; v produkci HTTPS cookie.

## Ověření před skutečným hlasováním

1. Bez přihlášení musí `/api/admin/status`, `/api/admin/code`, exporty i POST pro správu vrátit HTTP 403.
2. Správné jméno + heslo musí otevřít správu; nesprávné heslo nesmí fungovat.
3. Proveď výpis/export, zobraz čtyřmístný kód na plátně, odhlaš se a ověř, že export ani potvrzovací kód dál nejsou přístupné.
4. V prohlížeči otestuj obnovu stránky a expiraci relace. Přihlášení bez CSRF tokenu nesmí povolit zápis.
5. Proveď souběžné hlasování několika zařízeními, zkontroluj součty a pravidlo jednoho hlasu na lístek.
6. Ověř obnovu z databázové zálohy a připrav náhradní postup pro výpadek Internetu.

Základní automatizované testy autentizace: `py -m unittest discover -s tests`. Neověřují skutečný běh s Neon PostgreSQL; ten musíš vyzkoušet zvlášť.

### Zbývající bezpečnostní omezení

- Voliči stále používají čtyřmístné PINy původní aplikace. Jejich omezení chybných pokusů se částečně ukládá jen do paměti konkrétní funkce (nikoli globálně v databázi). Pro veřejnou ostrou volbu doporučujeme toto dále posílit a otestovat.
- Administrace stále zobrazuje existující PINy voličů. Při práci s databází a exporty dodržuj ochranu osobních údajů.
- Free tier neposkytuje garanci dostupnosti. Pro závazné hlasování je nutný provozní test a záložní plán.
- **Před ostrým použitím** proveď integrační a penetrační testy. Přiložená verze není certifikovaným elektronickým volebním systémem.
