SANDBOX: diseño, construcción y ejecución segura

Objetivo

Este documento fusiona guía de diseño y ejemplos de ejecución para un sandbox Docker destinado a alojar de forma controlada el núcleo del proyecto (Prometeo). Contiene instrucciones de construcción, ejemplos de ejecución segura y recomendaciones de endurecimiento.

1) Construir la imagen

```bash
docker build -t prometeo-sandbox:latest .
```

2) Ejecución recomendada (aislamiento estricto, sin red)

```bash
docker run --rm -it \
  --read-only \
  --network none \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  -v prometeo-logs:/var/log/prometeo:rw \
  -v $(pwd)/sandbox:/home/aether/sandbox:rw \
  --pids-limit=100 \
  --memory=512m \
  prometeo-sandbox:latest
```

3) Ejecución con red controlada (usar red Docker aislada + firewall del host)

```bash
# crear red aislada
docker network create --internal isolated-net

docker run --rm -it \
  --read-only \
  --network isolated-net \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  -v prometeo-logs:/var/log/prometeo:rw \
  --pids-limit=100 \
  --memory=512m \
  prometeo-sandbox:latest
```

Medidas clave de seguridad (resumen)

- Usuario no-root: el `Dockerfile` crea un usuario `aether` y ejecuta como no-root.
- Sistema de archivos de solo lectura: `--read-only` impide modificaciones del contenedor; monta volúmenes específicos para datos/logs.
- Red deshabilitada por defecto: `--network none`. Si se habilita, hacerlo sólo en redes controladas y con reglas firewall en el host.
- Capacidades reducidas: `--cap-drop ALL` elimina capacidades de Linux.
- `no-new-privileges`: evita escaladas por exec.
- Límites de recursos: `--memory`, `--pids-limit` para mitigar agotamiento.
- Logs inmutables: montar volúmenes de logs gestionados por host o configurar envío a un colector externo.

Notas de endurecimiento para producción

- Considerar runtimes con aislamiento reforzado (gVisor, Kata Containers, Firecracker).
- Usar nombres de usuario mapeados (user namespaces) y UID/GID remapping.
- Provisionar perfiles `seccomp` y AppArmor personalizados que limiten syscalls disponibles.
- Enviar logs a un colector externo inmutable y evitar escritura local cuando sea posible.
- No montar directorios raíz del host ni home users en el contenedor.
- Usar firewall a nivel host (`iptables`/`nftables`) para controlar salidas incluso si el contenedor tiene red.

Buenas prácticas operativas

- Construir la imagen desde CI con versiones fijadas de base y dependencias.
- Firmar y verificar imágenes antes de despliegue (sigstore / Docker Content Trust).
- Ejecutar análisis de vulnerabilidades periódicos en la imagen.
- Separar el supervisor del proceso del contenedor; preferir contenedores efímeros para pruebas.

Ejemplos y variantes de ejecución

- Desarrollo local (sin red, estricto): ver ejemplo en el punto 2.

- Red controlada (aislada internamente): ver ejemplo en el punto 3.

- Notas para CI/reproducibilidad:
  - Fijar versiones base en el `Dockerfile` (por ejemplo `python:3.11.7-slim`) en el pipeline.
  - Usar multistage builds para eliminar herramientas de construcción.
  - Verificar firmas y hashes de artefactos.

Integración de logs y auditoría

- Montar volumen de logs gestionado por host o configurar envío a servidor syslog/collector remoto.
- Asegurar que el contenedor no pueda truncar ni eliminar logs almacenados en el host; usar permisos y procesos de auditoría dedicados.

Limitaciones y advertencias

Esto es una guía inicial para creación de una jaula basada en Docker. Construir un entorno a prueba de fugas requiere un diseño holístico: endurecimiento del host, selección de runtime, configuración del kernel, y supervisión continua. Ponte en contacto con el equipo de seguridad para validar y certificar cualquier despliegue que ejecute código auto-modificable o no confiable.
