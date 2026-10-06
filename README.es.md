# Firmware para TempoTec V3 Blaze

Firmware oficial TempoTec v1.3 (`V3_ANALOG_2025`) con correcciones para los cortes y los artefactos de audio LDAC en modo Bluetooth Receiver. Versión del proyecto: v1.2.1.

<p align="center"><img src="docs/img/blaze-full-mod.jpg" alt="TempoTec V3 Blaze con Full Mod" width="70%"></p>

[English](README.md) · [Descargas](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases) · [Instalación](docs/INSTALL.md) · [Recuperación](docs/RECOVERY.md) · [Compilación](docs/BUILD.md) · [Telegram](https://t.me/V3_Blaze_Discussion)

## Ediciones

| Edición | Contenido | Archivo |
|---|---|---|
| V3 Blaze v1.3 Stock + Fixes | Aspecto y funciones oficiales, con solo las correcciones de Bluetooth Receiver | `V3-Blaze-v1.3-Stock-Fixes-v1.2.0.upt` |
| V3 Blaze v1.3 Full Mod | Base v1.3 corregida, interfaz personalizada de estilo HiBy y correcciones de UI probadas | `V3-Blaze-v1.3-Full-Mod-v1.2.1.upt` |

Ambas ediciones usan el kernel oficial e incluyen PEQ, búsqueda Bluetooth en tiempo real y mejoras de estabilidad de v1.3. Ambas incluyen las mismas dos correcciones de Bluetooth Receiver:

- **Cortes:** BlueZ mantenía la radio escaneando mientras recibía audio, así que el emisor no podía sostener LDAC 990 kb/s ni a corta distancia. Dos líneas de `/etc/bluetooth/main.conf` detienen esos escaneos; 990 kb/s ahora suena sin audio perdido a distancias que antes fallaban. [Detalles y mediciones](docs/BLUETOOTH-RANGE.md).
- **Artefactos LDAC:** una corrección de un byte en el decoder elimina los artefactos digitales introducidos por la v1.3 oficial. [Evidencia del decoder](docs/LDAC-RECEIVER-ARTIFACTS.md).

Stock + LDAC Fix ahora se llama Stock + Fixes. Stock + Fixes no cambia en v1.2.1.

Full Mod incluye todo lo de Stock + Fixes, además de:

**Interfaz**

- Launcher, categorías, interfaz oscura y Now Playing a pantalla completa con estilo HiBy OS.
- Ícono de batería: el relleno ya no desaparece por debajo de ~30 % y no hay batería doble al cargar; por debajo del 16 % el marco se pone rojo y el nivel sigue visible en el color del tema; esquinas del marco nítidas.
- El aviso de batería baja muestra su mensaje en vez de una tarjeta gris vacía.
- Íconos de ganancia con los tres niveles.
- Control de brillo funcional en el desplegable. Sus controles de volumen están ocultos; el volumen sigue disponible en otras pantallas.
- Tintado del color de acento corregido: no tiñe las muestras de color ni los códigos QR.
- Logos e identidad de TempoTec restaurados; elementos de interfaz faltantes restaurados.
- Fondos del launcher, imágenes de play/pausa y textos emergentes corregidos; ícono nativo de Balance en Ajustes rápidos con el estilo moderno.

**Navegación y pantallas**

- Abrir un álbum vuelve a ser rápido: se usa la lista de música oficial de v1.3.
- Cuenta regresiva de apagado al mantener Power, restaurada.
- La pantalla de apagado cubre toda la pantalla al abrirla desde Now Playing.
- Encabezados correctos en las páginas abiertas desde el menú de Now Playing.
- Al cambiar el color del tema vuelve a la pantalla principal en vez de a Música → Canciones.
- Las tarjetas de Ajustes ya no se corrompen cuando desaparece la barra de desplazamiento.
- Now Playing ya no muestra la calidad de audio de la siguiente canción en vez de la actual.

**Ajustes**

- Ajustes → Acerca de (acceso al modo desarrollador y ADB) y Ajustes → Color del tema.
- Caché de imágenes y de base de datos en la microSD.
- El ajuste del DAC se recuerda entre reinicios.

**Sistema**

- Read-ahead de la microSD en 2048 y presión de caché VFS en 50, aplicados solo donde existen las rutas.
- Memoria interna montada con `noatime` en vez de `sync`.

Estos ajustes se describen en las [notas técnicas](docs/HOW-IT-WORKS.md); su impacto en el rendimiento no se ha medido.

**Se conserva de la v1.3 oficial:** PEQ, búsqueda Bluetooth en tiempo real, los arreglos de estabilidad de TempoTec, el kernel oficial y la misma instalación por microSD.

**Limitación conocida:** el ícono de batería del menú desplegable mantiene el marco blanco con batería baja.

La interfaz se adaptó a través del port de Kae0 para V3 Analog con gráficos de HiBy. Véanse [créditos](CREDITS.md), [changelog](CHANGELOG.md) y [detalles de las correcciones de UI](docs/UI-FIXES.md).

## Limitaciones conocidas

Con el salvapantallas de carátula activo, la información y la carátula pueden tardar aproximadamente 1.5 segundos en actualizarse después de cambiar de canción. El mismo comportamiento fue reproducido en los firmwares oficiales TempoTec v1.2 y v1.3.

El Blaze ya no usa Bluetooth LE. No se encontró ninguna función del reproductor que lo necesite; A2DP, AVRCP y HiBy Link usan Bluetooth clásico. A más de unos 12 m con paredes de por medio, LDAC 990 kb/s todavía se corta y el emisor baja la tasa; es el límite físico del enlace. [Detalles de Bluetooth Receiver](docs/BLUETOOTH-RANGE.md).

El firmware v1.3 contiene una regla adicional downstream que suprime coeficientes y que no se encontró en las fuentes públicas examinadas. Evitar esa regla corrigió la corrupción de audio LDAC en modo Bluetooth Receiver en hardware V3 Blaze real. Su autor y finalidad son desconocidos. [Evidencia del decoder](docs/LDAC-RECEIVER-ARTIFACTS.md).

## Instalación

Solo para TempoTec V3 Blaze (`V3_ANALOG_2025`), no para el V3 Analog antiguo. Flashear tiene riesgos; lee primero las [instrucciones de recuperación](docs/RECOVERY.md).

**Un archivo llamado `update.upt` tiene prioridad sobre `v3_analog_2025.upt`, incluso al actualizar desde Ajustes. Elimina o renombra cualquier `update.upt` antes de instalar.**

1. **Si hay un `v3_analog_2025.upt` en la raíz de la microSD (por ejemplo, el que dejó la actualización OTA), renómbralo a `v3_analog_2025.upt.stock` antes de copiar el mod. Si no, el mod lo sobrescribirá y perderás tu copia del firmware oficial.**
2. Elige una edición y comprueba su SHA-256 con el [manifiesto v1.2.1](docs/releases/v1.2.1-manifest.json).
3. Renómbrala a `v3_analog_2025.upt` y cópiala a la raíz de una microSD.
4. Selecciona Ajustes → Actualización de firmware → Actualizar mediante microSD. Espera a que termine y reinicie.

Guarda las copias con `.upt.stock` o `.upt.bak`. Consulta [cómo obtener el firmware oficial v1.3](docs/INSTALL.md#getting-the-official-v13-firmware) y [respaldo y restauración](docs/INSTALL.md#backup-and-restore).

El modo desarrollador y ADB vienen desactivados por defecto en ambas ediciones y funcionan igual que en el firmware oficial: toca About 10 veces para activarlos. En la interfaz oficial y en Stock + Fixes, About está en el menú de inicio. El launcher estilo HiBy de Full Mod no tiene esa entrada, así que Full Mod muestra About en Ajustes (la configuración oficial de Ajustes oculta esa entrada porque el menú de inicio ya la tiene). Este proyecto no activa ADB ni cambia cómo funciona el modo desarrollador.

Ambos paquetes tienen 44,367,872 bytes.

| Edición | SHA-256 | MD5 |
|---|---|---|
| Stock + Fixes | `5ce109414e739546ed19d5cc74ad9b92e5a58f8545d5d3a482f673934a5929af` | `4e9408a7415b66fdad7d0ad560103194` |
| Full Mod | `db91cf52c3ac0f0005d90563bc1fa7f9e3e85abdb2c5ce3fe2e9100c18e6695a` | `d553a52f4fe924e1f663c0e3ac1ff992` |

## Desarrollo y licencia

Las [instrucciones de compilación](docs/BUILD.md) explican cómo generar ambas ediciones y comprobar su contenido. [CONTRIBUTING.md](CONTRIBUTING.md) describe las pruebas en el dispositivo.

Dudas, ayuda y reportes de errores: [grupo de Telegram](https://t.me/V3_Blaze_Discussion). Los errores confirmados y reproducibles van a los [issues de GitHub](https://github.com/carmine-bin/tempotec-v3-blaze-mod/issues) para darles seguimiento.

El desarrollo y parte del trabajo de ingeniería inversa contó con asistencia de herramientas de IA. Los cambios publicados del firmware fueron revisados y probados en hardware V3 Blaze real.

La licencia MIT cubre las herramientas y documentación originales. El firmware, los gráficos importados y el código LDAC conservan sus respectivos titulares. Véanse [NOTICE.md](NOTICE.md) y [LICENSE](LICENSE). Sin afiliación con TempoTec ni HiBy.
