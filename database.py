"""Initialisation et operations SQLite de base pour UzaApp."""

import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = (
    """
    CREATE TABLE IF NOT EXISTS etablissement (
        id INTEGER PRIMARY KEY,
        nom TEXT NOT NULL CHECK (length(trim(nom)) > 0),
        adresse TEXT NOT NULL DEFAULT '',
        telephone TEXT NOT NULL DEFAULT '',
        cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS stock (
        id INTEGER PRIMARY KEY,
        etablissement_id INTEGER NOT NULL,
        produit TEXT NOT NULL CHECK (length(trim(produit)) > 0),
        quantite REAL NOT NULL CHECK (quantite >= 0),
        prix_achat REAL NOT NULL CHECK (prix_achat >= 0),
        prix_vente REAL NOT NULL CHECK (prix_vente >= 0),
        mis_a_jour_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS entrees (
        id INTEGER PRIMARY KEY,
        etablissement_id INTEGER NOT NULL,
        produit TEXT NOT NULL CHECK (length(trim(produit)) > 0),
        quantite REAL NOT NULL CHECK (quantite > 0),
        prix_achat REAL NOT NULL CHECK (prix_achat > 0),
        prix_vente REAL NOT NULL CHECK (prix_vente > 0),
        cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY,
        etablissement_id INTEGER NOT NULL,
        produit TEXT NOT NULL CHECK (length(trim(produit)) > 0),
        quantite REAL NOT NULL CHECK (quantite > 0),
        prix_unitaire REAL NOT NULL CHECK (prix_unitaire >= 0),
        cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS depenses (
        id INTEGER PRIMARY KEY,
        etablissement_id INTEGER NOT NULL,
        libelle TEXT NOT NULL CHECK (length(trim(libelle)) > 0),
        montant REAL NOT NULL CHECK (montant > 0),
        cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS credits (
        id INTEGER PRIMARY KEY,
        etablissement_id INTEGER NOT NULL,
        client TEXT NOT NULL CHECK (length(trim(client)) > 0),
        montant REAL NOT NULL CHECK (montant > 0),
        solde REAL NOT NULL CHECK (solde >= 0 AND solde <= montant),
        cree_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS portefeuille_agents (
        id INTEGER PRIMARY KEY,
        etablissement_id INTEGER NOT NULL,
        agent TEXT NOT NULL CHECK (length(trim(agent)) > 0),
        solde REAL NOT NULL DEFAULT 0 CHECK (solde >= 0),
        mis_a_jour_le TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (etablissement_id) REFERENCES etablissement(id)
            ON UPDATE CASCADE ON DELETE RESTRICT
    )
    """,
)


def ouvrir_connexion(chemin: str | Path = "uzaapp.sqlite3") -> sqlite3.Connection:
    """Ouvre une connexion avec les contraintes de clefs etrangeres actives."""
    connexion = sqlite3.connect(chemin)
    connexion.row_factory = sqlite3.Row
    connexion.execute("PRAGMA foreign_keys = ON")
    return connexion


def creer_tables(connexion: sqlite3.Connection) -> None:
    """Cree les tables de l'application sans remplacer les donnees existantes."""
    with connexion:
        for instruction in SCHEMA:
            connexion.execute(instruction)


def inserer_entree(
    connexion: sqlite3.Connection,
    etablissement_id: int,
    donnees: dict[str, Any],
) -> int:
    """Insere une entree valide avec des parametres SQL, jamais par interpolation."""
    champs = ("produit", "quantite", "prix_achat", "prix_vente")
    if any(donnees.get(champ) is None for champ in champs):
        raise ValueError("⚠️ Message incomplet, envoi bloqué !")

    valeurs = tuple(donnees[champ] for champ in champs)
    if not isinstance(donnees["produit"], str) or not donnees["produit"].strip():
        raise ValueError("⚠️ Message incomplet, envoi bloqué !")
    try:
        if any(float(valeur) <= 0 for valeur in valeurs[1:]):
            raise ValueError("⚠️ Message incomplet, envoi bloqué !")
    except (TypeError, ValueError) as erreur:
        raise ValueError("⚠️ Message incomplet, envoi bloqué !") from erreur

    with connexion:
        curseur = connexion.execute(
            """INSERT INTO entrees
               (etablissement_id, produit, quantite, prix_achat, prix_vente)
               VALUES (?, ?, ?, ?, ?)""",
            (etablissement_id, *valeurs),
        )
    return int(curseur.lastrowid)