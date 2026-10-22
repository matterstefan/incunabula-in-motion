# Inventory of Swiss MEI holdings

Run the manually triggered **Inventory Swiss MEI holdings** workflow. It uses the
existing `CERL_USER_AGENT` repository secret and the same concurrency group as the
Zurich harvest. Requests are separated by at least two seconds. Avoid simultaneous
CERL harvests in other repositories, whose concurrency locks are independent.

The query is `data.holdingInstitution.country:CH`, based on the country field in
our retrieved MEI records. Its live index behaviour has not yet been verified.
The workflow first retrieves five records, checks for nonzero hits and verifies
current institution country CH. Full pagination then verifies hit counts and
unique IDs. Unexpected results stop the job rather than produce a misleading list.

Download the `swiss-mei-inventory` artifact:

- `swiss-institutions.csv`: institution IDs/names, MEI record counts, distinct ISTC
  editions, records containing provenance blocks, total blocks and example links.
- `inventory.json`: the same summary with query, retrieval date and scope.
- `swiss-mei-snapshot.json`: complete retrieved records for reuse in later imports.

Counts indicate MEI coverage at retrieval time, not total institutional holdings.
A provenance block does not necessarily provide a usable dated geographical stop.
The query excludes copies held abroad with former Swiss owners. Conversely,
missing or incorrect holding-country codes can omit Swiss institutions; therefore
this is an inventory of records coded CH, not proof of complete Swiss coverage.
No institutions are preselected and Solothurn is not a limiting criterion.

This workflow does not publish new map data, modify the current Zurich map or
commit the raw snapshot. If a run fails it must be restarted; page checkpoints
are not implemented in this small inventory workflow.

Offline validation on the existing Zurich snapshot returns one institution and
1,609 distinct MEI copies. Foreign holdings and duplicate IDs are rejected. Such
an offline sample is explicitly marked incomplete for the national inventory.

## Future catalogue imports

The map should continue to follow a copy of a printed edition. An Alma import may
need bibliographic, holdings and item-level information to identify that copy and
attach its provenance correctly. A bibliographic record ID alone must not be
assumed to identify one physical copy. Preserve source IDs and source scope;
introduce namespaced copy keys for non-MEI records, and explicit crosswalks if a
copy is also represented in MEI. MARC import remains a separate later pilot.
