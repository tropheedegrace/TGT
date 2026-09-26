"""Extraction des champs utiles depuis les messages de l'espace travailleur."""

import re
from typing import Any


ERREUR_ENTREE_INCOMPLETE = "⚠️ Message incomplet, envoi bloqué !"
TABLES_AUTORISEES = {
    "etablissement",
    "stock",
    "entrees",
    "ventes",
    "depenses",
    "credits",
    "portefeuille_agents",
}

_NOMBRE = r"(?:\d{1,3}(?:[ .]\d{3})+|\d+)(?:[,.]\d+)?"
_MESURES = re.compile(
    r"^\s*(?:sacs?|kg|kgs|kilogrammes?|g|grammes?|litres?|l|pieces?|unit[eé]s?)\b\s*(?:de\s+)?",
    re.IGNORECASE,
)
_QUANTITE_ET_PRODUIT = re.compile(
    r"^\s*(?P<quantite>\d+(?:[,.]\d+)?)\s+(?P<description>[^,;]+)",
    re.IGNORECASE,
)
_PRIX_ACHAT = re.compile(
    rf"\bprix\s+d['’]achat\s*[:=]?\s*(?P<montant>{_NOMBRE})\s*(?:FCFA|FC)?\b",
    re.IGNORECASE,
)
_PRIX_VENTE = re.compile(
    rf"\bprix\s+de\s+vente\s*[:=]?\s*(?P<montant>{_NOMBRE})\s*(?:FCFA|FC)?\b",
    re.IGNORECASE,
)


def _convertir_nombre(valeur: str) -> float:
    normalisee = valeur.replace(" ", "")
    if "." in normalisee and "," not in normalisee:
        normalisee = normalisee.replace(".", "")
    elif "," in normalisee and "." not in normalisee:
        normalisee = normalisee.replace(",", "")
    else:
        normalisee = normalisee.replace(".", "").replace(",", "")
    return float(normalisee)


def _convertir_quantite(valeur: str) -> float:
    return float(valeur.replace(",", "."))


def analyser_saisie_texte(texte_brut: str, table_cible: str) -> dict[str, Any]:
    """Analyse un message et refuse toute entree qui ne contient pas les 4 champs.

    La fonction ne touche jamais a la base. Pour une entree, son resultat valide
    peut etre transmis a ``database.inserer_entree``.
    """
    table = table_cible.strip().lower()
    if table not in TABLES_AUTORISEES:
        raise ValueError(f"Table cible inconnue : {table_cible}")
    if not isinstance(texte_brut, str) or not texte_brut.strip():
        if table == "entrees":
            raise ValueError(ERREUR_ENTREE_INCOMPLETE)
        raise ValueError("Le message est vide.")

    resultat: dict[str, Any] = {"table_cible": table, "message": texte_brut.strip()}
    quantite_produit = _QUANTITE_ET_PRODUIT.search(texte_brut)
    if quantite_produit:
        description = _MESURES.sub("", quantite_produit.group("description")).strip()
        resultat["quantite"] = _convertir_quantite(quantite_produit.group("quantite"))
        resultat["produit"] = description.strip(" .:-") or None

    for champ, motif in (
        ("prix_achat", _PRIX_ACHAT),
        ("prix_vente", _PRIX_VENTE),
    ):
        correspondance = motif.search(texte_brut)
        resultat[champ] = (
            _convertir_nombre(correspondance.group("montant"))
            if correspondance
            else None
        )

    if table == "entrees":
        champs_obligatoires = ("produit", "quantite", "prix_achat", "prix_vente")
        if any(not resultat.get(champ) for champ in champs_obligatoires):
            raise ValueError(ERREUR_ENTREE_INCOMPLETE)

    return resultat