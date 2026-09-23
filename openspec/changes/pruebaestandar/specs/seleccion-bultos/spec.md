# Spec Delta

## Purpose

Decidir, para cada tienda, qué artículos y cuántas cajas enteras de cada uno componen su medio (1 palet o 2 carros), respetando peso, volumen y densidad y repartiendo las cajas en proporción a las líneas de pedido.

## ADDED Requirements

### Requirement: Nº de días de datos
El cálculo SHALL recibir el nº de días de datos del fichero base como un número entero ≥ 1. Cualquier otro valor (0, negativo, decimal, texto o vacío) MUST rechazarse antes de calcular.

#### Scenario: Días válidos
- **WHEN** el usuario indica 5 días
- **THEN** el cálculo se realiza con 5 días

#### Scenario: Días no válidos
- **WHEN** el usuario indica `0`, `-3`, `2,5` o `abc`
- **THEN** el sistema no calcula y pide un nº entero de días mayor que 0

### Requirement: Artículos elegibles
Para una tienda, un artículo SHALL ser elegible sólo si sus BULTOS en esa tienda son mayores que 0 y tiene peso y volumen válidos. Un artículo no elegible MUST NOT seleccionarse nunca en esa tienda.

#### Scenario: Artículo sin salida
- **WHEN** el artículo 2102526 tiene BULTOS vacío en la tienda 10081
- **THEN** su ELECCIÓN para la tienda 10081 queda vacía

### Requirement: Máximo de cajas por artículo
Para cada artículo elegible en una tienda, el nº de cajas seleccionadas MUST ser un entero entre 1 y ⌈BULTOS / DÍAS⌉ (redondeo al entero superior, calculado sin errores de coma flotante), o bien 0 si no se selecciona.

#### Scenario: División exacta
- **WHEN** un artículo tiene 10 BULTOS y los datos son de 5 días
- **THEN** se pueden seleccionar como máximo 2 cajas

#### Scenario: División con decimales
- **WHEN** un artículo tiene 7 BULTOS y los datos son de 5 días
- **THEN** se pueden seleccionar como máximo 2 cajas (7/5 = 1,4 → 2)

#### Scenario: Pocos bultos en muchos días
- **WHEN** un artículo tiene 1 BULTO y los datos son de 20 días
- **THEN** se puede seleccionar como máximo 1 caja (1/20 = 0,05 → 1)

### Requirement: Capacidad del medio de la tienda
La capacidad de cada tienda SHALL calcularse con su fila de la tabla de tiendas y medios:
- PALET: 1 medio → peso máximo = PESO MAX, volumen máximo = VOLUMEN MÁX.
- CARRO: 2 medios → peso máximo = 2 × PESO MAX, volumen máximo = 2 × VOLUMEN MÁX.

La densidad límite SHALL ser la DENSIDAD de la tabla para ese medio (igual para 1 o 2 medios).

#### Scenario: Tienda con palet
- **WHEN** la tienda usa PALET de 875 kg y 1300 L
- **THEN** su selección puede llegar hasta 875 kg y 1300 L

#### Scenario: Tienda con carro
- **WHEN** la tienda usa CARRO de 475 kg y 600 L
- **THEN** su selección puede llegar hasta 950 kg y 1200 L

### Requirement: Restricciones de peso, volumen y densidad
Para cada tienda, siendo P la suma de (cajas × peso) y V la suma de (cajas × volumen) de los artículos seleccionados:
- P MUST ser ≤ peso máximo de la tienda;
- V MUST ser ≤ volumen máximo de la tienda;
- si V > 0, P / V MUST ser estrictamente menor que la densidad límite del medio.

Estas restricciones MUST cumplirse sin excepción; si no cabe nada, la tienda queda sin selección.

#### Scenario: Selección dentro de límites
- **WHEN** una tienda PALET (875 kg, 1300 L, 0,673 kg/L) recibe una selección de 800 kg y 1290 L
- **THEN** la selección es válida porque 800 ≤ 875, 1290 ≤ 1300 y 800/1290 = 0,620 < 0,673

#### Scenario: Selección demasiado densa
- **WHEN** una selección para un PALET suma 700 kg y 1000 L
- **THEN** es inválida porque 700/1000 = 0,70 no es menor que 0,673, aunque peso y volumen quepan

#### Scenario: Artículo denso compensado
- **WHEN** un artículo de densidad 0,97 kg/L tiene muchas líneas y hay artículos ligeros seleccionados
- **THEN** el artículo denso puede entrar siempre que la densidad del conjunto siga por debajo de la del medio

### Requirement: Reparto de cajas proporcional a las líneas
Para cada tienda, el sistema SHALL asignar las cajas de una en una. En cada paso, entre los artículos elegibles que no han alcanzado su máximo y cuya caja siguiente cabe respetando todas las restricciones, SHALL recibir la caja el de mayor índice LÍNEAS / (cajas ya asignadas + 1). En caso de empate SHALL preferirse, por este orden: el artículo que aún no tiene ninguna caja, el de más líneas, el de menor volumen por caja y el de menor código. El proceso SHALL terminar cuando ninguna caja más quepa o todos los artículos elegibles tengan su máximo.

Como consecuencia observable, a igualdad de máximos y de encaje, un artículo con más líneas MUST recibir al menos tantas cajas como uno con menos líneas.

#### Scenario: Más líneas, más cajas
- **WHEN** en una tienda el artículo A tiene 10 líneas y máximo 5 cajas, el B tiene 4 líneas y máximo 5 cajas, y sólo caben 3 cajas del mismo tamaño
- **THEN** A recibe 2 cajas (índices 10 y 5) y B recibe 1 (índice 4)

#### Scenario: Una caja que no cabe no bloquea al resto
- **WHEN** el siguiente artículo por índice tiene una caja de 30 L y sólo quedan 12 L libres
- **THEN** esa caja se descarta y se asigna la caja del siguiente artículo por índice que quepa en los 12 L

#### Scenario: Todo cabe
- **WHEN** la suma de los máximos de todos los artículos elegibles cabe en el medio cumpliendo peso, volumen y densidad
- **THEN** todos los artículos elegibles se seleccionan con su máximo de cajas

#### Scenario: Tienda sin artículos elegibles
- **WHEN** ninguna fila tiene BULTOS > 0 para una tienda
- **THEN** todas sus celdas ELECCIÓN quedan vacías y el resumen la cuenta como tienda sin selección

### Requirement: Resultado determinista
Con los mismos ficheros y el mismo nº de días, el sistema MUST producir exactamente la misma selección en cada ejecución.

#### Scenario: Dos ejecuciones iguales
- **WHEN** se ejecuta dos veces con los mismos datos y 5 días
- **THEN** las dos salidas tienen idénticos valores en todas las columnas ELECCIÓN
