# Local execution receipt — 25 November 2026

Native Python standard-library execution in the assistant's local container; no hardware or human participant. Local renderer SHA-256: 6205fe0837bef9301f374e8011d8ad258e593ee803974cb5cbbdd51b87340d1e.

```text
Grid contracts passed for 31 sizes (2..32).
Directed Hamiltonian path counts: {2: 8, 3: 40, 4: 552}
raster 4.0 seconds ae8639b8beaba1cd70cd42ad8e36bb2fd95de22b80cf448f3ded95abd1bbdac2
horizontal 4.0 seconds 29de548a33c45d507bca76a18c71356a8cda8158481701fbe495027b619ff590
vertical 4.0 seconds ef4aa9cf0f71e60ea746e43b70bb5963d5f8cb1a0f992d61ade6ef0796fb7261
two_pass 8.0 seconds df5009ecf8ae45ad43064491906146af7757a928dfd27138c35ef6301d97a6be
```

Assertions compare path edge sets with the exact expressions for 31 grid sizes and check repeated PCM, amplitude bound, headers and payloads. Census directly enumerates paths; counts are not separately proven by an independent implementation. SHA receipts refer to this local render; floating-point library differences across platforms may change sample rounding. No listening test. Full repository suite and exact-head CI not yet verified.
