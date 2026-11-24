# Respaldo cifrado de las fuentes de Huella

`fuentes.huella.bin` contiene los scripts de construcción y el banco de preguntas en texto plano, cifrados con AES-GCM.
Solo se abre con la clave de contenido (`K`) que está dentro de `huella-admin.html` (archivo privado del administrador).

Para restaurar (Node 18+): `node build/hl/backup.js --restaurar fuentes.huella.bin <K_base64> <carpeta_destino>`
(el script `backup.js` está dentro del propio respaldo; también puede descifrarse con cualquier implementación de AES-GCM:
4 bytes `HLS1`, 12 bytes de IV y el resto es el texto cifrado de un `.tgz`).
