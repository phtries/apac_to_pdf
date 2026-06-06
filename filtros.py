from typing import List, Dict, Any, Iterable


def filtrar_apacs(
    apacs: List[Dict[str, Any]],
    cnes_executante: str | None = None,
    procedimento_principal: str | None = None,
    procedimentos_principais: Iterable[str] | None = None,
) -> List[Dict[str, Any]]:
    """Filtra APACs por CNES executante e por um ou vários procedimentos principais.

    Mantive o parâmetro procedimento_principal para compatibilidade com versões antigas,
    mas a v4 usa procedimentos_principais para permitir seleção múltipla.
    """
    cnes_executante = (cnes_executante or "").strip()
    procedimento_principal = (procedimento_principal or "").strip()

    procs = {str(p).strip() for p in (procedimentos_principais or []) if str(p).strip()}
    if procedimento_principal:
        procs.add(procedimento_principal)

    filtradas = []
    for apac in apacs:
        if cnes_executante and apac.get("cnes_executante") != cnes_executante:
            continue
        if procs and apac.get("procedimento_principal") not in procs:
            continue
        filtradas.append(apac)
    return filtradas
