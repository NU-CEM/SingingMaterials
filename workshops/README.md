# Workshops

Sonification specs used in public workshops. Each material has its own folder:

| Folder | Material | Data source | Specs |
| --- | --- | --- | --- |
| `CaCO3` | calcite | `mp-3953` | `CaCO3_athermal.yml`, `CaCO3_300.yml` (DOS weighted at 300 K) |
| `diamond` | diamond | `mp-66` | `diamond_concat.yml`, `diamond_super.yml` |
| `graphene` | graphene | `phonopy_graphene.yaml` | `graphene_super.yml` |
| `graphite` | graphite | `mp-48` | `graphite_concat.yml` |
| `quartz` | α-quartz (SiO<sub>2</sub>) | `mp-6930` | `quartz_concat.yml`, `quartz_super.yml` |
| `salt` | rock salt (NaCl) | `mp-22862` | `salt_concat.yml`, `salt_super.yml` |

Specs named `_concat` play several sonifications one after another; specs named `_super` layer them on top of each other.

Run a spec from inside its folder, so that cached DOS data, the phonopy file and the output `.wav` files are found and written there:

```bash
cd workshops/quartz
phonon-sonify-yaml quartz_concat.yml
```
