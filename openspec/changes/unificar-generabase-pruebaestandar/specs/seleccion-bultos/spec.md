## MODIFIED Requirements

### Requirement: Nº de días de datos
El cálculo SHALL recibir el nº de días de datos como un número entero ≥ 1. Ese número no lo escribe el usuario: es el nº de fechas `MVFECI` distintas de las filas PI del Access, según la capacidad `pruebaestandar-integrado`. Si el recuento no da un entero ≥ 1, el sistema MUST rechazar el proceso antes de calcular.

#### Scenario: Días válidos
- **WHEN** el Access tiene filas PI en 5 fechas distintas
- **THEN** el cálculo se realiza con 5 días

#### Scenario: Días no válidos
- **WHEN** el Access no tiene ninguna fila PI con fecha
- **THEN** el sistema no calcula e informa de que no se ha podido contar el nº de días de datos
