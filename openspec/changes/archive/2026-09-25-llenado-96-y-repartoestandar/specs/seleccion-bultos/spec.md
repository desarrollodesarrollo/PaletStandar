# Spec Delta

## MODIFIED Requirements

### Requirement: Capacidad del medio de la tienda
La capacidad de cada tienda SHALL calcularse con su fila de la tabla de tiendas y medios y un **llenado máximo del 96 %** como margen de seguridad:
- PALET: 1 medio → peso máximo = 96 % × PESO MAX, volumen máximo = 96 % × VOLUMEN MÁX.
- CARRO: 2 medios → peso máximo = 96 % × 2 × PESO MAX, volumen máximo = 96 % × 2 × VOLUMEN MÁX.

El 96 % es fijo y MUST aplicarse tanto al peso como al volumen. La densidad límite SHALL ser la DENSIDAD de la tabla para ese medio (igual para 1 o 2 medios), sin aplicar el 96 %.

#### Scenario: Tienda con palet
- **WHEN** la tienda usa PALET de 875 kg y 1300 L
- **THEN** su selección puede llegar hasta 840 kg y 1248 L

#### Scenario: Tienda con carro
- **WHEN** la tienda usa CARRO de 475 kg y 600 L
- **THEN** su selección puede llegar hasta 912 kg y 1152 L

### Requirement: Restricciones de peso, volumen y densidad
Para cada tienda, siendo P la suma de (cajas × peso) y V la suma de (cajas × volumen) de los artículos seleccionados:
- P MUST ser ≤ peso máximo de la tienda (ya con el 96 % aplicado);
- V MUST ser ≤ volumen máximo de la tienda (ya con el 96 % aplicado);
- si V > 0, P / V MUST ser estrictamente menor que la densidad límite del medio.

Estas restricciones MUST cumplirse sin excepción; si no cabe nada, la tienda queda sin selección.

#### Scenario: Selección dentro de límites
- **WHEN** una tienda PALET (875 kg, 1300 L, 0,673 kg/L) recibe una selección de 800 kg y 1240 L
- **THEN** la selección es válida porque 800 ≤ 840, 1240 ≤ 1248 y 800/1240 = 0,645 < 0,673

#### Scenario: Selección que supera el 96 %
- **WHEN** una tienda PALET (1300 L) recibe una selección de 1290 L que cumple peso y densidad
- **THEN** es inválida porque 1290 L supera el 96 % del volumen (1248 L)

#### Scenario: Selección demasiado densa
- **WHEN** una selección para un PALET suma 700 kg y 1000 L
- **THEN** es inválida porque 700/1000 = 0,70 no es menor que 0,673, aunque peso y volumen quepan

#### Scenario: Artículo denso compensado
- **WHEN** un artículo de densidad 0,97 kg/L tiene muchas líneas y hay artículos ligeros seleccionados
- **THEN** el artículo denso puede entrar siempre que la densidad del conjunto siga por debajo de la del medio
