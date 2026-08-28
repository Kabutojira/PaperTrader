# Quadrant ingest identity-mapping correction

The five imported identities were returned by `watchlist import` in deterministic `security_id`
order, not request order. The completed ingest result associated four names with the wrong IDs when
building the first follow-up requests. The canonical `securities.csv` identities were always
correct, market refresh exposed the mismatch before any research operation was claimed, and no
assessment or trading state was affected.

Correct mapping:

| Security | Correct immutable identity | Venue | Provider symbol | Original queued operation |
| --- | --- | --- | --- | --- |
| MercadoLibre | `security_4935c6e39e38273a1731` | XNAS | `MELI` | `01M14VGSV8RMPCJSXPQN19CSSM` |
| Nomad Foods | `security_98a1943771da875efed5` | XNYS | `NOMD` | `01M14VGVSR1WXDTCCFX51T1NXT` |
| Fiserv | `security_d202772e4e62065cd17a` | XNAS | `FISV` | `01M14VGXR85Z62D6GDJJ9XH8RH` |
| Uber | `security_e4822686f60a96824b6e` | XNYS | `UBER` | `01M14VGZPRSXPKBED8XS85DJ2M` |
| Domino's Pizza | `security_f34181f3df32080a91d1` | XNAS | `DPZ` | `01M14VH1N8WRQBZMJ6BYRG2WWG` |

Four compensating `security_research` causes were merged into the active, still-unclaimed
operations through the queue CLI. Queue merge semantics preserve the original cause, add the
correct identity-specific objective, evidence and research focus, and raise the priority. The
security researcher must follow the canonical security row and the correction cause. Domino's was
already mapped correctly and required no compensating cause.
