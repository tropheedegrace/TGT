"""API partagee et authentifiee pour UzaApp.

La base SQLite doit se trouver sur un volume persistant lors d'un hebergement.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Any, Iterator

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

import backup_database
import database


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("UZAA_DATABASE_PATH", BASE_DIR / "data" / "uzaapp.sqlite3"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
SESSION_HOURS = 12
PASSWORD_SCRYPT_N = 2**14
MAX_AGENTS_PER_ESTABLISHMENT = 20
STATIC_FILES = {
    "index.html": BASE_DIR / "index.html",
    "styles.css": BASE_DIR / "styles.css",
    "app.js": BASE_DIR / "app.js",
    "logo-mark.svg": BASE_DIR / "logo-mark.svg",
    "uzaa-logo-transparent.png": BASE_DIR / "uzaa-logo-transparent.png",
    "manifest.webmanifest": BASE_DIR / "manifest.webmanifest",
    "service-worker.js": BASE_DIR / "service-worker.js",
}

app = FastAPI(title="UzaApp API", version="1.0.0", docs_url=None, redoc_url=None)

REQUIRED_TABLES = {
    "etablissement": {"id", "nom", "adresse", "telephone", "email", "numero_impot", "cree_le"},
    "stock": {"id", "etablissement_id", "produit", "quantite", "prix_achat", "prix_vente", "mis_a_jour_le"},
    "entrees": {"id", "etablissement_id", "produit", "quantite", "prix_achat", "prix_vente", "cree_le", "code_barres", "created_by"},
    "ventes": {"id", "etablissement_id", "produit", "quantite", "prix_unitaire", "cree_le", "client", "created_by"},
    "depenses": {"id", "etablissement_id", "libelle", "montant", "cree_le", "personne_responsable", "created_by"},
    "credits": {"id", "etablissement_id", "client", "montant", "solde", "produit", "quantite", "prix_unitaire", "telephone", "echeance", "observation", "updated_at", "created_by"},
    "comptes": {"id", "etablissement_id", "username", "password_hash", "password_salt", "role", "cree_le", "echecs_connexion", "bloque_jusqua", "actif"},
    "sessions": {"token_hash", "compte_id", "expire_le", "cree_le"},
    "mouvements_portefeuille": {"id", "etablissement_id", "agent", "montant", "observation", "cree_le", "created_by"},
}


def validate_database_schema() -> list[str]:
    with connect() as connection:
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing: list[str] = []
        for table, required_columns in REQUIRED_TABLES.items():
            if table not in tables:
                missing.append(f"table:{table}")
                continue
            existing = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            missing_columns = sorted(required_columns - existing)
            for column in missing_columns:
                missing.append(f"{table}.{column}")
        return missing


def sanitize_error_message(detail: Any) -> str:
    if detail is None:
        return "Une erreur inattendue s’est produite. Merci de réessayer."
    if isinstance(detail, dict):
        if "detail" in detail:
            return sanitize_error_message(detail["detail"])
        return sanitize_error_message(str(detail))
    if isinstance(detail, list):
        parts = [sanitize_error_message(item) for item in detail]
        return " ; ".join(part for part in parts if part)
    message = str(detail).strip()
    if not message or message == "None":
        return "Une erreur inattendue s’est produite. Merci de réessayer."
    mapping = {
        "UNIQUE constraint failed": "Ce nom de compte ou ce nom d’établissement est déjà utilisé.",
        "Nom de compte ou mot de passe invalide": "Nom de compte ou mot de passe invalide.",
        "Session invalide": "Session invalide. Veuillez vous reconnecter.",
        "Session expirée": "Votre session a expiré. Veuillez vous reconnecter.",
        "Trop de tentatives": "Trop de tentatives. Réessayez plus tard.",
        "Cette action est réservée": "Cette action est réservée au gérant.",
    }
    for old, replacement in mapping.items():
        if old.lower() in message.lower():
            return replacement
    cleaned = message.replace("Value error, ", "").replace("Validation error", "Vérification invalide").replace("AssertionError: ", "").replace("HTTPException: ", "")
    if cleaned.startswith("1 validation error for"):
        cleaned = cleaned.split("\n")[-1].strip()
    cleaned = cleaned.strip(" .;")
    return cleaned or "Une erreur inattendue s’est produite. Merci de réessayer."


def validate_password_policy(password: str) -> None:
    if len(password) < 12:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Le mot de passe doit contenir au moins 12 caractères.")


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": sanitize_error_message(exc.detail)})


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    details = []
    for error in errors:
        location = ".".join(str(part) for part in error.get("loc", ()))
        message = error.get("msg", "Données invalides.")
        details.append(f"{location or 'champ'} : {message}")
    return JSONResponse(status_code=400, content={"detail": sanitize_error_message(" ; ".join(details))})


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Any) -> Any:
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; media-src 'self' blob:; "
        "connect-src 'self'; worker-src 'self'; manifest-src 'self'; object-src 'none'; "
        "base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(self), microphone=(), geolocation=()"
    if os.environ.get("UZAA_HTTPS_ONLY", "").lower() in {"1", "true", "yes"}:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DB_PATH, timeout=15)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 15000")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def ensure_column(connection: sqlite3.Connection, table: str, column: str, declaration: str) -> None:
    existing = {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}
    if column not in existing:
        connection.execute(f"ALTER TABLE {table} ADD COLUMN {column} {declaration}")


def initialize_database() -> None:
    with connect() as connection:
        database.creer_tables(connection)
        for column, declaration in (
            ("numero_impot", "TEXT NOT NULL DEFAULT ''"),
            ("email", "TEXT NOT NULL DEFAULT ''"),
        ):
            ensure_column(connection, "etablissement", column, declaration)
        for column, declaration in (
            ("code_barres", "TEXT NOT NULL DEFAULT ''"),
            ("created_by", "INTEGER"),
        ):
            ensure_column(connection, "entrees", column, declaration)
        for column, declaration in (
            ("client", "TEXT NOT NULL DEFAULT 'Vente comptoir'"),
            ("created_by", "INTEGER"),
        ):
            ensure_column(connection, "ventes", column, declaration)
        for column, declaration in (
            ("personne_responsable", "TEXT NOT NULL DEFAULT ''"),
            ("created_by", "INTEGER"),
        ):
            ensure_column(connection, "depenses", column, declaration)
        for column, declaration in (
            ("produit", "TEXT NOT NULL DEFAULT ''"),
            ("quantite", "REAL NOT NULL DEFAULT 0"),
            ("prix_unitaire", "REAL NOT NULL DEFAULT 0"),
            ("telephone", "TEXT NOT NULL DEFAULT ''"),
            ("echeance", "TEXT NOT NULL DEFAULT ''"),
            ("observation", "TEXT NOT NULL DEFAULT 'A payer'"),
            ("updated_at", "TEXT NOT NULL DEFAULT ''"),
            ("created_by", "INTEGER"),
        ):
            ensure_column(connection, "credits", column, declaration)
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS comptes (
                id INTEGER PRIMARY KEY,
                etablissement_id INTEGER NOT NULL,
                username TEXT NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('gerant', 'agent')),
                cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                echecs_connexion INTEGER NOT NULL DEFAULT 0,
                bloque_jusqua TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
                    ON UPDATE CASCADE ON DELETE CASCADE,
                UNIQUE (etablissement_id, username)
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token_hash TEXT PRIMARY KEY,
                compte_id INTEGER NOT NULL,
                expire_le TEXT NOT NULL,
                cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (compte_id) REFERENCES comptes(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS paiements_credits (
                id INTEGER PRIMARY KEY,
                credit_id INTEGER NOT NULL,
                montant REAL NOT NULL CHECK (montant > 0),
                cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (credit_id) REFERENCES credits(id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS mouvements_portefeuille (
                id INTEGER PRIMARY KEY,
                etablissement_id INTEGER NOT NULL,
                agent TEXT NOT NULL,
                montant REAL NOT NULL CHECK (montant > 0),
                observation TEXT NOT NULL DEFAULT '',
                cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
                    ON UPDATE CASCADE ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_entrees_etablissement_produit
                ON entrees(etablissement_id, produit);
            CREATE INDEX IF NOT EXISTS idx_ventes_etablissement_date
                ON ventes(etablissement_id, cree_le);
            CREATE INDEX IF NOT EXISTS idx_sessions_expiration ON sessions(expire_le);
            CREATE TABLE IF NOT EXISTS rate_limits (
                scope TEXT NOT NULL,
                ip_hash TEXT NOT NULL,
                window_started REAL NOT NULL,
                attempts INTEGER NOT NULL,
                PRIMARY KEY (scope, ip_hash)
            );
            """
        )
        ensure_column(connection, "comptes", "actif", "INTEGER NOT NULL DEFAULT 1")
        connection.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_comptes_username_global ON comptes(username COLLATE NOCASE)"
        )


initialize_database()
missing_schema = validate_database_schema()
if missing_schema:
    raise RuntimeError(f"Database schema is incomplete: {missing_schema}")


class SetupRequest(BaseModel):
    setup_key: str = Field(min_length=1, max_length=200)
    username: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=200)
    establishment: str = Field(min_length=2, max_length=100)
    address: str = Field(default="", max_length=160)
    telephone: str = Field(default="", max_length=40)
    email: str = Field(default="", max_length=120)
    numero_impot: str = Field(default="", max_length=60)


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=200)
    establishment: str = Field(min_length=2, max_length=100)
    address: str = Field(default="", max_length=160)
    telephone: str = Field(default="", max_length=40)
    email: str = Field(default="", max_length=120)
    numero_impot: str = Field(default="", max_length=60)
    website: str = Field(default="", max_length=200)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=40)
    password: str = Field(min_length=1, max_length=200)


class AgentRequest(BaseModel):
    username: str = Field(min_length=3, max_length=40, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=12, max_length=200)


class ProfileRequest(BaseModel):
    nom: str = Field(min_length=2, max_length=100)
    adresse: str = Field(default="", max_length=160)
    telephone: str = Field(default="", max_length=40)
    email: str = Field(default="", max_length=120)


class EntryRequest(BaseModel):
    product: str = Field(min_length=1, max_length=120)
    quantity: float = Field(gt=0, le=1_000_000)
    purchasePrice: float = Field(gt=0, le=1_000_000_000)
    salePrice: float = Field(gt=0, le=1_000_000_000)
    barcode: str = Field(default="", max_length=80)


class SaleLine(BaseModel):
    product: str = Field(min_length=1, max_length=120)
    quantity: float = Field(gt=0, le=1_000_000)


class SaleRequest(BaseModel):
    items: list[SaleLine] = Field(min_length=1, max_length=100)
    client: str = Field(default="Vente comptoir", max_length=80)


class ExpenseRequest(BaseModel):
    motive: str = Field(min_length=1, max_length=200)
    amount: float = Field(gt=0, le=1_000_000_000)
    responsible: str = Field(min_length=1, max_length=80)


class CreditRequest(BaseModel):
    client: str = Field(min_length=1, max_length=100)
    product: str = Field(min_length=1, max_length=120)
    quantity: float = Field(gt=0, le=1_000_000)
    dueAt: datetime
    phone: str = Field(default="", max_length=40)


class CreditPaymentRequest(BaseModel):
    amount: float = Field(gt=0, le=1_000_000_000)


class WalletRequest(BaseModel):
    agent: str = Field(min_length=1, max_length=80)
    amount: float = Field(gt=0, le=1_000_000_000)
    observation: str = Field(default="Avance", max_length=200)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def password_digest(password: str, salt: bytes) -> str:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=PASSWORD_SCRYPT_N, r=8, p=1).hex()


def create_password(password: str) -> tuple[str, str]:
    salt = secrets.token_bytes(16)
    return password_digest(password, salt), salt.hex()


def new_session(account_id: int) -> str:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("ascii")).hexdigest()
    expires = (now_utc() + timedelta(hours=SESSION_HOURS)).isoformat()
    with connect() as connection:
        connection.execute(
            "INSERT INTO sessions(token_hash, compte_id, expire_le) VALUES (?, ?, ?)",
            (token_hash, account_id, expires),
        )
    return token


def account_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {"id": row["id"], "username": row["username"], "role": row["role"]}


def require_account(authorization: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Connectez-vous pour continuer.")
    token = authorization[7:].strip()
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect() as connection:
        row = connection.execute(
                """SELECT c.id, c.username, c.role, c.etablissement_id, c.actif, s.expire_le
               FROM sessions s JOIN comptes c ON c.id = s.compte_id
               WHERE s.token_hash = ?""",
            (token_hash,),
        ).fetchone()
        if not row or not row["actif"]:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session invalide. Reconnectez-vous.")
        if row["expire_le"] <= now_utc().isoformat():
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expirée. Reconnectez-vous.")
    return dict(row)


def require_manager(account: dict[str, Any] = Depends(require_account)) -> dict[str, Any]:
    if account["role"] != "gerant":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cette action est réservée au gérant.")
    return account


def stock_for_product(connection: sqlite3.Connection, establishment_id: int, product: str) -> dict[str, Any] | None:
    entry = connection.execute(
        """SELECT produit, prix_achat, prix_vente, code_barres, cree_le
           FROM entrees WHERE etablissement_id = ? AND produit = ? COLLATE NOCASE
           ORDER BY id DESC LIMIT 1""",
        (establishment_id, product),
    ).fetchone()
    if not entry:
        return None
    entries = connection.execute(
        "SELECT COALESCE(SUM(quantite), 0) FROM entrees WHERE etablissement_id = ? AND produit = ? COLLATE NOCASE",
        (establishment_id, product),
    ).fetchone()[0]
    sales = connection.execute(
        "SELECT COALESCE(SUM(quantite), 0) FROM ventes WHERE etablissement_id = ? AND produit = ? COLLATE NOCASE",
        (establishment_id, product),
    ).fetchone()[0]
    credits = connection.execute(
        "SELECT COALESCE(SUM(quantite), 0) FROM credits WHERE etablissement_id = ? AND produit = ? COLLATE NOCASE",
        (establishment_id, product),
    ).fetchone()[0]
    return {
        "product": entry["produit"],
        "barcode": entry["code_barres"],
        "quantity": float(entries - sales - credits),
        "purchasePrice": float(entry["prix_achat"]),
        "salePrice": float(entry["prix_vente"]),
        "updatedAt": entry["cree_le"],
    }


def established_profile(connection: sqlite3.Connection, establishment_id: int) -> dict[str, str]:
    row = connection.execute("SELECT * FROM etablissement WHERE id = ?", (establishment_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Etablissement introuvable.")
    return {
        "nom": row["nom"],
        "adresse": row["adresse"],
        "telephone": row["telephone"],
        "email": row["email"],
    }


def iso_or_db(value: str) -> str:
    if "T" in value:
        return value
    return value.replace(" ", "T") + "+00:00"


def money(value: float | int) -> str:
    return f"{float(value):,.0f} FC".replace(",", " ")


def build_business_summary(establishment_id: int, start_date: str | None = None, end_date: str | None = None) -> dict[str, Any]:
    def previous_window(current_start: str | None, current_end: str | None) -> tuple[str | None, str | None]:
        if not current_start or not current_end:
            return None, None
        start_dt = datetime.strptime(current_start, "%Y-%m-%d")
        end_dt = datetime.strptime(current_end, "%Y-%m-%d")
        if end_dt < start_dt:
            return None, None

        def previous_month_day(value: datetime) -> datetime:
            first_of_month = value.replace(day=1)
            last_of_previous_month = first_of_month - timedelta(days=1)
            return last_of_previous_month.replace(day=min(value.day, last_of_previous_month.day))

        prev_start = previous_month_day(start_dt)
        prev_end = previous_month_day(end_dt)
        return prev_start.strftime("%Y-%m-%d"), prev_end.strftime("%Y-%m-%d")

    with connect() as connection:
        sales_where = "WHERE etablissement_id = ?"
        params: list[Any] = [establishment_id]
        if start_date:
            sales_where += " AND cree_le >= ?"
            params.append(f"{start_date}T00:00:00+00:00")
        if end_date:
            sales_where += " AND cree_le <= ?"
            params.append(f"{end_date}T23:59:59+00:00")
        sales_total = connection.execute(
            f"SELECT COALESCE(SUM(quantite * prix_unitaire), 0) FROM ventes {sales_where}",
            tuple(params),
        ).fetchone()[0]
        expenses_where = "WHERE etablissement_id = ?"
        expense_params: list[Any] = [establishment_id]
        if start_date:
            expenses_where += " AND cree_le >= ?"
            expense_params.append(f"{start_date}T00:00:00+00:00")
        if end_date:
            expenses_where += " AND cree_le <= ?"
            expense_params.append(f"{end_date}T23:59:59+00:00")
        expenses_total = connection.execute(
            f"SELECT COALESCE(SUM(montant), 0) FROM depenses {expenses_where}",
            tuple(expense_params),
        ).fetchone()[0]
        credits_outstanding = connection.execute(
            "SELECT COALESCE(SUM(solde), 0) FROM credits WHERE etablissement_id = ? AND solde > 0",
            (establishment_id,),
        ).fetchone()[0]
        products = connection.execute(
            "SELECT produit FROM entrees WHERE etablissement_id = ? GROUP BY produit COLLATE NOCASE ORDER BY produit",
            (establishment_id,),
        ).fetchall()
        stock_low_count = 0
        stock_value = 0.0
        product_health: list[dict[str, Any]] = []
        for row in products:
            product = row["produit"]
            stock = stock_for_product(connection, establishment_id, product)
            if not stock:
                continue
            stock_value += float(stock["quantity"]) * float(stock["purchasePrice"])
            if stock["quantity"] <= 5:
                stock_low_count += 1
            product_health.append({
                "product": stock["product"],
                "quantity": stock["quantity"],
                "purchase_price": stock["purchasePrice"],
                "sale_price": stock["salePrice"],
                "low_stock": stock["quantity"] <= 5,
            })
        top_products = []
        if start_date or end_date:
            product_sales = connection.execute(
                "SELECT produit, SUM(quantite) AS quantity, SUM(quantite * prix_unitaire) AS revenue FROM ventes "
                "WHERE etablissement_id = ? AND cree_le >= ? AND cree_le <= ? GROUP BY produit COLLATE NOCASE ORDER BY revenue DESC LIMIT 5",
                (establishment_id, (start_date or "1970-01-01") + "T00:00:00+00:00", (end_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")) + "T23:59:59+00:00"),
            ).fetchall()
        else:
            product_sales = connection.execute(
                "SELECT produit, SUM(quantite) AS quantity, SUM(quantite * prix_unitaire) AS revenue FROM ventes WHERE etablissement_id = ? GROUP BY produit COLLATE NOCASE ORDER BY revenue DESC LIMIT 5",
                (establishment_id,),
            ).fetchall()
        for row in product_sales:
            top_products.append({
                "product": row["produit"],
                "quantity": float(row["quantity"]),
                "revenue": float(row["revenue"]),
            })
        previous_start, previous_end = previous_window(start_date, end_date)
        prev_sales_total = 0.0
        if previous_start and previous_end:
            prev_sales_total = connection.execute(
                "SELECT COALESCE(SUM(quantite * prix_unitaire), 0) FROM ventes WHERE etablissement_id = ? AND cree_le >= ? AND cree_le <= ?",
                (establishment_id, f"{previous_start}T00:00:00+00:00", f"{previous_end}T23:59:59+00:00"),
            ).fetchone()[0]
        alerts = []
        if stock_low_count > 0:
            alerts.append({"type": "stock", "title": "Stock faible", "message": f"{stock_low_count} produit(s) ont un stock faible."})
        if credits_outstanding > 0:
            alerts.append({"type": "credit", "title": "Crédits", "message": f"{money(credits_outstanding)} sont encore à recouvrer."})
        if sales_total < 1:
            alerts.append({"type": "sales", "title": "Activité faible", "message": "Aucune vente enregistrée sur cette période."})
        summary = {
            "sales_total": float(sales_total),
            "expenses_total": float(expenses_total),
            "cashflow_total": float(sales_total - expenses_total),
            "credits_outstanding": float(credits_outstanding),
            "stock_low_count": int(stock_low_count),
            "stock_value": float(stock_value),
            "products": product_health,
            "top_products": top_products,
            "alerts": alerts,
            "comparison": {
                "previous_start": previous_start,
                "previous_end": previous_end,
                "previous_sales_total": float(prev_sales_total),
                "delta_sales_total": float(sales_total - prev_sales_total),
            },
        }
        return summary


@app.get("/api/reports/summary")
def get_business_summary(account: dict[str, Any] = Depends(require_account), start_date: str | None = None, end_date: str | None = None) -> dict[str, Any]:
    return build_business_summary(account["etablissement_id"], start_date=start_date, end_date=end_date)


@app.get("/api/reports/export")
def export_business_report(account: dict[str, Any] = Depends(require_account), start_date: str | None = None, end_date: str | None = None) -> Response:
    summary = build_business_summary(account["etablissement_id"], start_date=start_date, end_date=end_date)
    rows = [
        ["sales_total", summary["sales_total"]],
        ["expenses_total", summary["expenses_total"]],
        ["cashflow_total", summary["cashflow_total"]],
        ["credits_outstanding", summary["credits_outstanding"]],
        ["stock_low_count", summary["stock_low_count"]],
        ["stock_value", summary["stock_value"]],
    ]
    csv_rows = [",".join([str(key), str(value)]) for key, value in rows]
    payload = "metric,value\n" + "\n".join(csv_rows) + "\n"
    filename = f"uzaapp-rapport-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.csv"
    return Response(content=payload, media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@app.get("/api/reports/pdf")
def export_business_pdf(account: dict[str, Any] = Depends(require_account), start_date: str | None = None, end_date: str | None = None) -> Response:
    summary = build_business_summary(account["etablissement_id"], start_date=start_date, end_date=end_date)
    comparison = summary["comparison"]
    report_lines = [
        "UzaApp - Rapport de performance",
        f"Période: {start_date or 'toute la période'} au {end_date or 'aujourd\'hui'}",
        f"Ventes: {summary['sales_total']} FC",
        f"Ventes période précédente: {comparison['previous_sales_total']} FC",
        f"Evolution des ventes: {comparison['delta_sales_total']} FC",
        f"Dépenses: {summary['expenses_total']} FC",
        f"Cashflow: {summary['cashflow_total']} FC",
        f"Crédits: {summary['credits_outstanding']} FC",
        f"Stock bas: {summary['stock_low_count']} produit(s)",
        "Alertes:",
        *(f"- {alert['title']}: {alert['message']}" for alert in summary["alerts"]),
    ]
    content_lines = []
    cursor_y = 760
    for line in report_lines:
        escaped = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        content_lines.append(f"BT /F1 12 Tf 72 {cursor_y} Td ({escaped}) Tj ET")
        cursor_y -= 18
    content_stream = "\n".join(content_lines).encode("latin-1", errors="replace")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        b"4 0 obj\n<< /Length " + str(len(content_stream)).encode("ascii") + b" >>\nstream\n" + content_stream + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    ]
    pdf_bytes = b"%PDF-1.4\n"
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf_bytes))
        pdf_bytes += obj
    xref_start = len(pdf_bytes)
    pdf_bytes += f"xref\n0 {len(objects) + 1}\n".encode("ascii")
    pdf_bytes += b"0000000000 65535 f \n"
    for offset in offsets[1:]:
        pdf_bytes += f"{offset:010d} 00000 n \n".encode("ascii")
    pdf_bytes += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    filename = f"uzaapp-performance-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}.pdf"
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def enforce_ip_rate_limit(
    connection: sqlite3.Connection,
    scope: str,
    client_ip: str,
    limit: int,
    window_seconds: int,
    global_limit: int | None = None,
) -> None:
    now = time.time()
    limit_secret = os.environ.get("UZAA_RATE_LIMIT_SECRET") or str(DB_PATH.resolve())
    ip_hash = hmac.new(limit_secret.encode("utf-8"), client_ip.encode("utf-8"), hashlib.sha256).hexdigest()
    connection.execute("BEGIN IMMEDIATE")
    connection.execute("DELETE FROM rate_limits WHERE window_started < ?", (now - window_seconds,))
    if global_limit is not None:
        global_attempts = connection.execute(
            "SELECT COALESCE(SUM(attempts), 0) FROM rate_limits WHERE scope = ? AND window_started >= ?",
            (scope, now - window_seconds),
        ).fetchone()[0]
        if global_attempts >= global_limit:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Les inscriptions sont temporairement limitées. Réessayez plus tard.")
    row = connection.execute(
        "SELECT window_started, attempts FROM rate_limits WHERE scope = ? AND ip_hash = ?",
        (scope, ip_hash),
    ).fetchone()
    if row and now - row["window_started"] < window_seconds and row["attempts"] >= limit:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Trop de tentatives. Réessayez plus tard.")
    if row and now - row["window_started"] < window_seconds:
        connection.execute("UPDATE rate_limits SET attempts = attempts + 1 WHERE scope = ? AND ip_hash = ?", (scope, ip_hash))
    else:
        connection.execute(
            "INSERT INTO rate_limits(scope, ip_hash, window_started, attempts) VALUES (?, ?, ?, 1) "
            "ON CONFLICT(scope, ip_hash) DO UPDATE SET window_started = excluded.window_started, attempts = 1",
            (scope, ip_hash, now),
        )
@app.get("/api/auth/status")
def auth_status() -> dict[str, bool]:
    with connect() as connection:
        account_count = connection.execute("SELECT COUNT(*) FROM comptes").fetchone()[0]
    return {
        "initialized": account_count > 0,
        "setupConfigured": bool(os.environ.get("UZAA_SETUP_KEY")),
        "publicRegistrationEnabled": os.environ.get("UZAA_ALLOW_PUBLIC_REGISTRATION", "true").lower() in {"1", "true", "yes"},
    }


@app.post("/api/auth/register", status_code=201)
def register_owner(payload: RegisterRequest, request: Request) -> dict[str, Any]:
    if os.environ.get("UZAA_ALLOW_PUBLIC_REGISTRATION", "true").lower() not in {"1", "true", "yes"}:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Les inscriptions publiques sont désactivées. Utilisez la configuration initiale sécurisée.")
    if payload.website:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Inscription refusée.")
    validate_password_policy(payload.password)
    client_ip = request.client.host if request.client else "unknown"
    with connect() as connection:
        enforce_ip_rate_limit(connection, "register", client_ip, limit=10, window_seconds=3600, global_limit=100)
    password_hash, password_salt = create_password(payload.password)
    try:
        with connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "INSERT INTO etablissement(nom, adresse, telephone, email, numero_impot) VALUES (?, ?, ?, ?, ?)",
                (payload.establishment.strip(), payload.address.strip(), payload.telephone.strip(), payload.email.strip(), payload.numero_impot.strip()),
            )
            establishment_id = int(cursor.lastrowid)
            cursor = connection.execute(
                """INSERT INTO comptes(etablissement_id, username, password_hash, password_salt, role)
                   VALUES (?, ?, ?, ?, 'gerant')""",
                (establishment_id, payload.username.lower(), password_hash, password_salt),
            )
            account_id = int(cursor.lastrowid)
    except sqlite3.IntegrityError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ce nom de compte est déjà utilisé. Choisissez-en un autre.") from error
    token = new_session(account_id)
    return {"token": token, "user": {"id": account_id, "username": payload.username.lower(), "role": "gerant"}}


@app.post("/api/auth/setup")
def setup_owner(payload: SetupRequest, request: Request) -> dict[str, Any]:
    client_ip = request.client.host if request.client else "unknown"
    with connect() as connection:
        enforce_ip_rate_limit(connection, "setup", client_ip, limit=10, window_seconds=900)
    expected_key = os.environ.get("UZAA_SETUP_KEY", "")
    if not expected_key or not hmac.compare_digest(payload.setup_key, expected_key):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Code de première configuration invalide ou non défini sur le serveur.")
    validate_password_policy(payload.password)
    password_hash, password_salt = create_password(payload.password)
    try:
        with connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if connection.execute("SELECT 1 FROM comptes LIMIT 1").fetchone():
                raise HTTPException(status.HTTP_409_CONFLICT, "Le premier gérant est déjà créé.")
            cursor = connection.execute(
                "INSERT INTO etablissement(nom, adresse, telephone, email, numero_impot) VALUES (?, ?, ?, ?, ?)",
                (payload.establishment.strip(), payload.address.strip(), payload.telephone.strip(), payload.email.strip(), payload.numero_impot.strip()),
            )
            establishment_id = int(cursor.lastrowid)
            cursor = connection.execute(
                """INSERT INTO comptes(etablissement_id, username, password_hash, password_salt, role)
                   VALUES (?, ?, ?, ?, 'gerant')""",
                (establishment_id, payload.username.lower(), password_hash, password_salt),
            )
            account_id = int(cursor.lastrowid)
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Impossible de créer le compte initial.") from error
    token = new_session(account_id)
    return {"token": token, "user": {"id": account_id, "username": payload.username.lower(), "role": "gerant"}}


@app.post("/api/auth/login")
def login(payload: LoginRequest, request: Request) -> dict[str, Any]:
    client_ip = request.client.host if request.client else "unknown"
    with connect() as connection:
        enforce_ip_rate_limit(connection, "login", client_ip, limit=20, window_seconds=900)
    with connect() as connection:
        row = connection.execute(
            "SELECT * FROM comptes WHERE username = ? COLLATE NOCASE AND actif = 1 LIMIT 1",
            (payload.username.strip(),),
        ).fetchone()
        if not row:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Nom de compte ou mot de passe invalide.")
        now = now_utc().isoformat()
        if row["bloque_jusqua"] and row["bloque_jusqua"] > now:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Trop de tentatives. Réessayez dans quelques minutes.")
        supplied = password_digest(payload.password, bytes.fromhex(row["password_salt"]))
        if not hmac.compare_digest(supplied, row["password_hash"]):
            failures = row["echecs_connexion"] + 1
            lock_until = (now_utc() + timedelta(minutes=15)).isoformat() if failures >= 8 else ""
            connection.execute(
                "UPDATE comptes SET echecs_connexion = ?, bloque_jusqua = ? WHERE id = ?",
                (0 if lock_until else failures, lock_until, row["id"]),
            )
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Nom de compte ou mot de passe invalide.")
        connection.execute("UPDATE comptes SET echecs_connexion = 0, bloque_jusqua = '' WHERE id = ?", (row["id"],))
        account = account_payload(row)
    return {"token": new_session(account["id"]), "user": account}


@app.post("/api/auth/logout", status_code=204)
def logout(account: dict[str, Any] = Depends(require_account), authorization: Annotated[str | None, Header()] = None) -> None:
    token = (authorization or "")[7:].strip()
    with connect() as connection:
        connection.execute("DELETE FROM sessions WHERE token_hash = ?", (hashlib.sha256(token.encode()).hexdigest(),))


@app.get("/api/auth/me")
def who_am_i(account: dict[str, Any] = Depends(require_account)) -> dict[str, Any]:
    return {"id": account["id"], "username": account["username"], "role": account["role"]}


@app.get("/api/data")
def get_data(account: dict[str, Any] = Depends(require_account)) -> dict[str, Any]:
    establishment_id = account["etablissement_id"]
    manager = account["role"] == "gerant"
    with connect() as connection:
        profile = established_profile(connection, establishment_id)
        entries_rows = connection.execute(
            "SELECT * FROM entrees WHERE etablissement_id = ? ORDER BY id",
            (establishment_id,),
        ).fetchall()
        stock = []
        latest_products = connection.execute(
            "SELECT produit FROM entrees WHERE etablissement_id = ? GROUP BY produit COLLATE NOCASE ORDER BY produit",
            (establishment_id,),
        ).fetchall()
        for product_row in latest_products:
            item = stock_for_product(connection, establishment_id, product_row["produit"])
            if item:
                if not manager:
                    item["purchasePrice"] = None
                stock.append(item)
        sales_sql = "SELECT * FROM ventes WHERE etablissement_id = ?"
        expenses_sql = "SELECT * FROM depenses WHERE etablissement_id = ?"
        credits_sql = "SELECT * FROM credits WHERE etablissement_id = ?"
        wallet_sql = "SELECT * FROM mouvements_portefeuille WHERE etablissement_id = ?"
        parameters: tuple[Any, ...] = (establishment_id,)
        if not manager:
            sales_sql += " AND created_by = ?"
            expenses_sql += " AND created_by = ?"
            credits_sql += " AND created_by = ?"
            parameters = (establishment_id, account["id"])
        sales_rows = connection.execute(sales_sql + " ORDER BY id", parameters).fetchall()
        expense_rows = connection.execute(expenses_sql + " ORDER BY id", parameters).fetchall()
        credit_rows = connection.execute(credits_sql + " ORDER BY id", parameters).fetchall()
        wallet_rows = connection.execute(wallet_sql + " ORDER BY id", (establishment_id,)).fetchall() if manager else []
        if not manager:
            entries_rows = [dict(row) | {"prix_achat": None} for row in entries_rows]
        entries = [{
            "id": row["id"], "product": row["produit"], "quantity": row["quantite"],
            "purchasePrice": row["prix_achat"], "salePrice": row["prix_vente"],
            "barcode": row["code_barres"], "createdAt": iso_or_db(row["cree_le"]),
        } for row in entries_rows]
        sales = [{
            "id": row["id"], "product": row["produit"], "quantity": row["quantite"],
            "unitPrice": row["prix_unitaire"], "amount": row["quantite"] * row["prix_unitaire"],
            "client": row["client"], "createdAt": iso_or_db(row["cree_le"]),
        } for row in sales_rows]
        expenses = [{
            "id": row["id"], "motive": row["libelle"], "amount": row["montant"],
            "responsible": row["personne_responsable"], "createdAt": iso_or_db(row["cree_le"]),
        } for row in expense_rows]
        credits = [{
            "id": row["id"], "client": row["client"], "product": row["produit"],
            "quantity": row["quantite"], "unitPrice": row["prix_unitaire"],
            "amount": row["montant"], "balance": row["solde"], "phone": row["telephone"],
            "dueAt": iso_or_db(row["echeance"]) if row["echeance"] else "",
            "status": row["observation"], "createdAt": iso_or_db(row["cree_le"]),
        } for row in credit_rows]
        wallet = [{
            "id": row["id"], "agent": row["agent"], "amount": row["montant"],
            "observation": row["observation"], "createdAt": iso_or_db(row["cree_le"]),
        } for row in wallet_rows]
    if not manager:
        profile = {key: value for key, value in profile.items() if key in ("nom", "adresse", "telephone")}
    return {"profile": profile, "entries": entries, "stock": stock, "sales": sales, "expenses": expenses, "credits": credits, "wallet": wallet}


@app.put("/api/profile")
def update_profile(payload: ProfileRequest, account: dict[str, Any] = Depends(require_manager)) -> dict[str, str]:
    with connect() as connection:
        connection.execute(
            """UPDATE etablissement SET nom = ?, adresse = ?, telephone = ?, email = ?
               WHERE id = ?""",
            (payload.nom.strip(), payload.adresse.strip(), payload.telephone.strip(), payload.email.strip(), account["etablissement_id"]),
        )
        return established_profile(connection, account["etablissement_id"])


@app.post("/api/agents", status_code=201)
def create_agent(payload: AgentRequest, account: dict[str, Any] = Depends(require_manager)) -> dict[str, Any]:
    validate_password_policy(payload.password)
    try:
        with connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            active_agents = connection.execute(
                "SELECT COUNT(*) FROM comptes WHERE etablissement_id = ? AND role = 'agent' AND actif = 1",
                (account["etablissement_id"],),
            ).fetchone()[0]
            if active_agents >= MAX_AGENTS_PER_ESTABLISHMENT:
                raise HTTPException(status.HTTP_409_CONFLICT, f"Un commerce ne peut pas avoir plus de {MAX_AGENTS_PER_ESTABLISHMENT} agents actifs.")
            password_hash, password_salt = create_password(payload.password)
            cursor = connection.execute(
                """INSERT INTO comptes(etablissement_id, username, password_hash, password_salt, role)
                   VALUES (?, ?, ?, ?, 'agent')""",
                (account["etablissement_id"], payload.username.lower(), password_hash, password_salt),
            )
            return {"id": int(cursor.lastrowid), "username": payload.username.lower(), "role": "agent"}
    except sqlite3.IntegrityError as error:
        raise HTTPException(409, "Ce nom de compte est déjà utilisé. Choisissez-en un autre.") from error


@app.get("/api/agents")
def list_agents(account: dict[str, Any] = Depends(require_manager)) -> list[dict[str, Any]]:
    with connect() as connection:
        rows = connection.execute(
            "SELECT id, username, actif FROM comptes WHERE etablissement_id = ? AND role = 'agent' ORDER BY username COLLATE NOCASE",
            (account["etablissement_id"],),
        ).fetchall()
    return [{"id": row["id"], "username": row["username"], "active": bool(row["actif"])} for row in rows]


@app.delete("/api/agents/{agent_id}", status_code=204)
def revoke_agent(agent_id: int, account: dict[str, Any] = Depends(require_manager)) -> None:
    with connect() as connection:
        cursor = connection.execute(
            "UPDATE comptes SET actif = 0 WHERE id = ? AND etablissement_id = ? AND role = 'agent' AND actif = 1",
            (agent_id, account["etablissement_id"]),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Compte agent introuvable ou déjà désactivé.")
        connection.execute("DELETE FROM sessions WHERE compte_id = ?", (agent_id,))


@app.post("/api/entries", status_code=201)
def create_entry(payload: EntryRequest, account: dict[str, Any] = Depends(require_manager)) -> dict[str, Any]:
    product = payload.product.strip()
    with connect() as connection:
        if payload.barcode:
            duplicate = connection.execute(
                "SELECT produit FROM entrees WHERE etablissement_id = ? AND code_barres = ? LIMIT 1",
                (account["etablissement_id"], payload.barcode.strip()),
            ).fetchone()
            if duplicate and duplicate["produit"].casefold() != product.casefold():
                raise HTTPException(409, "Ce code-barres est déjà associé à un autre produit.")
        cursor = connection.execute(
            """INSERT INTO entrees(etablissement_id, produit, quantite, prix_achat, prix_vente, code_barres, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (account["etablissement_id"], product, payload.quantity, payload.purchasePrice, payload.salePrice, payload.barcode.strip(), account["id"]),
        )
        return {"id": int(cursor.lastrowid), "product": product}


@app.post("/api/sales", status_code=201)
def create_sale(payload: SaleRequest, account: dict[str, Any] = Depends(require_account)) -> dict[str, Any]:
    establishment_id = account["etablissement_id"]
    combined: dict[str, float] = {}
    for item in payload.items:
        key = item.product.strip().casefold()
        combined[key] = combined.get(key, 0) + item.quantity
    created_at = now_utc().isoformat()
    rows: list[dict[str, Any]] = []
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        for key, quantity in combined.items():
            catalog_row = connection.execute(
                "SELECT produit, prix_vente FROM entrees WHERE etablissement_id = ? AND produit = ? COLLATE NOCASE ORDER BY id DESC LIMIT 1",
                (establishment_id, key),
            ).fetchone()
            if not catalog_row:
                raise HTTPException(404, f"Produit « {key} » absent du catalogue.")
            stock = stock_for_product(connection, establishment_id, catalog_row["produit"])
            if not stock or stock["quantity"] < quantity:
                raise HTTPException(409, f"Stock insuffisant pour {catalog_row['produit']}.")
            cursor = connection.execute(
                """INSERT INTO ventes(etablissement_id, produit, quantite, prix_unitaire, client, created_by, cree_le)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (establishment_id, catalog_row["produit"], quantity, catalog_row["prix_vente"], payload.client.strip() or "Vente comptoir", account["id"], created_at),
            )
            rows.append({"id": int(cursor.lastrowid), "product": catalog_row["produit"], "quantity": quantity, "unitPrice": catalog_row["prix_vente"], "amount": quantity * catalog_row["prix_vente"], "client": payload.client.strip() or "Vente comptoir", "createdAt": created_at})
    return {"sales": rows}


@app.post("/api/expenses", status_code=201)
def create_expense(payload: ExpenseRequest, account: dict[str, Any] = Depends(require_account)) -> dict[str, Any]:
    with connect() as connection:
        cursor = connection.execute(
            """INSERT INTO depenses(etablissement_id, libelle, montant, personne_responsable, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            (account["etablissement_id"], payload.motive.strip(), payload.amount, payload.responsible.strip(), account["id"]),
        )
        return {"id": int(cursor.lastrowid)}


@app.post("/api/credits", status_code=201)
def create_credit(payload: CreditRequest, account: dict[str, Any] = Depends(require_account)) -> dict[str, Any]:
    establishment_id = account["etablissement_id"]
    due_at = payload.dueAt.astimezone(timezone.utc).isoformat()
    created_at = now_utc().isoformat()
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        stock = stock_for_product(connection, establishment_id, payload.product.strip())
        if not stock:
            raise HTTPException(404, "Produit absent du catalogue.")
        if stock["quantity"] < payload.quantity:
            raise HTTPException(409, "Stock insuffisant pour enregistrer ce crédit.")
        unit_price = stock["salePrice"]
        amount = unit_price * payload.quantity
        cursor = connection.execute(
            """INSERT INTO credits(etablissement_id, client, montant, solde, produit, quantite, prix_unitaire,
                   telephone, echeance, observation, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'A payer', ?, ?)""",
            (establishment_id, payload.client.strip(), amount, amount, stock["product"], payload.quantity, unit_price, payload.phone.strip(), due_at, created_at, account["id"]),
        )
        return {"id": int(cursor.lastrowid), "amount": amount, "balance": amount, "dueAt": due_at}


@app.post("/api/credits/{credit_id}/payments", status_code=201)
def pay_credit(credit_id: int, payload: CreditPaymentRequest, account: dict[str, Any] = Depends(require_manager)) -> dict[str, Any]:
    with connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        credit = connection.execute(
            "SELECT id, solde FROM credits WHERE id = ? AND etablissement_id = ?",
            (credit_id, account["etablissement_id"]),
        ).fetchone()
        if not credit:
            raise HTTPException(404, "Crédit introuvable.")
        if payload.amount > credit["solde"]:
            raise HTTPException(409, "Le paiement dépasse le solde restant.")
        balance = credit["solde"] - payload.amount
        status_text = "Paye" if balance == 0 else "Partiellement paye"
        connection.execute("INSERT INTO paiements_credits(credit_id, montant, created_by) VALUES (?, ?, ?)", (credit_id, payload.amount, account["id"]))
        connection.execute("UPDATE credits SET solde = ?, observation = ?, updated_at = ? WHERE id = ?", (balance, status_text, now_utc().isoformat(), credit_id))
        return {"id": credit_id, "balance": balance, "status": status_text}


@app.post("/api/wallet", status_code=201)
def create_wallet_movement(payload: WalletRequest, account: dict[str, Any] = Depends(require_manager)) -> dict[str, Any]:
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO mouvements_portefeuille(etablissement_id, agent, montant, observation, created_by) VALUES (?, ?, ?, ?, ?)",
            (account["etablissement_id"], payload.agent.strip(), payload.amount, payload.observation.strip(), account["id"]),
        )
        return {"id": int(cursor.lastrowid)}


@app.post("/api/backup")
def create_app_backup(account: dict[str, Any] = Depends(require_manager)) -> dict[str, str]:
    backup_path = backup_database.create_backup(backup_database.BACKUP_DIR, keep=30)
    return {"path": str(backup_path), "name": backup_path.name}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/{asset_path:path}", include_in_schema=False)
def static_assets(asset_path: str = "") -> FileResponse:
    if not asset_path:
        asset_path = "index.html"
    asset = STATIC_FILES.get(asset_path)
    if not asset or not asset.is_file():
        raise HTTPException(404, "Fichier introuvable.")
    return FileResponse(asset)
