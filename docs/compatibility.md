# Compatibility Matrix

The first supported row is exact. A tag without its pinned commit or digest is not an equivalent compatibility claim.

| Component | Supported value | Notes |
| --- | --- | --- |
| Factorio Learning Environment | `v0.4.3` | Pinned to commit `6439e18b7870770454cf91eb36b3d1e6412724f4`. |
| Factorio | `2.0.73` | Base game only; Space Age, Quality, and Elevated Rails are not required. |
| Container image | `docker.io/factoriotools/factorio:2.0.73` | OCI image index digest `sha256:6471fbfb7eab3abf55bb53fed632606ecf17bf930891bccddff724afab9ed94c`. |
| Environment API | classic `gym` as used by FLE `v0.4.3` | The project does not claim Gymnasium compatibility. |
| Python | `3.12.9` | Used for development, tests, adapter, and benchmark tooling. |

The FLE tag and full commit identify the dependency source. The container tag and OCI index digest identify the server image. Platform-specific manifests may have their own digests; those do not replace the pinned index digest in release metadata.

Factorio `2.0.77` is an upgrade candidate only. It is unsupported until the custom-mod integration spike, complete acceptance suite, clean-install package smoke test, and scripted baseline all pass and this matrix is deliberately updated. Do not silently substitute `2.0.77`, `latest`, or another `2.0.x` version.

FLE upgrades follow the same rule: update the tag and full commit together, run project-owned classic-Gym lifecycle and string-tool compatibility tests, and record the verified Factorio image tag and digest. The adapter must not rely on FLE `v0.4.3`'s unconnected mod-mount paths or mutate FLE's runtime prototype enums.
