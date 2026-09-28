# Firmware para TempoTec V3 Blaze

Firmware oficial TempoTec v1.3 (`V3_ANALOG_2025`) con una corrección para los artefactos de audio LDAC en modo Bluetooth Receiver. Versión del proyecto: v1.1.2.

<p align="center"><img src="docs/img/launcher.jpg" alt="Launcher de Full Mod" width="45%"> <img src="docs/img/nowplaying.jpg" alt="Now Playing de Full Mod" width="45%"></p>

[English](README.md) · [Descargas](https://github.com/carmine-bin/tempotec-v3-blaze-mod/releases) · [Instalación](docs/INSTALL.md) · [Recuperación](docs/RECOVERY.md) · [Compilación](docs/BUILD.md)

## Ediciones

| Edición | Contenido | Archivo |
|---|---|---|
| V3 Blaze v1.3 Stock + LDAC Fix | Aspecto y funciones oficiales, con solo la corrección del decoder LDAC | `V3-Blaze-v1.3-Stock-LDAC-Fix.upt` |
| V3 Blaze v1.3 Full Mod | Base v1.3 corregida, interfaz personalizada de estilo HiBy y correcciones de UI probadas | `V3-Blaze-v1.3-Full-Mod-v1.1.2.upt` |

Ambas ediciones usan el kernel oficial e incluyen PEQ, búsqueda Bluetooth en tiempo real y mejoras de estabilidad de v1.3. Stock + LDAC Fix no cambia respecto a la versión anterior. Full Mod v1.1.2 incluye las correcciones de UI probadas en un V3 Blaze real.

Full Mod incluye:

- Launcher y categorías de estilo HiBy, interfaz oscura y Now Playing a pantalla completa.
- Relleno de batería y gráficos de carga corregidos, iconos de ganancia de tres estados, control de brillo y tintado del tema.
- Acceso a Acerca de/desarrollador, colores del tema, caché de imágenes/base de datos en TF y persistencia del ajuste DAC.
- Correcciones existentes de navegación por álbumes, cuenta regresiva de apagado con Power restaurada y gráficos finales de Balance en Quick Settings.
- Cobertura completa del apagado, encabezados coherentes en las páginas del menú de Now Playing, regreso a la pantalla principal al cambiar el color y redibujado correcto de Ajustes al ocultarse la barra de desplazamiento.

El desplegable tiene un control de brillo; sus controles de volumen están ocultos. Los controles de volumen siguen disponibles en otras pantallas. Full Mod también incluye los ajustes comprobados de read-ahead MMC y presión de caché, los cambios de montaje UBIFS y la corrección de metadatos de la pista siguiente descritos en las [notas técnicas](docs/HOW-IT-WORKS.md). Estos ajustes forman parte de Full Mod; su impacto en el rendimiento no se ha medido.

La interfaz se adaptó a través del port de Kae0 para V3 Analog con gráficos de HiBy. Véanse [créditos](CREDITS.md), [changelog](CHANGELOG.md) y [detalles de las correcciones de UI](docs/UI-FIXES.md).

## Limitaciones conocidas

Con el salvapantallas de carátula activo, la información y la carátula pueden tardar aproximadamente 1.5 segundos en actualizarse después de cambiar de canción. El mismo comportamiento fue reproducido en los firmwares oficiales TempoTec v1.2 y v1.3.

La recepción Bluetooth tiene un margen de enlace limitado, especialmente con LDAC sostenido a tasas altas y en condiciones de RF desfavorables. AAC ha sido más estable durante las pruebas. Este comportamiento es independiente de la corrupción de audio LDAC de v1.3 corregida por el proyecto. La causa del poco margen de señal sigue sin determinarse. [Observaciones del enlace](docs/BLUETOOTH-RANGE.md).

El firmware v1.3 contiene una regla adicional downstream que suprime coeficientes y que no se encontró en las fuentes públicas examinadas. Evitar esa regla corrigió la corrupción de audio LDAC en modo Bluetooth Receiver en hardware V3 Blaze real. Su autor y finalidad son desconocidos. [Evidencia del decoder](docs/LDAC-RECEIVER-ARTIFACTS.md).

## Instalación

Solo para TempoTec V3 Blaze (`V3_ANALOG_2025`), no para el V3 Analog antiguo. Flashear tiene riesgos; lee primero las [instrucciones de recuperación](docs/RECOVERY.md).

1. Elige una edición y comprueba su SHA-256 con el [manifiesto v1.1.2](docs/releases/v1.1.2-manifest.json).
2. Renómbrala a `v3_analog_2025.upt` y cópiala a la raíz de una microSD.
3. Selecciona Ajustes → Actualización de firmware → Actualizar mediante microSD. Espera a que termine y reinicie.

Guarda las copias con `.upt.stock` o `.upt.bak`. Un archivo llamado `update.upt` tiene prioridad sobre `v3_analog_2025.upt`, incluso al actualizar desde Ajustes.

Ambos paquetes tienen 44,367,872 bytes.

| Edición | SHA-256 | MD5 |
|---|---|---|
| Stock + LDAC Fix | `273f56607d477d44bd071c1a3e2097361610c2e403cfddc7ccf51b98a56210d1` | `cd380b93df9a600a5d24cb64585aac88` |
| Full Mod | `6bd0c1bf1973241efe6985d6da63572197f502b190851883876d82e8255017e8` | `f85adf2d2f5bc684061f9c27fa6c5d56` |

## Desarrollo y licencia

Las [instrucciones de compilación](docs/BUILD.md) explican cómo generar ambas ediciones y comprobar su contenido. [CONTRIBUTING.md](CONTRIBUTING.md) describe las pruebas en el dispositivo.

El desarrollo y parte del trabajo de ingeniería inversa contó con asistencia de herramientas de IA. Los cambios publicados del firmware fueron revisados y probados en hardware V3 Blaze real.

La licencia MIT cubre las herramientas y documentación originales. El firmware, los gráficos importados y el código LDAC conservan sus respectivos titulares. Véanse [NOTICE.md](NOTICE.md) y [LICENSE](LICENSE). Sin afiliación con TempoTec ni HiBy.
